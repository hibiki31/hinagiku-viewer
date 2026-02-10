import datetime
import json
import os
import shutil
import uuid

from sqlalchemy import and_

from books.models import (
    AuthorModel,
    BookModel,
    BookUserMetaDataModel,
    GenreModel,
    LibraryModel,
    PublisherModel,
    SeriesModel,
)
from mixins.convertor import get_hash, make_thum
from mixins.log import setup_logger
from mixins.purser import PurseResult, base_purser
from settings import DATA_ROOT
from users.models import UserModel

logger = setup_logger(__name__)


class PreBookClass:
    def __init__(self):
        self.uuid = None
        self.sha1 = None
        self.page = None
        self.title = None
        self.publisher = None
        self.publisher_id = None
        self.author = None
        self.author_id = None
        self.library = None
        self.library_id = None
        self.genre = None
        self.genre_id = None
        self.library = None
        self.library_id = None
        self.series = None
        self.series_id = None
        self.series_no = None
        self.rate = None

def main(db, user_id):
    db.query(UserModel).filter(UserModel.id == user_id).one()

    book_models = db.query(BookModel).all()

    for book_model in book_models:
        book_model:BookModel

        file_name_purse:PurseResult = base_purser(book_model.import_file_name)

        publisher_model = db.query(PublisherModel).filter(PublisherModel.name==file_name_purse.publisher).one_or_none()

        if publisher_model is None:
            publisher_model = PublisherModel(name=file_name_purse.publisher)
            db.add(publisher_model)
            db.commit()

        book_model.publisher_id = publisher_model.id
        db.merge(book_model)
        db.commit()


def book_import(send_book, user_model, db):
    # モデル定義
    pre_model = PreBookClass()
    # チェックサム
    pre_model.sha1 = get_hash(send_book)
    # ライブラリ名定義
    if os.path.basename(os.path.dirname(send_book)) == "book_send":
        pre_model.library = "default"
    else:
        pre_model.library = os.path.basename(os.path.dirname(send_book))

    if os.path.exists(f'{os.path.splitext(send_book)[0]}.json'):
        # Jsonインポート
        with open(f'{os.path.splitext(send_book)[0]}.json') as f:
            json_metadata = json.load(f)
        # 破損チェック
        if pre_model.sha1 != json_metadata["sha1"]:
            logger.error(f'{send_book} メタデータとハッシュ値が異なるため破損している可能性がありエラーへ移動')
            shutil.move(send_book, f'{DATA_ROOT}book_fail/{os.path.basename(send_book)}')
            return
        # モデルに代入
        pre_model = book_model_mapper_json(pre_model, json_metadata)
        is_import = True
    else:
        # 新規追加モード
        pre_model.uuid = str(uuid.uuid4())
        # ファイル名からパース
        file_name_purse:PurseResult = base_purser(os.path.basename(send_book))
        pre_model = book_model_mapper_file(pre_model, file_name_purse)
        pre_model.size = os.path.getsize(send_book)
        pre_model.file_date = datetime.datetime.fromtimestamp(os.path.getmtime(send_book))
        pre_model.import_file_name = os.path.basename(send_book)
        is_import = False

    # サムネイルの作成とページ数取得
    pre_model.page = make_thum(send_book, pre_model.uuid)

    if not (library_model := db.query(LibraryModel).filter(and_(LibraryModel.name==pre_model.library,LibraryModel.user_id==user_model.id)).one_or_none()):
        library_model = LibraryModel(name=pre_model.library, user_id=user_model.id)
        db.add(library_model)
        db.commit()
    pre_model.library_id = library_model.id


    if (pre_model.genre is not None) and not (genre_model := db.query(GenreModel).filter(GenreModel.name==pre_model.genre).one_or_none()):
        genre_model = GenreModel(name=pre_model.genre)
        db.add(genre_model)
        db.commit()
        pre_model.genre_id = genre_model.id
    elif (pre_model.genre is not None):
        pre_model.genre_id = genre_model.id

    if (pre_model.publisher is not None) and not (publisher_model := db.query(PublisherModel).filter(PublisherModel.name==pre_model.publisher).one_or_none()):
        publisher_model = PublisherModel(name=pre_model.publisher)
        db.add(publisher_model)
        db.commit()
        pre_model.publisher_id = publisher_model.id
    elif (pre_model.publisher is not None):
        pre_model.publisher = publisher_model.id

    if (pre_model.series is not None) and not (series_model := db.query(SeriesModel).filter(SeriesModel.name==pre_model.series).one_or_none()):
        series_model = SeriesModel(name=pre_model.series)
        db.add(series_model)
        db.commit()
        pre_model.series_model = series_model.id
    elif (pre_model.series is not None):
        pre_model.series_model = series_model.id

    model = BookModel(
        sha1 = pre_model.sha1,
        uuid = pre_model.uuid,
        user_id = user_model.id,
        title = pre_model.title,
        publisher_id = pre_model.publisher_id,
        series_id = pre_model.series_id,
        series_no = pre_model.series_no,
        genre_id = pre_model.genre_id,
        library_id = pre_model.library_id,
        size = pre_model.size,
        page = pre_model.page,
        add_date = pre_model.add_date,
        file_date = pre_model.file_date,
        import_file_name = pre_model.import_file_name,
        is_shered = False
    )

    db.add(model)

    if not (author_model := db.query(AuthorModel).filter(AuthorModel.name==pre_model.author).one_or_none()):
        author_model = AuthorModel(name=pre_model.author)
    model.authors.append(author_model)

    if is_import:
        metadata_model = BookUserMetaDataModel(
            user_id = user_model.id,
            book_uuid = pre_model.uuid,
            rate = pre_model.rate,
        )
        db.add(metadata_model)

    db.commit()

    shutil.move(send_book, f'{DATA_ROOT}/book_library/{pre_model.uuid}.zip')

    if is_import:
        logger.info(f'ライブラリにインポート: {DATA_ROOT}/book_library/{pre_model.uuid}.zip')
    else:
        logger.info(f'ライブラリに追加: {DATA_ROOT}/book_library/{pre_model.uuid}.zip')

    shutil.rmtree("/tmp/hinav/")
    os.mkdir("/tmp/hinav/")


def book_model_mapper_json(model:BookModel, json):

    model.title = json['title']
    model.uuid = json['uuid']
    model.author = json['author']
    model.publisher = json['publisher']
    model.series = json['series']
    model.series_no = json['series_no']
    model.genre = json['genre']
    model.library = json['library']
    model.size = json['size']
    model.page = json['page']
    model.add_date = datetime.datetime.fromisoformat(json['add_date'])
    model.file_date = datetime.datetime.fromisoformat(json['file_date'])
    model.import_file_name = json['import_file_name']
    model.rate = json['rate']

    return model

def book_model_mapper_file(model, file_name_purse):

    model.title = file_name_purse.title
    model.author = file_name_purse.author
    model.publisher = file_name_purse.publisher
    model.add_date = datetime.datetime.now()

    return model
