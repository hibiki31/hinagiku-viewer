"""
SHA1ハッシュが重複している書籍を削除

同じSHA1ハッシュを持つ書籍グループを検出し、
各グループで最も古い（add_dateが最小）1冊のみを保持して、
残りをbook_export/deletedに移動する。
"""
from typing import Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from books.models import BookModel
from mixins.log import setup_logger
from tasks.library_delete import main as library_delete
from tasks.utility import update_task_status

logger = setup_logger(__name__)


def main(db: Session, task_id: Optional[str] = None) -> Dict[str, int]:
    """
    SHA1ハッシュ重複書籍の削除

    処理フロー:
    1. SHA1でグループ化し、2冊以上存在するグループを抽出
    2. 各グループで add_date が最も古い1冊を保持
    3. それ以外を library_delete で削除（book_export/deletedに移動）

    Args:
        db: データベースセッション
        task_id: タスクID

    Returns:
        {"deleted": 削除件数, "error": エラー件数, "kept": 保持件数, "groups": グループ数}
    """
    logger.info("SHA1ハッシュ重複削除開始")

    try:
        # 初期化
        if task_id:
            update_task_status(
                db, task_id,
                status="running",
                progress=0,
                current_step="初期化",
                message="SHA1重複を検出中"
            )

        # ステップ1: SHA1が重複している書籍を抽出（2冊以上存在するもの）
        logger.info("重複SHA1を検出中...")
        duplicate_sha1s = db.query(BookModel.sha1)\
            .group_by(BookModel.sha1)\
            .having(func.count(BookModel.sha1) > 1)\
            .all()

        group_count = len(duplicate_sha1s)
        logger.info(f"重複グループ数: {group_count}グループ")

        if group_count == 0:
            logger.info("重複なし、処理完了")
            if task_id:
                update_task_status(
                    db, task_id,
                    status="completed",
                    progress=100,
                    current_step="完了",
                    current_item=0,
                    total_items=0,
                    message="重複なし"
                )
            return {"deleted": 0, "error": 0, "kept": 0, "groups": 0}

        if task_id:
            update_task_status(
                db, task_id,
                progress=10,
                current_step="削除処理",
                total_items=0,
                message=f"{group_count}グループの重複を処理中"
            )

        # ステップ2: 各グループで削除対象を選定・削除
        deleted_count = 0
        error_count = 0
        kept_count = 0
        total_books_processed = 0

        for idx, sha1_tuple in enumerate(duplicate_sha1s, 1):
            sha1 = sha1_tuple[0]

            # 同じSHA1を持つ書籍を取得（add_dateでソート）
            books = db.query(BookModel)\
                .filter(BookModel.sha1 == sha1)\
                .order_by(BookModel.add_date)\
                .all()

            if len(books) <= 1:
                # 1冊以下の場合はスキップ（念のため）
                continue

            # 最初の1冊を保持、残りを削除
            book_to_keep = books[0]
            books_to_delete = books[1:]

            logger.info(
                f"[{idx}/{group_count}] SHA1グループ処理: "
                f"保持={book_to_keep.uuid}({book_to_keep.import_file_name}), "
                f"削除対象={len(books_to_delete)}冊"
            )
            kept_count += 1

            # 削除処理
            for book in books_to_delete:
                total_books_processed += 1
                try:
                    # 物理ファイルを book_export/deleted に移動
                    library_delete(db, book.uuid, book.import_file_name)

                    # DBレコード削除
                    # BookUserMetaDataModel は DB レベルの CASCADE で自動削除される
                    db.delete(book)
                    db.commit()

                    deleted_count += 1
                    logger.info(f"削除完了: {book.uuid} ({book.import_file_name})")

                except Exception as e:
                    book_uuid = book.uuid
                    logger.error(f"削除エラー {book_uuid}: {e}", exc_info=True)
                    db.rollback()
                    error_count += 1

            # 進捗更新（1%刻み または 10グループごと）
            if task_id and (idx % max(1, group_count // 100) == 0 or idx == group_count):
                progress = 10 + int((idx / group_count) * 85)
                update_task_status(
                    db, task_id,
                    progress=progress,
                    current_item=idx,
                    message=f"処理中: {idx}/{group_count}グループ（削除{deleted_count}件）"
                )

        # 完了
        result = {
            "deleted": deleted_count,
            "error": error_count,
            "kept": kept_count,
            "groups": group_count
        }

        message = f"完了: 削除{deleted_count}件/エラー{error_count}件/保持{kept_count}件（{group_count}グループ）"
        logger.info(message)

        if task_id:
            update_task_status(
                db, task_id,
                status="completed",
                progress=100,
                current_step="完了",
                current_item=group_count,
                message=message
            )

        return result

    except Exception as e:
        logger.error(f"SHA1重複削除エラー: {e}", exc_info=True)
        if task_id:
            update_task_status(
                db, task_id,
                status="failed",
                error_message=str(e)
            )
        raise


if __name__ == "__main__":
    from mixins.database import SessionLocal
    db = SessionLocal()
    result = main(db)
    logger.info(f"結果: {result}")
