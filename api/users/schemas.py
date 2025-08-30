from mixins.schema import BaseSchema
from pydantic import BaseModel


# RFCでスネークケース指定あるやんけ
class TokenRFC6749Response(BaseModel):
    access_token: str
    token_type: str

class AuthValidateResponse(TokenRFC6749Response):
    username: str

class UserBase(BaseSchema):
    id: str = None

class UserGet(UserBase):
    is_admin: bool

class UserCurrent(UserGet):
    token:str

class UserPost(UserBase):
    password: str