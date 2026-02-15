from pathlib import Path

from sqlalchemy.orm import Session

from books.models import BookModel
from mixins.convertor import DebugTimer, image_convertor, unzip_original
from mixins.log import setup_logger
from settings import DATA_ROOT

logger = setup_logger(__name__)


def main(db: Session, book_uuid: str, to_height: int = 1080, mode: int = 3) -> None:
    """書籍の全ページをキャッシュとして変換・保存する

    Args:
        db: DBセッション
        book_uuid: 書籍UUID
        to_height: リサイズ後の高さ
        mode: 変換モード（未使用、互換性のため維持）
    """
    timer = DebugTimer()
    # キャッシュ先にフォルダ作成
    Path(f"{DATA_ROOT}/book_cache/{book_uuid}/").mkdir(parents=True, exist_ok=True)

    # 解凍
    original_images = unzip_original(book_uuid=book_uuid)
    original_images.sort()

    # 変換
    for index, original_image in enumerate(original_images):
        convert_path = f"{DATA_ROOT}/book_cache/{book_uuid}/{to_height}_{str(index+1).zfill(4)}.jpg"
        image_convertor(original_image, convert_path, to_height=to_height, quality=85)

    # キャッシュの状態を保存
    book_model: BookModel = db.query(BookModel).filter(BookModel.uuid == book_uuid).one()
    book_model.cached = True
    db.commit()

    timer.lap(f"変換終了: {book_uuid}")
