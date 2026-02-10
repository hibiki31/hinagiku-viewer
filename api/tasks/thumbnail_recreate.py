from pathlib import Path

from sqlalchemy.orm import Session

from books.models import BookModel
from mixins.convertor import make_thumbnail
from mixins.log import setup_logger
from settings import DATA_ROOT

logger = setup_logger(__name__)


def main(db: Session, book_uuid: str | None = None):
    """
    サムネイルを再作成するタスク

    Args:
        db: DBセッション
        book_uuid: 指定された場合は該当書籍のみ、Noneの場合は全書籍を処理
    """
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

        except Exception as e:
            logger.error(f"[{index}/{total}] サムネイル再作成失敗: {book_model.uuid} - {e}")
            error_count += 1
            db.rollback()
            continue

    logger.info(f"サムネイル再作成完了: 成功 {success_count}件 / 失敗 {error_count}件 / 合計 {total}件")
