import sys

from mixins.convertor import create_book_page_cache
from mixins.database import SessionLocal
from mixins.log import setup_logger
from tasks.library_export import main as task_library_export
from tasks.library_fixmetadata import main as task_library_fixmetadata
from tasks.library_import import main as task_library_import
from tasks.library_integrity_check import main as task_library_integrity_check
from tasks.library_rule import main as task_library_rule
from tasks.library_sim import main as task_library_sim
from tasks.library_sim_lsh import main as task_library_sim_lsh
from tasks.media_cache import main as task_media_cache
from tasks.thumbnail_recreate import main as task_thumbnail_recreate

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
        task_id = args[2] if len(args) > 2 else None
        logger.info(f'別プロセスでライブラリエクスポート開始 (task_id={task_id})')
        task_library_export(db=db, export_uuid=False, task_id=task_id)
        logger.info('別プロセスでライブラリエクスポート終了')

    if args[1] == "export_uuid":
        task_id = args[2] if len(args) > 2 else None
        logger.info(f'別プロセスでライブラリエクスポート開始 (task_id={task_id})')
        task_library_export(db=db, export_uuid=True, task_id=task_id)
        logger.info('別プロセスでライブラリエクスポート終了')

    if args[1] == "load":
        user_id = args[2]
        task_id = args[3] if len(args) > 3 else None
        logger.info(f'別プロセスでライブラリ追加処理開始 (task_id={task_id})')
        task_library_import(db=db, user_id=user_id, task_id=task_id)
        logger.info('別プロセスでライブラリ追加処理終了')

    if args[1] == "fixmetadata":
        user_id = args[2]
        task_id = args[3] if len(args) > 3 else None
        logger.info(f'別プロセスでメタデータ更新開始 (task_id={task_id})')
        task_library_fixmetadata(db=db, user_id=user_id, task_id=task_id)
        logger.info('別プロセスでメタデータ更新完了')

    if args[1] == "sim":
        mode = args[2]
        task_id = args[3] if len(args) > 3 else None
        # 旧アルゴリズム使用（sim_old指定時）
        if mode == "old":
            logger.info(f'ワーカで重複検索開始（旧アルゴリズム） (task_id={task_id})')
            task_library_sim(db=db, mode="all", task_id=task_id)
            logger.info('ワーカで重複検索完了（旧アルゴリズム）')
        else:
            # 新LSHアルゴリズム使用（デフォルト）
            logger.info(f'ワーカで重複検索開始（LSHアルゴリズム） (task_id={task_id})')
            task_library_sim_lsh(db=db, mode=mode, task_id=task_id)
            logger.info('ワーカで重複検索完了（LSHアルゴリズム）')

    if args[1] == "rule":
        task_id = args[2] if len(args) > 2 and args[2] != "None" else None
        uuid = None
        logger.info(f'ワーカでrule適応開始 (task_id={task_id})')
        task_library_rule(
            db=db,
            uuid=uuid,
            task_id=task_id
        )
        logger.info('ワーカでrule適応完了')

    if args[1] == "thumbnail_recreate":
        task_id = args[2] if len(args) > 2 else None
        uuid = None
        logger.info(f'ワーカでサムネイル再作成開始 (task_id={task_id})')
        task_thumbnail_recreate(
            db=db,
            book_uuid=uuid,
            task_id=task_id
        )
        logger.info('ワーカでサムネイル再作成完了')

    if args[1] == "integrity_check":
        task_id = args[2] if len(args) > 2 else None
        logger.info(f'ワーカで整合性確認開始 (task_id={task_id})')
        task_library_integrity_check(db=db, task_id=task_id)
        logger.info('ワーカで整合性確認完了')
