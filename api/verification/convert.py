import zipfile
from verification.common import DebugTimer
from settings import DATA_ROOT
from mixins.database import SessionLocal
from mixins.convertor import task_convert
from books.models import BookModel
from users.models import UserModel

def debug():
    db = SessionLocal()
    for book in db.query(BookModel).all():
        timer = DebugTimer()
        task_convert(book_uuid=book.uuid, to_height=1000)
        timer.rap("終了")