from datetime import datetime
from typing import Optional

from mixins.schema import BaseSchema


class TaskSchema(BaseSchema):
    """タスク詳細スキーマ"""
    id: str
    task_type: str
    status: str
    progress: int
    current_item: int
    total_items: Optional[int] = None
    current_step: Optional[str] = None
    message: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_id: Optional[str] = None


class TaskListResponse(BaseSchema):
    """タスク一覧レスポンス"""
    count: int
    limit: int
    offset: int
    rows: list[TaskSchema]


class TaskCreateResponse(BaseSchema):
    """タスク作成レスポンス"""
    status: str
    task_id: str
