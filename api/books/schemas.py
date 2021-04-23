from datetime import datetime

from typing import List, Optional, Literal
from pydantic import BaseModel
from fastapi_camelcase import CamelModel


class BookUserDataBase(CamelModel):
    last_open_date: datetime = None
    read_times:int = None
    open_page:int = None
    rate: int = None

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
    last_open_date: datetime = None
    read_times:int = None
    open_page:int = None
    rate: int = None
    user_data: BookUserDataBase = None
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

class BookUserMetaDataPatch(CamelModel):
    uuids: List[str]
    page: int = None
    status: Literal['open', 'close', 'pause']
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