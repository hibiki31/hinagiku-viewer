from mixins.schema import BaseSchema


class TagCreate(BaseSchema):
    """タグ作成スキーマ"""
    name: str


class TagResponse(BaseSchema):
    """タグレスポンス"""
    id: int
    name: str
