import subprocess
import sys
from time import time, sleep
from sqlalchemy import desc

from mixins.settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.database import SessionLocal

from mixins.convertor import task_library, task_convert, task_export, export_library, create_book_page_cache

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


if __name__ == "__main__":
    args = sys.argv

    # worker.py convert uuid height
    if len(args) == 4:
        if args[1] == "convert":
            logger.info(f'別プロセスでキャッシュ作成 height:{args[3]} uuid:{args[2]}')
            task_convert(
                book_uuid=args[2], 
                to_height=int(args[3])
            )
            logger.info(f'別プロセスでキャッシュ完了 height:{args[3]} uuid:{args[2]}')
    elif len(args) == 5:
        if args[1] == "page":
            uuid = args[2]
            height = int(args[3])
            page = int(args[4])
            logger.info(f'別プロセスでページキャッシュ作成 height:{height} uuid:{uuid}')
            create_book_page_cache(
                book_uuid=uuid, 
                page=page, 
                to_height=height, 
                quality=85
            )
            logger.info(f'別プロセスでページキャッシュ完了 height:{height} uuid:{uuid}')
    elif len(args) == 2:
        if args[1] == "library":
            db = SessionLocal()
            logger.info(f'別プロセスでライブラリ追加処理開始')
            task_library(db=db)
            logger.info(f'別プロセスでライブラリ追加処理終了')
            logger.info(f'別プロセスでライブラリエクスポート開始')
            export_library(db=db)
            logger.info(f'別プロセスでライブラリエクスポート終了')
    else:
        endless_eight()