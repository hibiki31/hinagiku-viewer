import subprocess
import sys
from time import time, sleep
from sqlalchemy import desc

from mixins.settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.database import SessionLocal

from mixins.convertor import task_library, task_convert, task_export

from books.models import BookModel 


logger = setup_logger(__name__)


def endless_eight():
    logger.info("Worker起動")
    db = SessionLocal()
    while True:
        task_library()

        for request in db.query(BookModel).filter(BookModel.state=="request").all():
            request: BookModel
            logger.info("キャッシュを作成開始: "+request.uuid)
            task_convert(book_uuid=request.uuid)
            
            request.state = "cached"
            logger.info("キャッシュを作成終了: "+request.uuid)
            break
        
        for request in db.query(BookModel).filter(BookModel.state=="export"):
            request: BookModel
            task_export(request)
            break
        
        db.query(BookModel).filter(BookModel.state=="export").delete()

        db.commit()
        
        sleep(0.1)


def one_shot_convert(uuid):
    db = SessionLocal()
    logger.info("単体変換起動")
    task_convert(book_uuid=uuid)



if __name__ == "__main__":
    args = sys.argv

    if len(args) == 1:
        endless_eight()
    elif len(args) == 3:
        if args[2] == "convert":
            one_shot_convert(args[3])    