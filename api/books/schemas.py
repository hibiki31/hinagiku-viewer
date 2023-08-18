from books.models import BookUserMetaDataModel
from datetime import datetime
from enum import Enum, IntEnum

from typing import List, Optional, Literal, Any
from mixins.schema import BaseSchema


class BookUserMetaDataPatch(BaseSchema):
    uuids: List[str]
    page: int = None
    status: Literal['open', 'close', 'pause']


class BookUserDataBase(BaseSchema):
    last_open_date: datetime = None
    read_times:int = None
    open_page:int = None
    rate: int = None

class BookBase(BaseSchema):
    uuid: str
    user_id: str
    title: str = None
    authors: Any
    publisher: Any
    is_shered: bool
    library_id: int
    genre_id: str = None
    tags: list = None
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
    series_no: int = None
    series: str = None
    author: str = None
    title: str = None
    publisher: str = None
    genre: str = None
    library_id: int = None

class BookUserMetaDataPut(BaseSchema):
    uuids: List[str]
    rate: int = None

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