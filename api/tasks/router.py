import subprocess
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mixins.database import get_db
from mixins.log import setup_logger
from settings import APP_ROOT
from tasks.models import TaskModel
from tasks.schemas import TaskCreate, TaskCreateResponse, TaskListResponse, TaskSchema
from tasks.utility import create_task
from users.router import get_current_user
from users.schemas import UserCurrent

app = APIRouter(
    prefix="/api",
    tags=["Task"]
)
logger = setup_logger(__name__)

# バックグラウンドタスク実行中のプロセスを管理
task_pool = []


@app.post("/tasks", response_model=TaskCreateResponse, summary="タスク開始")
async def create_background_task(
    model: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserCurrent = Depends(get_current_user)
):
    """
    各種バックグラウンドタスクを開始する

    task_type:
    - load: ライブラリのロード
    - fixmetadata: メタデータの修正
    - export: ライブラリのエクスポート
    - export_uuid: UUID指定エクスポート
    - sim_all: 全体の類似度計算
    - rule: ルール適用
    - thumbnail_recreate: サムネイル再作成
    - integrity_check: 整合性チェック
    """
    # 既に実行中のタスクがあるかチェック（完了したプロセスを削除）
    for i in range(len(task_pool) - 1, -1, -1):
        if task_pool[i].poll() is not None:
            logger.debug(f"完了したプロセスをプールから削除 {task_pool[i].args}")
            del task_pool[i]

    # 実行中のタスクがある場合はエラー
    for process in task_pool:
        if process.poll() is None:
            logger.warning(f"既に実行中のタスクがあります: {process.args}")
            return {"status": "already_running", "task_id": ""}

    # タスクレコード作成
    task_id = str(uuid4())
    create_task(db=db, task_id=task_id, task_type=model.task_type, user_id=current_user.id)

    # タスクタイプに応じてワーカープロセスを起動
    if model.task_type == "load":
        task_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "load", current_user.id, task_id]))
    elif model.task_type == "fixmetadata":
        task_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "fixmetadata", current_user.id, task_id]))
    elif model.task_type == "export":
        task_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "export", task_id]))
    elif model.task_type == "export_uuid":
        task_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "export_uuid", task_id]))
    elif model.task_type == "sim_all":
        task_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "sim", "all", task_id]))
    elif model.task_type == "rule":
        task_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "rule", task_id]))
    elif model.task_type == "thumbnail_recreate":
        task_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "thumbnail_recreate", task_id]))
    elif model.task_type == "integrity_check":
        task_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "integrity_check", task_id]))

    logger.info(f"タスク開始: {model.task_type} (task_id: {task_id}) by {current_user.id}")

    return {"status": "ok", "task_id": task_id}


@app.get("/tasks", response_model=TaskListResponse, summary="タスク一覧取得")
async def list_tasks(
    db: Session = Depends(get_db),
    current_user: UserCurrent = Depends(get_current_user),
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    タスク一覧を取得する

    Args:
        status: ステータスフィルタ (pending, running, completed, failed)
        task_type: タスク種別フィルタ (load, sim_all, export等)
        limit: 取得件数
        offset: オフセット
    """
    query = db.query(TaskModel)

    # 管理者以外は自分のタスクのみ表示
    if not current_user.is_admin:
        query = query.filter(TaskModel.user_id == current_user.id)

    # フィルタ
    if status:
        query = query.filter(TaskModel.status == status)
    if task_type:
        query = query.filter(TaskModel.task_type == task_type)

    # カウント
    count = query.count()

    # ソート・ページング
    query = query.order_by(TaskModel.created_at.desc())
    query = query.limit(limit).offset(offset)

    rows = query.all()

    return {
        "count": count,
        "limit": limit,
        "offset": offset,
        "rows": rows
    }


@app.get("/tasks/{task_id}", response_model=TaskSchema, summary="タスク詳細取得")
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: UserCurrent = Depends(get_current_user)
):
    """
    タスクの詳細情報を取得する

    Args:
        task_id: タスクID
    """
    task = db.query(TaskModel).filter(TaskModel.id == task_id).one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")

    # 管理者以外は自分のタスクのみ表示
    if not current_user.is_admin and task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="このタスクにアクセスする権限がありません")

    return task


@app.delete("/tasks/{task_id}", summary="タスクキャンセル（未実装）")
async def cancel_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: UserCurrent = Depends(get_current_user)
):
    """
    タスクをキャンセルする（将来実装予定）

    現在はステータスをcancelledに変更するのみで、
    実際のプロセス停止は未実装。
    """
    task = db.query(TaskModel).filter(TaskModel.id == task_id).one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="タスクが見つかりません")

    # 管理者以外は自分のタスクのみ操作可能
    if not current_user.is_admin and task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="このタスクにアクセスする権限がありません")

    # 実行中のタスクのみキャンセル可能
    if task.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="このタスクはキャンセルできません")

    task.status = "cancelled"
    db.commit()

    logger.info(f"タスクキャンセル: {task_id} by {current_user.id}")

    return {"status": "cancelled", "taskId": task_id}
