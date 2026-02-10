import shutil
import zipfile
from pathlib import Path
from time import time

from sqlalchemy.orm import Session

from books.models import BookModel
from mixins.convertor import image_convertor
from mixins.log import setup_logger
from settings import DATA_ROOT

logger = setup_logger(__name__)


Path("/tmp/hinav/").mkdir(parents=True, exist_ok=True)


class DebugTimer:
    def __init__(self):
        self.time = time()
    def rap(self, message, level='debug'):
        now_time = time()
        run_time = (now_time - self.time) * 1000
        if level == 'info':
            logger.debug(f'{run_time:.1f}ms - {message}')
        else:
            logger.debug(f'{run_time:.1f}ms - {message}')
        self.time = now_time


def main(db: Session, book_uuid, to_height=1080, mode=3):
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
    book_model:BookModel = db.query(BookModel).filter(BookModel.uuid==book_uuid).one()
    book_model.cached = True
    db.commit()

    timer.rap(f"変換終了: {book_uuid}")


def unzip_original(book_uuid):
    original_images = []
    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
        existing_zip.extractall(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp")

    tmp_path = Path(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp")
    file_list = [p for p in tmp_path.rglob("*") if p.suffix.lower() in [".png", ".jpeg", ".jpg"]]
    file_list.sort()

    for index, temp_file_path in enumerate(file_list):
        file_ext = temp_file_path.suffix.lower()
        file_path = f"{DATA_ROOT}/book_cache/{book_uuid}/original_{str(index+1).zfill(4)}{file_ext}"
        shutil.move(str(temp_file_path), file_path)
        original_images.append(file_path)

    shutil.rmtree(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp/")
    return original_images


def unzip_single_file(book_uuid):
    original_images = []

    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
        # zip内の画像パスをリスト化
        file_list_in_zip = existing_zip.namelist()
        file_list_in_zip = [p for p in file_list_in_zip if Path(p).suffix.lower() in [".png", ".jpeg", ".jpg"]]
        file_list_in_zip.sort()

        for index, file_name in enumerate(file_list_in_zip):
            file_ext = Path(file_name).suffix.lower()
            convert_path = f"{DATA_ROOT}/book_cache/{book_uuid}/original_{str(index+1).zfill(4)}{file_ext}"
            convert_tmep = f"{DATA_ROOT}/book_cache/{book_uuid}/original_{str(index+1).zfill(4)}.book_temp{file_ext}"
            existing_zip.extract(file_name, convert_tmep)

            original_images.append(convert_path)

    return original_images
