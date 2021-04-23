from datetime import datetime

from typing import List, Optional
from pydantic import BaseModel
from fastapi_camelcase import CamelModel


class BookBase(CamelModel):
    uuid: str
    user_id: str
    title: str = None
    author: str = None
    publisher: str = None
    is_shered: bool
    library: str
    genre: str = None
    tags: list = None
    size: int
    page: int
    import_file_name: str
    add_date: datetime
    file_date: datetime
    user_last_open_date: datetime = None
    user_read_times:int = None
    user_open_page:int = None
    user_rate: int = None
    class Config:
        orm_mode  =  True


class BookGet(CamelModel):
    limit: int
    offset: int
    count: int
    rows: List[BookBase]
    

class BookPut(CamelModel):
    uuids: List[str]
    state: str = None
    rate: int = None
    series_no: int = None
    series: str = None
    author: str = None
    title: str = None
    publisher: str = None
    genre: str = None
    library: str = None
    class Config:
        orm_mode  =  True

class BookUserMetaDataPut(CamelModel):
    uuids: List[str]
    rate: int = None
    class Config:
        orm_mode  =  True

class BookTagBase(CamelModel):
    uuids: List[str]
    name: str

class BookCacheCreate(CamelModel):
    uuid: str
    height: int

class LibraryPatch(CamelModel):
    state: str