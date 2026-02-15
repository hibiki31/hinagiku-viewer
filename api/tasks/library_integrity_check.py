from pathlib import Path
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from books.models import BookModel
from mixins.log import setup_logger
from settings import DATA_ROOT
from tasks.utility import update_task_status

logger = setup_logger(__name__)


def main(db: Session, task_id: Optional[str] = None):
    """
    ライブラリ整合性確認タスク

    全書籍のZipファイル存在を確認し、存在しない場合は以下のステータスを設定：
    - "duplicate_missing_file": 同じSHA1ハッシュの別登録がある（過去のバグによる重複）
    - "missing_file": ファイルが完全にロスト

    Args:
        db: DBセッション
        task_id: タスクID
    """
    try:
        if task_id:
            update_task_status(db, task_id, status="running", progress=0, current_step="初期化中", message="全書籍を確認中")

        # 全書籍を取得
        all_books = db.query(BookModel).all()
        total = len(all_books)

        if total == 0:
            logger.info("対象書籍がありません")
            if task_id:
                update_task_status(
                    db, task_id,
                    status="completed",
                    progress=100,
                    current_step="完了",
                    current_item=0,
                    message="対象書籍がありません"
                )
            return

        logger.info(f"整合性確認開始: 対象書籍数 {total}")

        if task_id:
            update_task_status(
                db, task_id,
                progress=5,
                current_step="整合性確認中",
                total_items=total,
                message=f"{total}冊の整合性を確認"
            )

        missing_count = 0
        duplicate_count = 0
        normal_count = 0
        skip_count = 0

        for idx, book in enumerate(all_books, 1):
            # Zipファイルのパスを構築
            file_path = Path(f"{DATA_ROOT}/book_library/{book.uuid}.zip")

            # ファイルが存在する場合
            if file_path.exists():
                if book.state in ["missing_file", "duplicate_missing_file"]:
                    # 異常状態から正常に修復
                    book.state = None
                    normal_count += 1
                else:
                    # すでに正常状態（何もしない）
                    skip_count += 1
            else:
                # ファイルが存在しない場合、同じSHA1の別の書籍を検索
                duplicate_books = db.query(BookModel).filter(
                    and_(
                        BookModel.sha1 == book.sha1,
                        BookModel.uuid != book.uuid
                    )
                ).all()

                if duplicate_books:
                    # 重複登録がある場合
                    book.state = "duplicate_missing_file"
                    duplicate_count += 1
                    logger.warning(f"[{idx}/{total}] 重複登録（ファイル欠損）: {book.uuid} (SHA1: {book.sha1}, 重複数: {len(duplicate_books)})")
                else:
                    # ファイル完全ロスト
                    book.state = "missing_file"
                    missing_count += 1
                    logger.error(f"[{idx}/{total}] ファイルロスト: {book.uuid} (SHA1: {book.sha1}, タイトル: {book.title})")

            # 進捗更新（100冊ごと、または1%ごと、または最後の書籍）
            if task_id:
                update_interval = min(100, max(1, total // 100))  # 1%刻みまたは100冊ごと
                if idx % update_interval == 0 or idx == total:
                    progress = 5 + int((idx / total) * 90)
                    update_task_status(
                        db,
                        task_id,
                        progress=progress,
                        current_item=idx,
                        message=f"{idx}/{total}冊確認（ロスト: {missing_count}, 重複: {duplicate_count}, 修復: {normal_count}）"
                    )

        # 変更をコミット
        db.commit()

        # 最終結果
        logger.info(
            f"整合性確認完了: "
            f"ファイルロスト {missing_count}件 / "
            f"重複登録（ファイル欠損） {duplicate_count}件 / "
            f"修復 {normal_count}件 / "
            f"スキップ {skip_count}件 / "
            f"合計 {total}件"
        )

        if task_id:
            update_task_status(
                db,
                task_id,
                status="completed",
                progress=100,
                current_step="完了",
                current_item=total,
                message=f"完了: ロスト{missing_count}件/重複{duplicate_count}件/修復{normal_count}件/スキップ{skip_count}件"
            )

    except Exception as e:
        logger.error(f"整合性確認エラー: {e}", exc_info=True)
        if task_id:
            update_task_status(db, task_id, status="failed", error_message=str(e))
        raise
