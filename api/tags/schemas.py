from typing import List
from fastapi_camelcase import CamelModel


class BookTagBase(CamelModel):
    uuids: List[str]
    name: str