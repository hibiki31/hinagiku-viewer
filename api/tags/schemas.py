from typing import List

from mixins.schema import BaseSchema


class BookTagBase(BaseSchema):
    uuids: List[str]
    name: str
