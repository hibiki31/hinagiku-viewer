from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from books.models import BookModel
from mixins.convertor import make_thumbnail
from mixins.log import setup_logger
from settings import DATA_ROOT
from tasks.utility import update_task_status

logger = setup_logger(__name__)


def main(db: Session, book_uuid: Optional[str] = None, task_id: Optional[str] = None):
    """
    サムネイルを再作成するタスク

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
        success_count = 0
        error_count = 0

        logger.info(f"サムネイル再作成開始: 対象書籍数 {total}")
        
        if task_id:
            update_task_status(db, task_id, progress=5, total_items=total, message=f"{total}冊のサムネイルを再作成")

        for index, book_model in enumerate(book_models, 1):
            book_model: BookModel
            book_path = Path(f"{DATA_ROOT}/book_library/{book_model.uuid}.zip")

            # Zipファイルの存在確認
            if not book_path.exists():
                logger.warning(f"[{index}/{total}] Zipファイルが存在しません: {book_model.uuid}")
                error_count += 1
                continue

            try:
                # サムネイル再作成とハッシュ更新
                page_len, ahash, phash, dhash = make_thumbnail(
                    send_book=str(book_path),
                    book_uuid=book_model.uuid,
                    db=db
                )

                # ページ数とハッシュ値を更新
                book_model.page = page_len
                if ahash:
                    book_model.ahash = ahash
                if phash:
                    book_model.phash = phash
                if dhash:
                    book_model.dhash = dhash

                db.commit()
                success_count += 1
                logger.info(f"[{index}/{total}] サムネイル再作成成功: {book_model.uuid} (ページ数: {page_len})")
                
                # 進捗更新
                if task_id:
                    progress = 5 + int((index / total) * 90)
                    update_task_status(db, task_id, progress=progress, current_item=index, message=f"{index}/{total}冊完了")

            except Exception as e:
                logger.error(f"[{index}/{total}] サムネイル再作成失敗: {book_model.uuid} - {e}")
                error_count += 1
                db.rollback()
                continue

        logger.info(f"サムネイル再作成完了: 成功 {success_count}件 / 失敗 {error_count}件 / 合計 {total}件")
        
        if task_id:
            update_task_status(db, task_id, status="completed", progress=100, message=f"完了: 成功{success_count}件/失敗{error_count}件")
            
    except Exception as e:
        logger.error(f"サムネイル再作成エラー: {e}", exc_info=True)
        if task_id:
            update_task_status(db, task_id, status="failed", error_message=str(e))
        raise
