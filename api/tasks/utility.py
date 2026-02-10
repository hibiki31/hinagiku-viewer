import datetime
from typing import Optional

from sqlalchemy.orm import Session

from mixins.log import setup_logger
from tasks.models import TaskModel

logger = setup_logger(__name__)


def update_task_status(
    db: Session,
    task_id: str,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    current_item: Optional[int] = None,
    total_items: Optional[int] = None,
    current_step: Optional[str] = None,
    message: Optional[str] = None,
    error_message: Optional[str] = None
) -> None:
    """
    タスクのステータスを更新する
    
    Args:
        db: データベースセッション
        task_id: タスクID
        status: ステータス (pending, running, completed, failed, cancelled)
        progress: 進捗率 0-100
        current_item: 処理済み件数
        total_items: 全体件数
        current_step: 現在のステップ
        message: メッセージ
        error_message: エラーメッセージ
    """
    if not task_id:
        return

    task = db.query(TaskModel).filter(TaskModel.id == task_id).one_or_none()
    if not task:
        logger.warning(f"タスクが見つかりません: {task_id}")
        return

    # ステータス更新
    if status:
        task.status = status
        if status == "running" and not task.started_at:
            task.started_at = datetime.datetime.now()
        elif status in ["completed", "failed", "cancelled"]:
            if not task.completed_at:
                task.completed_at = datetime.datetime.now()

    # 進捗情報更新
    if progress is not None:
        task.progress = min(100, max(0, progress))  # 0-100に制限
    if current_item is not None:
        task.current_item = current_item
    if total_items is not None:
        task.total_items = total_items
    if current_step:
        task.current_step = current_step
    if message:
        task.message = message
    if error_message:
        task.error_message = error_message

    try:
        db.commit()
    except Exception as e:
        logger.error(f"タスクステータス更新エラー: {e}", exc_info=True)
        db.rollback()


def create_task(
    db: Session,
    task_id: str,
    task_type: str,
    user_id: Optional[str] = None
) -> TaskModel:
    """
    新規タスクを作成する
    
    Args:
        db: データベースセッション
        task_id: タスクID (UUID)
        task_type: タスク種別
        user_id: 実行ユーザーID
    
    Returns:
        作成されたTaskModel
    """
    task = TaskModel(
        id=task_id,
        task_type=task_type,
        status="pending",
        user_id=user_id
    )
    db.add(task)
    db.commit()
    logger.info(f"タスク作成: {task_id} (type={task_type}, user={user_id})")
    return task
