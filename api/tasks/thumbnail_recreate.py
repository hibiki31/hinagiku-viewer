import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from books.models import BookModel
from mixins.convertor import make_thumbnail
from mixins.database import SessionLocal
from mixins.log import setup_logger
from settings import CONVERT_THREAD, DATA_ROOT
from tasks.utility import update_task_status

logger = setup_logger(__name__)


def process_single_book(book_data: dict, total: int, progress_lock: threading.Lock, counters: dict) -> dict:
    """
    単一書籍のサムネイル再作成を処理（ワーカースレッド用）

    Args:
        book_data: 書籍情報 (uuid, index)
        total: 総書籍数
        progress_lock: 進捗カウンター用ロック
        counters: 共有カウンター辞書 (success_count, error_count, processed_count)

    Returns:
        処理結果の辞書
    """
    book_uuid = book_data["uuid"]
    index = book_data["index"]
    book_path = Path(f"{DATA_ROOT}/book_library/{book_uuid}.zip")

    # Zipファイルの存在確認
    if not book_path.exists():
        logger.warning(f"[{index}/{total}] Zipファイルが存在しません: {book_uuid}")
        with progress_lock:
            counters["error_count"] += 1
            counters["processed_count"] += 1
        return {"uuid": book_uuid, "success": False, "error": "Zipファイルが存在しません"}

    # 各スレッドで独立したDBセッションを作成
    db = SessionLocal()
    try:
        # サムネイル再作成とハッシュ更新
        page_len, ahash, phash, dhash = make_thumbnail(
            send_book=str(book_path),
            book_uuid=book_uuid,
            db=db
        )

        # DB更新
        book_model = db.query(BookModel).filter(BookModel.uuid == book_uuid).first()
        if book_model:
            book_model.page = page_len
            if ahash:
                book_model.ahash = ahash
            if phash:
                book_model.phash = phash
            if dhash:
                book_model.dhash = dhash
            db.commit()

        with progress_lock:
            counters["success_count"] += 1
            counters["processed_count"] += 1

        logger.info(f"[{index}/{total}] サムネイル再作成成功: {book_uuid} (ページ数: {page_len})")
        return {"uuid": book_uuid, "success": True, "page_len": page_len}

    except Exception as e:
        logger.error(f"[{index}/{total}] サムネイル再作成失敗: {book_uuid} - {e}")
        db.rollback()
        with progress_lock:
            counters["error_count"] += 1
            counters["processed_count"] += 1
        return {"uuid": book_uuid, "success": False, "error": str(e)}

    finally:
        db.close()


def main(db: Session, book_uuid: Optional[str] = None, task_id: Optional[str] = None):
    """
    サムネイルを再作成するタスク（並列処理対応）

    Args:
        db: DBセッション
        book_uuid: 指定された場合は該当書籍のみ、Noneの場合は全書籍を処理
        task_id: タスクID
    """
    try:
        if task_id:
            update_task_status(db, task_id, status="running", progress=0, current_step="初期化中", message="対象書籍を確認中")

        # 対象書籍を取得
        if book_uuid:
            book_models = db.query(BookModel).filter(BookModel.uuid == book_uuid).all()
            if not book_models:
                logger.warning(f"指定された書籍が存在しません: {book_uuid}")
                return
        else:
            book_models = db.query(BookModel).all()

        total = len(book_models)
        if total == 0:
            logger.info("対象書籍がありません")
            if task_id:
                update_task_status(db, task_id, status="completed", progress=100, message="対象書籍がありません")
            return

        logger.info(f"サムネイル再作成開始: 対象書籍数 {total}, 並列度 {CONVERT_THREAD}")

        if task_id:
            update_task_status(db, task_id, progress=5, total_items=total, message=f"{total}冊のサムネイルを再作成（並列度: {CONVERT_THREAD}）")

        # 書籍データリストを作成
        book_data_list = [
            {"uuid": book_model.uuid, "index": idx}
            for idx, book_model in enumerate(book_models, 1)
        ]

        # 共有カウンターとロック
        progress_lock = threading.Lock()
        counters = {
            "success_count": 0,
            "error_count": 0,
            "processed_count": 0
        }

        # 並列処理実行
        with ThreadPoolExecutor(max_workers=CONVERT_THREAD) as executor:
            # 全タスクを投入
            future_to_book = {
                executor.submit(process_single_book, book_data, total, progress_lock, counters): book_data
                for book_data in book_data_list
            }

            # 完了したタスクから処理
            for future in as_completed(future_to_book):
                try:
                    _ = future.result()  # エラーチェックのため呼び出し

                    # 進捗更新（定期的に）
                    if task_id:
                        with progress_lock:
                            processed = counters["processed_count"]
                            progress = 5 + int((processed / total) * 90)
                            update_task_status(
                                db,
                                task_id,
                                progress=progress,
                                current_item=processed,
                                message=f"{processed}/{total}冊完了（成功: {counters['success_count']}, 失敗: {counters['error_count']}）"
                            )

                except Exception as e:
                    logger.error(f"ワーカースレッドでエラー: {e}")

        # 最終結果
        success_count = counters["success_count"]
        error_count = counters["error_count"]

        logger.info(f"サムネイル再作成完了: 成功 {success_count}件 / 失敗 {error_count}件 / 合計 {total}件")

        if task_id:
            update_task_status(db, task_id, status="completed", progress=100, message=f"完了: 成功{success_count}件/失敗{error_count}件")

    except Exception as e:
        logger.error(f"サムネイル再作成エラー: {e}", exc_info=True)
        if task_id:
            update_task_status(db, task_id, status="failed", error_message=str(e))
        raise
