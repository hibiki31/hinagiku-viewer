from books.models import BookUserMetaDataModel
from datetime import datetime
from enum import Enum, IntEnum

from typing import List, Optional, Literal, Any
from mixins.schema import BaseSchema


class BookUserMetaDataPatch(BaseSchema):
    uuids: List[str]
    page: Optional[int] = None
    status: Literal['open', 'close', 'pause']


class BookUserDataBase(BaseSchema):
    last_open_date: Optional[datetime] = None
    read_times: Optional[int] = None
    open_page: Optional[int] = None
    rate: Optional[int] = None

class BookBase(BaseSchema):
    uuid: str
    user_id: str
    title: Optional[str] = None
    authors: Any
    publisher: Any
    is_shered: bool
    library_id: int
    genre_id: Optional[str] = None
    tags: Optional[list] = None
    size: int
    page: int
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
    series_no: Optional[int] = None
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

class LibraryPatch(BaseSchema):
    state: LibraryPatchEnum = LibraryPatchEnum.load