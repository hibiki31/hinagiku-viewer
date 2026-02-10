from mixins.schema import BaseSchema


class TagCreate(BaseSchema):
    """タグ作成スキーマ"""
    name: str
