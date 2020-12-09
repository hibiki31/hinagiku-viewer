from datetime import datetime

from typing import List, Optional
from pydantic import BaseModel
from fastapi_camelcase import CamelModel


class BookBase(CamelModel):
    uuid: str
    title: str = None
    author: str = None
    size: int = None
    page: int = None
    add_date: datetime = None
    file_date: datetime = None
    import_file_name: str
    state: str = None
    rate: int = None
    genre: str = None
    library: str = None
    class Config:
        orm_mode  =  True
    

class BookPut(CamelModel):
    uuids: List[str]
    state: str = None
    rate: int = None
    series_no: int = None
    series: str = None
    author: str = None
    title: str = None
    genre: str = None
    library: str = None
    class Config:
        orm_mode  =  True