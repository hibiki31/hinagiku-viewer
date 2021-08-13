import os, uuid, datetime, shutil, glob, json

from sqlalchemy import or_, and_

from mixins.settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.purser import PurseResult, base_purser
from mixins.convertor import get_hash, make_thum

from books.models import BookModel, LibraryModel, PublisherModel, SeriesModel, GenreModel, AuthorModel, BookUserMetaDataModel
from users.models import UserModel


logger = setup_logger(__name__)




def main(db, export_uuid):
    print(export_uuid)
    os.makedirs(f"{DATA_ROOT}book_export/", exist_ok=True)
    for book_model in db.query(BookModel).all():
        book_model:BookModel
        d = get_model_dict(book_model)
        d["ver"] = "2.0"
        d["add_date"] = d["add_date"].isoformat()
        d["file_date"] = d["file_date"].isoformat()
        d["user_data"] = []
        d["tags"] = []
        d["authors"] = []
        d["library"] = book_model.library.name
        if book_model.genre == None:
            d["genre"] = None
        else:
            d["genre"] = book_model.genre.name
        
        if book_model.publisher == None:
            d["publicher"] = None
        else:
            d["genre"] = book_model.publisher.name
        
        if book_model.series == None:
            d["series"] = None
        else:
            d["series"] = book_model.series.name

        for i in book_model.user_data:
            d["user_data"].append(get_model_dict(i))
        for i in book_model.tags:
            d["tags"].append(i.name)
        for i in book_model.authors:
            d["authors"].append(i.name)
        
        # ファイル出力
        with open(f"{DATA_ROOT}book_export/{book_model.uuid}.json", 'w') as f:
            json.dump(d, f, indent=4,sort_keys=True)
        
        logger.debug(f"UUID={book_model.uuid}: JSONエクスポート完了")
        task_export(book_model=book_model, export_uuid=export_uuid)
        logger.debug(f"UUID={book_model.uuid}: ファイル移動完了")
        book_model.authors = []
        db.commit()
        db.query(BookModel).filter(BookModel.uuid==book_model.uuid).delete()
        logger.debug(f"UUID={book_model.uuid}: データベース削除完了")
        db.commit()


def task_export(book_model, export_uuid):
    book_uuid = book_model.uuid
    export_file = f'{DATA_ROOT}book_library/{book_uuid}.zip'
    export_dir = f"{DATA_ROOT}book_export/"
    
    if export_uuid:
        file_name = f"{book_uuid}.zip"
    else:
        file_name = book_model.import_file_name

    os.makedirs(export_dir, exist_ok=True)

    print(export_uuid, file_name)

    try:
        shutil.move(export_file, export_dir+file_name)
    except FileNotFoundError:
        logger.error(f"UUID={book_model.uuid}: 存在しないためデータベースから消去")
    
    try:
        os.remove(f'{DATA_ROOT}book_cache/thum/{book_uuid}.jpg')
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