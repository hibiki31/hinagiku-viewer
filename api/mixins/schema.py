from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """全体共通の情報をセットするBaseSchema"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )


class MessageResponse(BaseSchema):
    """汎用メッセージレスポンス"""
    message: str


class StatusResponse(BaseSchema):
    """汎用ステータスレスポンス"""
    status: str
