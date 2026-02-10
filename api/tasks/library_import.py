import datetime
import json
import shutil
import uuid
import zlib
from pathlib import Path
from zipfile import BadZipFile

import PIL
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
from mixins.convertor import NotContentZip, get_hash, make_thumbnail
from mixins.log import setup_logger
from mixins.parser import ParseResult, parse_filename
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
    # ディレクトリ作成
    Path(f"{DATA_ROOT}/book_library/").mkdir(parents=True, exist_ok=True)
    Path(f"{DATA_ROOT}/book_send/").mkdir(parents=True, exist_ok=True)
    Path(f"{DATA_ROOT}/book_fail/").mkdir(parents=True, exist_ok=True)
    Path(f"{DATA_ROOT}/book_thum/").mkdir(parents=True, exist_ok=True)

    user_model = db.query(UserModel).filter(UserModel.id == user_id).one()

    send_books_path = Path(f"{DATA_ROOT}/book_send")
    send_books_list = [str(p) for p in send_books_path.rglob("*") if p.suffix.lower() == ".zip"]
    if len(send_books_list) != 0:
        logger.info(str(len(send_books_list)) + "件の本をライブラリに追加します")

    for send_book in send_books_list:
        try:
            book_import(send_book, user_model, db)

        except (PIL.Image.DecompressionBombError, NotContentZip, BadZipFile, zlib.error) as e:
            logger.error(f'{send_book} ファイルに問題があるためインポート処理を中止 {e}')
            shutil.move(send_book, f'{DATA_ROOT}/book_fail/{Path(send_book).name}')

        except Exception as e:
            logger.critical(e, exc_info=True)
            logger.critical(f'{send_book} 補足できないエラーが発生したためインポート処理を中止')

def book_import(send_book, user_model, db):
    # モデル定義
    pre_model = PreBookClass()
    send_book_path = Path(send_book)

    # チェックサム
    pre_model.sha1 = get_hash(send_book)

    # ライブラリ名定義
    if send_book_path.parent.name == "book_send":
        pre_model.library = "default"
    else:
        pre_model.library = send_book_path.parent.name

    json_path = send_book_path.with_suffix('.json')
    if json_path.exists():
        # Jsonインポート
        with json_path.open() as f:
            json_metadata = json.load(f)
        # 破損チェック
        if pre_model.sha1 != json_metadata["sha1"]:
            logger.error(f'{send_book} メタデータとハッシュ値が異なるため破損している可能性がありエラーへ移動')
            shutil.move(send_book, f'{DATA_ROOT}/book_fail/{send_book_path.name}')
            return
        # モデルに代入
        pre_model = book_model_mapper_json(pre_model, json_metadata)
        is_import = True
    else:
        # 新規追加モード
        pre_model.uuid = str(uuid.uuid4())
        # ファイル名からパース
        parsed_filename: ParseResult = parse_filename(send_book_path.name)
        pre_model = book_model_mapper_file(pre_model, parsed_filename)
        pre_model.size = send_book_path.stat().st_size
        pre_model.file_date = datetime.datetime.fromtimestamp(send_book_path.stat().st_mtime)
        pre_model.import_file_name = send_book_path.name
        is_import = False

    # サムネイルの作成、ページ数取得、マルチハッシュ計算
    page_len, ahash, phash, dhash = make_thumbnail(send_book, pre_model.uuid)
    pre_model.page = page_len
    pre_model.ahash = ahash
    pre_model.phash = phash
    pre_model.dhash = dhash

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

    if pre_model.publisher is not None:
        publisher_model = db.query(PublisherModel).filter(PublisherModel.name==pre_model.publisher).one_or_none()

        if publisher_model is None:
            publisher_model = PublisherModel(name=pre_model.publisher)
            db.add(publisher_model)
            db.commit()
            pre_model.publisher_id = publisher_model.id
        else:
            pre_model.publisher_id = publisher_model.id

    if (pre_model.series is not None) and not (series_model := db.query(SeriesModel).filter(SeriesModel.name==pre_model.series).one_or_none()):
        series_model = SeriesModel(name=pre_model.series)
        db.add(series_model)
        db.commit()
        pre_model.series_model = series_model.id
    elif (pre_model.series is not None):
        pre_model.series_model = series_model.id

    model = BookModel(
        sha1 = pre_model.sha1,
        ahash = pre_model.ahash,
        phash = pre_model.phash,
        dhash = pre_model.dhash,
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
        is_shared = False
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
    Path("/tmp/hinav/").mkdir()


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
