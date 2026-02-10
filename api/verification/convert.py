import zipfile

from books.models import BookModel
from mixins.convertor import task_convert
from mixins.database import SessionLocal
from settings import DATA_ROOT
from users.models import UserModel
from verification.common import DebugTimer


def debug():
    db = SessionLocal()
    for book in db.query(BookModel).all():
        timer = DebugTimer()
        task_convert(book_uuid=book.uuid, to_height=1000)
        timer.rap("終了")
