from fastapi_camelcase import CamelModel



class AuthorGet(CamelModel):
    id: int = None
    name: str = None

class BookAuthorPost(CamelModel):
    author_id: int = None
    author_name: str = None

class BookAuthorDelete(CamelModel):
    author_id: int