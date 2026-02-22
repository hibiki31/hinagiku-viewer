from datetime import datetime
from typing import Any

from mixins.schema import BaseSchema


class SystemSettingSchema(BaseSchema):
    """システム設定項目"""
    key: str
    value: str
    data_type: str  # "int" | "float" | "bool" | "string" | "json"
    description: str | None = None
    category: str | None = None
    is_public: bool = False
    updated_at: datetime
    updated_by: str | None = None


class SystemSettingValueSchema(BaseSchema):
    """設定値のみ（更新用）"""
    value: str


class SystemSettingCreateSchema(BaseSchema):
    """設定作成用"""
    key: str
    value: str
    data_type: str = "string"
    description: str | None = None
    category: str | None = None
    is_public: bool = False


class SystemSettingBulkUpdateSchema(BaseSchema):
    """一括更新用"""
    settings: dict[str, str]  # { "key": "value", ... }


class SystemSettingsListResponse(BaseSchema):
    """設定一覧レスポンス"""
    settings: list[SystemSettingSchema]
    total: int


class SystemSettingDeleteResponse(BaseSchema):
    """設定削除レスポンス"""
    message: str
    key: str


class SystemSettingBulkUpdateResponse(BaseSchema):
    """設定一括更新レスポンス"""
    message: str
    updated: int
    errors: list[dict[str, str]]


class SystemSettingsCategoryResponse(BaseSchema):
    """カテゴリ別設定取得レスポンス（型変換済み）"""
    settings: dict[str, Any]
