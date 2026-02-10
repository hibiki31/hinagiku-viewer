from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from mixins.database import Base


class SystemSettingsModel(Base):
    """
    システム設定テーブル（Key-Value型）
    
    動的に設定を追加・変更可能な汎用設定ストレージ。
    マイグレーション不要で新規設定項目を追加できる。
    """
    __tablename__ = 'system_settings'

    key = Column(String(255), primary_key=True, comment='設定キー')
    value = Column(String(1000), nullable=False, comment='設定値（文字列として保存）')
    data_type = Column(String(50), nullable=False, comment='データ型: int, float, bool, string, json')
    description = Column(String(500), nullable=True, comment='設定の説明')
    category = Column(String(100), nullable=True, comment='カテゴリ: system, security, task, thumbnail等')
    is_public = Column(Boolean, nullable=False, default=False, comment='非管理者も取得可能か')
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='更新日時')
    updated_by = Column(String, ForeignKey('users.id', onupdate='CASCADE', ondelete='SET NULL'), nullable=True, comment='更新者')
