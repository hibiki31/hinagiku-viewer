from typing import Optional

from mixins.schema import BaseSchema


class AuthorGet(BaseSchema):
    id: Optional[int] = None
    name: Optional[str] = None
    is_favorite: bool

class BookAuthorPost(BaseSchema):
    author_id: Optional[int] = None
    author_name: Optional[str] = None

class BookAuthorDelete(BaseSchema):
    author_id: int

class PatchAuthor(BaseSchema):
    author_id: int
    is_favorite: bool
