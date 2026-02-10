import os, uuid, datetime, shutil, glob, json

from sqlalchemy import or_, and_

from settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.purser import PurseResult, base_purser
from mixins.convertor import get_hash, make_thum

from books.models import BookModel, LibraryModel, PublisherModel, SeriesModel, GenreModel, AuthorModel, BookUserMetaDataModel
from users.models import UserModel


logger = setup_logger(__name__)




def main(db, delete_uuid, file_name):
    delete_path = f"{DATA_ROOT}/book_export/deleted"
    os.makedirs(delete_path, exist_ok=True)

    try:
        shutil.move(f'{DATA_ROOT}/book_thum/{delete_uuid}.jpg', os.path.join(delete_path, file_name+".jpg"))
        shutil.move(f'{DATA_ROOT}/book_library/{delete_uuid}.zip', os.path.join(delete_path, file_name))
        os.removedirs(f'{DATA_ROOT}/book_cache/{delete_uuid}')
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

    os.makedirs(export_dir, exist_ok=True)

    try:
        shutil.move(export_file, export_dir+file_name)
    except FileNotFoundError:
        logger.error(f"UUID={book_model.uuid}: 存在しないためデータベースから消去")
    
    try:
        os.remove(f'{DATA_ROOT}/book_cache/thum/{book_uuid}.jpg')
    except:
        logger.error(f'UUID={book_model.uuid}: サムネイルが削除出来ませんでした')

    os.chmod(export_dir+file_name,777)


def get_model_dict(model):
    return dict((
            column.name, 
            getattr(model, column.name)
        )
        for column in model.__table__.columns
    )