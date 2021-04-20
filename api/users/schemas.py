from fastapi_camelcase import CamelModel
from typing import List, Optional
from pydantic import BaseModel

# RFCでスネークケース指定あるやんけ
class TokenRFC6749Response(BaseModel):
    access_token: str
    token_type: str

class UserBase(CamelModel):
    id: str = None
    class Config:
        orm_mode = True

class UserGet(UserBase):
    is_admin: bool

class UserCurrent(UserGet):
    token:str

class UserPost(UserBase):
    password: str

