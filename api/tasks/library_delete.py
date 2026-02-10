import os
import shutil
from pathlib import Path

from mixins.log import setup_logger
from settings import DATA_ROOT

logger = setup_logger(__name__)




def main(db, delete_uuid, file_name):
    delete_path = f"{DATA_ROOT}/book_export/deleted"
    Path(delete_path).mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(f'{DATA_ROOT}/book_thum/{delete_uuid}.jpg', str(Path(delete_path) / (file_name+".jpg")))
        shutil.move(f'{DATA_ROOT}/book_library/{delete_uuid}.zip', str(Path(delete_path) / file_name))
        cache_dir = f'{DATA_ROOT}/book_cache/{delete_uuid}'
        if Path(cache_dir).exists():
            shutil.rmtree(cache_dir)
    except FileNotFoundError:
        logger.info(f"UUID={delete_uuid}: 削除中一部ファイルは存在しませんでした", exc_info=True)



def task_export(book_model, export_uuid):
    book_uuid = book_model.uuid
    export_file = f'{DATA_ROOT}/book_library/{book_uuid}.zip'
    export_dir = f"{DATA_ROOT}/book_export/"

    if export_uuid:
        file_name = f"{book_uuid}.zip"
    else:
        file_name = book_model.import_file_name

    Path(export_dir).mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(export_file, export_dir+file_name)
    except FileNotFoundError:
        logger.error(f"UUID={book_model.uuid}: 存在しないためデータベースから消去")

    try:
        Path(f'{DATA_ROOT}/book_cache/thum/{book_uuid}.jpg').unlink()
    except Exception:
        logger.error(f'UUID={book_model.uuid}: サムネイルが削除出来ませんでした')

    Path(export_dir+file_name).chmod(0o777)


def get_model_dict(model):
    return {column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }
