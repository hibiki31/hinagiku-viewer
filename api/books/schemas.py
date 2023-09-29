from books.models import BookUserMetaDataModel
from datetime import datetime
from enum import Enum, IntEnum

from typing import List, Optional, Literal, Any
from mixins.schema import BaseSchema


class GetLibrary(BaseSchema):
    count: int
    name: str
    id: int
    user_id: str


class BookUserMetaDataPatch(BaseSchema):
    uuids: List[str]
    page: int = None
    status: Literal['open', 'close', 'pause']


class BookUserDataBase(BaseSchema):
    last_open_date: datetime | None = None
    read_times:int | None = None
    open_page:int | None = None
    rate: int | None = None


class BookAuthors(BaseSchema):
    id: int
    name: str
    description: str | None = None
    

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
    is_shered: bool
    chached: bool
    library_id: int
    genre_id: str | None = None
    tags: List[BookTag]
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
    sim_all = "sim_all"

class LibraryPatch(BaseSchema):
    state: LibraryPatchEnum = LibraryPatchEnum.load