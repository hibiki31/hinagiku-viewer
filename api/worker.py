import subprocess
import sys
from time import time, sleep
from sqlalchemy import desc

from mixins.settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.database import SessionLocal
from mixins.convertor import task_convert, task_export, export_library, create_book_page_cache

from tasks.library_import import main as task_library_import
from tasks.library_export import main as task_library_export

from books.models import BookModel 


logger = setup_logger(__name__)


def endless_eight():
    logger.info("Worker起動")
    db = SessionLocal()
    while True:
        task_library_import()

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
    if len(args) == 1:
        endless_eight()

    if args[1] == "convert":
        book_uuid = args[2]
        height = int(args[3])
        logger.info(f'ワーカーが全ページキャッシュ作成 height:{args[3]} uuid:{args[2]}')
        task_convert(
            book_uuid=book_uuid, 
            to_height=height
        )
        logger.info(f'別プロセスでキャッシュ完了 height:{args[3]} uuid:{args[2]}')
    
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

    if args[1] == "export":
        db = SessionLocal()
        logger.info(f'別プロセスでライブラリエクスポート開始')
        task_library_export(db=db, export_uuid=False)
        logger.info(f'別プロセスでライブラリエクスポート終了')
    
    if args[1] == "export_uuid":
        print("aaaaaaaaaaaaaaaa")
        db = SessionLocal()
        logger.info(f'別プロセスでライブラリエクスポート開始')
        task_library_export(db=db, export_uuid=True)
        logger.info(f'別プロセスでライブラリエクスポート終了')

    if args[1] == "load":
        user_id = args[2]
        db = SessionLocal()
        logger.info(f'別プロセスでライブラリ追加処理開始')
        task_library_import(db=db, user_id=user_id)
        logger.info(f'別プロセスでライブラリ追加処理終了')