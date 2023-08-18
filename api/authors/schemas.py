from mixins.schema import BaseSchema



class AuthorGet(BaseSchema):
    id: int = None
    name: str = None

class BookAuthorPost(BaseSchema):
    author_id: int = None
    author_name: str = None

class BookAuthorDelete(BaseSchema):
    author_id: int