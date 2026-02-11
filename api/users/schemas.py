from typing import Optional

from mixins.schema import BaseSchema


class UserBase(BaseSchema):
    id: Optional[str] = None

class UserGet(UserBase):
    is_admin: bool
