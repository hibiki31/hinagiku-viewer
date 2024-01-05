from mixins.schema import BaseSchema



class AuthorGet(BaseSchema):
    id: int = None
    name: str = None
    is_favorite: bool

class BookAuthorPost(BaseSchema):
    author_id: int = None
    author_name: str = None

class BookAuthorDelete(BaseSchema):
    author_id: int
    
class PatchAuthor(BaseSchema):
    author_id: int
    is_favorite: bool