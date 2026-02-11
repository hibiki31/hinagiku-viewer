from mixins.schema import BaseSchema


class AuthorSearchParams(BaseSchema):
    """著者検索パラメータ"""
    name: str | None = None
    name_like: str | None = None
    is_favorite: bool | None = None


class AuthorGet(BaseSchema):
    """著者取得レスポンス"""
    id: int
    name: str
    is_favorite: bool = False
    book_count: int | None = None
    description: str | None = None


class AuthorDetail(BaseSchema):
    """著者詳細レスポンス"""
    id: int
    name: str
    is_favorite: bool
    description: str | None
    book_count: int


class BookAuthorPost(BaseSchema):
    """書籍への著者追加リクエスト"""
    author_id: int | None = None
    author_name: str | None = None


class BookAuthorDelete(BaseSchema):
    """書籍から著者削除リクエスト"""
    author_id: int


class AuthorUpdate(BaseSchema):
    """著者更新リクエスト"""
    name: str | None = None
    is_favorite: bool | None = None
    description: str | None = None


# 後方互換性のため残す（Deprecated）
class PatchAuthor(BaseSchema):
    """著者更新リクエスト（旧形式・非推奨）"""
    author_id: int
    is_favorite: bool


class BookAuthorResponse(BaseSchema):
    """書籍著者追加レスポンス"""
    message: str
    book_uuid: str
    author_id: int
