from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from pydantic import Field

from mixins.schema import BaseSchema


class GetLibrary(BaseSchema):
    count: int
    name: str
    id: int
    user_id: str


class BookUserMetaDataPatch(BaseSchema):
    uuids: List[str]
    page: Optional[int] = None
    status: Literal['open', 'close', 'pause']


class BookUserDataBase(BaseSchema):
    last_open_date: datetime | None = None
    read_times: int | None = None
    open_page: int | None = None
    rate: int | None = None


class BookAuthors(BaseSchema):
    id: int
    name: str
    description: str | None = None
    is_favorite: bool = False


class BookTag(BaseSchema):
    id: int
    name: str


class BookPublisher(BaseSchema):
    name: str | None = ""
    id: int | None = None


class BookBase(BaseSchema):
    uuid: str
    user_id: str
    title: str | None = None
    authors: List[BookAuthors]
    publisher: BookPublisher
    # データベースのタイポをPython側では正しく扱う（OpenAPIではタイポを維持）
    is_shared: bool = Field(..., alias="isShered")
    cached: bool = Field(..., alias="chached")
    library_id: int
    genre_id: str | None = None
    tags: List[BookTag]
    size: int
    page: int
    sha1: str
    import_file_name: str
    add_date: datetime
    file_date: datetime
    user_data: BookUserDataBase


class BookGet(BaseSchema):
    limit: int
    offset: int
    count: int
    rows: List[BookBase]


class BookPut(BaseSchema):
    uuids: List[str]
    # series_number -> seriesNo (numberではなくno)
    series_number: Optional[int] = Field(default=None, alias="seriesNo")
    series: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    publisher: Optional[str] = None
    genre: Optional[str] = None
    library_id: Optional[int] = None

class BookUserMetaDataPut(BaseSchema):
    uuids: List[str]
    rate: Optional[int] = None

class BookTagBase(BaseSchema):
    uuids: List[str]
    name: str

class BookCacheCreate(BaseSchema):
    uuid: str
    height: int

class LibraryPatchEnum(str, Enum):
    export = "export"
    load = "load"
    export_uuid = "export_uuid"
    fixmetadata = "fixmetadata"
    sim_all = "sim_all"
    rule = "rule"

class LibraryPatch(BaseSchema):
    state: LibraryPatchEnum = LibraryPatchEnum.load


class BookSearchParams(BaseSchema):
    """書籍検索用クエリパラメータ

    snake_caseで定義することでPython側の命名規則に従い、
    BaseSchemaのalias_generator=to_camelにより自動的にCamelCaseでAPIに公開される。

    例:
        - file_name_like (Python) -> fileNameLike (API)
        - author_like (Python) -> authorLike (API)
        - author_is_favorite (Python) -> authorIsFavorite (API)
    """
    uuid: Optional[str] = None
    file_name_like: Optional[str] = None
    cached: Optional[bool] = None
    author_like: Optional[str] = None
    author_is_favorite: Optional[bool] = None
    title_like: Optional[str] = None
    full_text: Optional[str] = None
    rate: Optional[int] = None
    series_id: Optional[str] = None
    genre_id: Optional[str] = None
    library_id: int = 1
    tag: Optional[str] = None
    state: Optional[str] = None
    limit: int = 50
    offset: int = 0
    sort_key: str = "authors"
    sort_desc: bool = False
