from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from mixins.database import get_db
from mixins.log import setup_logger
from tasks.models import TaskModel
from tasks.schemas import TaskListResponse, TaskSchema
from users.router import get_current_user
from users.schemas import UserCurrent

app = APIRouter()
logger = setup_logger(__name__)


@app.get("/api/tasks", tags=["Task"], response_model=TaskListResponse, summary="タスク一覧取得")
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


@app.get("/api/tasks/{task_id}", tags=["Task"], response_model=TaskSchema, summary="タスク詳細取得")
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


@app.delete("/api/tasks/{task_id}", tags=["Task"], summary="タスクキャンセル（未実装）")
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
