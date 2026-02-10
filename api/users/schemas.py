from typing import Optional

from pydantic import BaseModel, ConfigDict

from mixins.schema import BaseSchema


# RFCでスネークケース指定があるため、こちらは変換しない
class TokenRFC6749Response(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    access_token: str
    token_type: str

class AuthValidateResponse(TokenRFC6749Response):
    username: str
    is_admin: bool

class UserBase(BaseSchema):
    id: Optional[str] = None

class UserGet(UserBase):
    is_admin: bool

class UserCurrent(UserGet):
    token: str

class UserPost(UserBase):
    password: str
