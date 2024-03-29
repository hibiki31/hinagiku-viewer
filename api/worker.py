import subprocess
import sys
from time import time, sleep
from sqlalchemy import desc

from settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.database import SessionLocal
from mixins.convertor import create_book_page_cache

from tasks.library_import import main as task_library_import
from tasks.library_export import main as task_library_export
from tasks.library_fixmetadata import main as task_library_fixmetadata
from tasks.media_cache import main as task_media_cache
from tasks.library_sim import main as task_library_sim
from tasks.library_rule import main as task_library_rule

from books.models import BookModel 


logger = setup_logger(__name__)


if __name__ == "__main__":
    args = sys.argv
    db = SessionLocal()

    if args[1] == "convert":
        book_uuid = args[2]
        height = int(args[3])
        logger.info(f'別プロセスで全ページキャッシュ作成 height:{args[3]} uuid:{args[2]}')
        task_media_cache(
            db=db,
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
        logger.info(f'別プロセスでライブラリエクスポート開始')
        task_library_export(db=db, export_uuid=False)
        logger.info(f'別プロセスでライブラリエクスポート終了')
    
    if args[1] == "export_uuid":
        logger.info(f'別プロセスでライブラリエクスポート開始')
        task_library_export(db=db, export_uuid=True)
        logger.info(f'別プロセスでライブラリエクスポート終了')

    if args[1] == "load":
        user_id = args[2]
        logger.info(f'別プロセスでライブラリ追加処理開始')
        task_library_import(db=db, user_id=user_id)
        logger.info(f'別プロセスでライブラリ追加処理終了')
    
    if args[1] == "fixmetadata":
        user_id = args[2]
        logger.info(f'別プロセスでメタデータ更新開始')
        task_library_fixmetadata(db=db, user_id=user_id)
        logger.info(f'別プロセスでメタデータ更新完了')
    
    if args[1] == "sim":
        mode = args[2]
        logger.info(f'ワーカで重複検索開始')
        task_library_sim(
            db=db,
            mode = mode
        )
        logger.info(f'ワーカで重複検索完了')
        
    if args[1] == "rule":
        uuid = args[2] if len(args) == 3 else None
        logger.info(f'ワーカでrule適応開始')
        task_library_rule(
            db=db,
            uuid=uuid
        )
        logger.info(f'ワーカでrule適応完了')