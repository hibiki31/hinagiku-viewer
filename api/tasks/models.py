from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.sql import func

from mixins.database import Base


class TaskModel(Base):
    """
    バックグラウンドタスク管理テーブル
    
    長時間実行されるタスク（ライブラリ追加、重複検索など）の
    ステータスと進捗を管理する。
    """
    __tablename__ = 'tasks'

    # 基本情報
    id = Column(String, primary_key=True, comment='タスクID（UUID）')
    task_type = Column(String(50), nullable=False, index=True, comment='タスク種別: load, sim_all, export等')
    status = Column(String(20), nullable=False, index=True, default='pending', comment='ステータス: pending, running, completed, failed, cancelled')

    # 進捗情報
    progress = Column(Integer, default=0, comment='進捗率 0-100')
    current_item = Column(Integer, default=0, comment='処理済み件数')
    total_items = Column(Integer, nullable=True, comment='全体件数')
    current_step = Column(String(200), nullable=True, comment='現在のステップ: 初期化中、ハッシュ計算中等')

    # メッセージ
    message = Column(String(500), nullable=True, comment='現在の処理内容メッセージ')
    error_message = Column(String(1000), nullable=True, comment='エラー詳細メッセージ')

    # タイムスタンプ
    created_at = Column(DateTime, nullable=False, server_default=func.now(), comment='作成日時')
    started_at = Column(DateTime, nullable=True, comment='開始日時')
    completed_at = Column(DateTime, nullable=True, comment='完了日時')

    # ユーザー情報
    user_id = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), nullable=True, comment='実行ユーザー')

    # インデックス
    __table_args__ = (
        Index('idx_tasks_status_created', 'status', 'created_at'),
        Index('idx_tasks_user_status', 'user_id', 'status'),
    )
