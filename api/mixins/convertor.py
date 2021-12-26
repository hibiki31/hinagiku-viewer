import sys
import hashlib

import zipfile

import glob
from PIL import Image, ImageFilter
from io import BytesIO 
import os
import uuid

from fastapi import HTTPException

import datetime
from time import sleep, time


import shutil

from sqlalchemy.sql.functions import mode

from mixins.settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.database import SessionLocal
from mixins.purser import PurseResult, base_purser

from books.models import *
from users.models import UserModel

import json
import hashlib



logger = setup_logger(__name__)


os.makedirs(f"{APP_ROOT}temp/", exist_ok=True)


class DebugTimer():
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



def get_hash(path):
    # ハッシュアルゴリズム決定
    algo = 'sha1'
    # ハッシュオブジェクト作成
    h = hashlib.new(algo)
    # 分割する長さをブロックサイズの整数倍で指定
    Length = hashlib.new(algo).block_size * 0x800

    with open(path,'rb') as f:
        BinaryData = f.read(Length)

        # データがなくなるまでループ
        while BinaryData:
            # ハッシュオブジェクトに追加して計算
            h.update(BinaryData)
            # データの続きを読み込む
            BinaryData = f.read(Length)

    return h.hexdigest()



def book_icon():
    send_books_list = glob.glob(f"{DATA_ROOT}book_library/**", recursive=True)
    send_books_list = [p for p in send_books_list if os.path.splitext(p)[1].lower() in [".zip"]]

    for send_book in send_books_list:
        book_uuid = os.path.splitext(os.path.basename(send_book))[0]
        print(send_book)
        try:
            with zipfile.ZipFile(send_book) as existing_zip:
                zip_content = [p for p in existing_zip.namelist() if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
                page_len = len(zip_content)
                cover_path = zip_content[0]
                existing_zip.extract(cover_path, f"{APP_ROOT}temp/")
                image_convertor(src_path=f"{APP_ROOT}temp/{cover_path}",dst_path=f'{DATA_ROOT}book_cache/thum/{book_uuid}.jpg',to_height=640,quality=85)
        except:
            import traceback
            traceback.print_exc()
            continue
    return


def is_copping(file_path):
    '''
    ファイルサイズの変更がなくなるまで待機する
    '''
    for i in range(1,10):
        seize_point1 = os.path.getsize(file_path)
        sleep(1)
        seize_point2 = os.path.getsize(file_path)

        if seize_point1 != seize_point2:
            logger.error("サイズが変わったため読み直します")
            continue
        if seize_point2 == 0:
            logger.error("0Byteなので読み直します")
            continue
        # 1秒サイズ変わってないからコピー中では無い
        return False
    # 10秒ずっと変わってたからコピー中
    return True


def task_library(db, user_id):
    # ディレクトリ作成
    os.makedirs(f"{DATA_ROOT}book_library/", exist_ok=True)
    os.makedirs(f"{DATA_ROOT}book_send/", exist_ok=True)
    os.makedirs(f"{DATA_ROOT}book_fail/", exist_ok=True)
    os.makedirs(f"{DATA_ROOT}book_cache/thum/", exist_ok=True)

    user_model = db.query(UserModel).filter(UserModel.id == user_id).one()

    send_books_list = glob.glob(f"{DATA_ROOT}book_send/**", recursive=True)
    send_books_list = [p for p in send_books_list if os.path.splitext(p)[1].lower() in [".zip"]]
    if len(send_books_list) != 0:
        logger.info(str(len(send_books_list)) + "件の本をライブラリに追加します")

    for send_book in send_books_list:
        book_load(send_book, user_model, db)
    return

def make_thum(send_book, book_uuid):
    """
    サムネイルの作成とページ数の取得 -> page_len
    """
    try:
        with zipfile.ZipFile(send_book) as existing_zip:
            zip_content = [p for p in existing_zip.namelist() if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
            # ページ数取得
            page_len = len(zip_content)
            zip_content.sort()
            # サムネイル作成
            cover_path = zip_content[0]
            existing_zip.extract(cover_path, f"{APP_ROOT}temp/")
            image_convertor(src_path=f"{APP_ROOT}temp/{cover_path}",dst_path=f'{DATA_ROOT}book_thum/{book_uuid}.jpg',to_height=600,quality=85)
    except:
        logger.error(f'{send_book} エラーが発生したため除外されました', exc_info=True)
        shutil.move(send_book, f'{DATA_ROOT}book_fail/{os.path.basename(send_book)}')
        return
    return page_len


def book_load(send_book, user_model, db):
    # チェックサム
    sha1 = get_hash(send_book)

    # メタデータの取得を試みる
    josn_path = f'{os.path.splitext(send_book)[0]}.json'
    # インポート用データ
    json_metadata = None
    book_uuid = uuid.uuid4()

    # インポートできた場合は上書き
    if os.path.exists(josn_path):
        with open(josn_path) as f:
            json_metadata = json.load(f)
        book_uuid = json_metadata['uuid']
        if sha1 != json_metadata["sha1"]:
            logger.error(f'{send_book} メタデータとハッシュ値が異なるため破損している可能性がありエラーへ移動')
            shutil.move(send_book, f'{DATA_ROOT}book_fail/{os.path.basename(send_book)}')
            return
    
    page_len = make_thum(send_book, book_uuid)

    # ライブラリ名定義
    get_library = os.path.basename(os.path.dirname(send_book))
    if get_library == "book_send":
        get_library = "default"
    
    # ファイル名からパース
    file_name_purse:PurseResult = base_purser(os.path.basename(send_book))

    if os.path.exists(josn_path):
        title = json_metadata['title']
        author = json_metadata['author']
        publisher = json_metadata['publisher']
        series = json_metadata['series']
        series_no = json_metadata['series_no']
        genre = json_metadata['genre']
        library = json_metadata['library']
        size = json_metadata['size']
        page = json_metadata['page']
        add_date = datetime.datetime.fromisoformat(json_metadata['add_date'])
        file_date = datetime.datetime.fromisoformat(json_metadata['file_date'])
        import_file_name = json_metadata['import_file_name']
    else:
        title = file_name_purse.title
        author = file_name_purse.author
        publisher = file_name_purse.publisher
        series = None
        series_no = None
        genre = None
        library = get_library
        size = os.path.getsize(send_book)
        page = page_len
        add_date = datetime.datetime.now()
        file_date = datetime.datetime.fromtimestamp(os.path.getmtime(send_book))
        import_file_name = os.path.basename(send_book)

    if (library!=None) and not (library_model := db.query(LibraryModel).filter(LibraryModel.name==library).one_or_none()):
        library_model = LibraryModel(name=library)
        db.add(library_model)
        db.commit()
        library = library_model.id
    elif (library!=None):
        library = library_model.id


    if (genre != None) and not (genre_model := db.query(GenreModel).filter(GenreModel.name==genre).one_or_none()):
        genre_model = GenreModel(name=genre)
        db.add(genre_model)
        db.commit()
        genre = genre_model.id
    elif (genre != None):
        genre = genre_model.id
    
    if (publisher != None) and not (publisher_model := db.query(PublisherModel).filter(PublisherModel.name==publisher).one_or_none()):
        publisher_model = PublisherModel(name=publisher)
        db.add(publisher_model)
        db.commit()
        publisher = publisher_model.id
    elif (publisher != None):
        publisher = publisher_model.id

    if (series != None) and not (series_model := db.query(SeriesModel).filter(SeriesModel.name==series).one_or_none()):
        series_model = SeriesModel(name=series)
        db.add(series_model)
        db.commit()
        series_model = series_model.id
    elif (series != None):
        series_model = series_model.id

    model = BookModel(
        sha1 = sha1,
        uuid = str(book_uuid),
        user_id = user_model.id,
        # ソフトメタデータ
        title = title,
        publisher_id = publisher,
        series_id = series,
        series_no = series_no,
        genre_id = genre,
        library_id = library,
        # ハードメタデータ
        size = size,
        page = page,
        add_date = add_date,
        file_date = file_date,
        import_file_name = import_file_name,
        is_shered = False
    )
    
    db.add(model)
    if not (author_model := db.query(AuthorModel).filter(AuthorModel.name==author).one_or_none()):
        author_model = AuthorModel(name=author)
    
    model.authors.append(author_model)
    db.commit()
   
        
    if json_metadata:
        metadata_model = BookUserMetaDataModel(
            user_id = user_model.id,
            book_uuid = str(book_uuid),
            rate = json_metadata['rate'],
        )
        db.add(metadata_model)
    db.commit()
    
    
    shutil.move(send_book, f'{DATA_ROOT}book_library/{book_uuid}.zip')

    if json_metadata:
        logger.info(f'ライブラリにインポート: {DATA_ROOT}book_library/{book_uuid}.zip')
    else:
        logger.info(f'ライブラリに追加: {DATA_ROOT}book_library/{book_uuid}.zip')

    shutil.rmtree(f"{APP_ROOT}temp/")
    os.mkdir(f"{APP_ROOT}temp/")



def export_library(db):
    os.makedirs(f"{DATA_ROOT}book_export/", exist_ok=True)
    for book_model in db.query(BookModel).filter(BookModel.state=="export").all():
        book_model: BookModel
        task_export(book_model=book_model)
        db.query(BookModel).filter(BookModel.uuid==book_model.uuid).delete()
        db.commit()
    return
    for book_model in db.query(BookModel).all():
        book_model: BookModel
        d = get_model_dict(book_model)
        d["sha1"] = get_hash(f'{DATA_ROOT}book_library/{book_model.uuid}.zip')
        d["add_date"] = d["add_date"].isoformat()
        d["file_date"] = d["file_date"].isoformat()
        with open(f"{DATA_ROOT}book_export/{book_model.uuid}.json", 'w') as f:
            json.dump(d, f, indent=4)
    
def get_model_dict(model):
    return dict((
                column.name, 
                getattr(model, column.name)
            )
            for column in model.__table__.columns
        )


def task_convert(book_uuid, to_height=1080, mode=2):
    timer = DebugTimer()
    # キャッシュ先にフォルダ作成
    os.makedirs(f"{DATA_ROOT}book_cache/{book_uuid}/", exist_ok=True)
    # 解凍
    with zipfile.ZipFile(f'{DATA_ROOT}book_library/{book_uuid}.zip') as existing_zip:
        file_list_in_zip = existing_zip.namelist()
        file_list_in_zip = [p for p in file_list_in_zip if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
        file_list_in_zip.sort()

        for index, file_name in enumerate(file_list_in_zip):
            convert_path = f"{DATA_ROOT}book_cache/{book_uuid}/{to_height}_{str(index+1).zfill(4)}.jpg"
            convert_tmep = f"{DATA_ROOT}book_cache/{book_uuid}/{to_height}_{str(index+1).zfill(4)}.book_temp.jpg"
            
            if mode == 1:
                existing_zip.extract(file_name, f'{APP_ROOT}temp/{book_uuid}')
                image_convertor(f'{APP_ROOT}temp/{book_uuid}/{file_name}', convert_path, to_height=to_height,quality=85)
            elif mode == 2:
                # 指定されたページだけ読み込んでPILに
                img_src = Image.open(BytesIO(existing_zip.read(file_name))).convert('RGB')
            
                # 縦横計算
                width, height = img_src.size
                if height < to_height:
                    new_height = height
                    new_width = width
                else:
                    new_height = int(to_height)
                    new_width = int(to_height / height * width)
                
                # 変換
                new_img = img_src.resize((new_width, new_height), Image.LANCZOS)
                new_img.save(convert_tmep, format='JPEG')
                shutil.move(convert_tmep, convert_path)
                logger.debug(convert_path)
    shutil.rmtree(f"{APP_ROOT}temp/")
    os.mkdir(f"{APP_ROOT}temp/")
    timer.rap("変換終了")




def direct_book_page(book_uuid, page, to_height, quality):
    timer = DebugTimer()
    try:
        with zipfile.ZipFile(f'{DATA_ROOT}book_library/{book_uuid}.zip') as existing_zip:
            # 関係あるファイルパスのリストに変更
            file_list_in_zip = existing_zip.namelist()
            file_list_in_zip = [p for p in file_list_in_zip if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
            file_list_in_zip.sort()

            if page > len(file_list_in_zip):
                raise HTTPException(
                    status_code=404,
                    detail="ページが存在しません",
                )
            timer.rap("リストをソート")

            # 指定されたページだけ読み込んでPILに
            img_src = Image.open(BytesIO(existing_zip.read(file_list_in_zip[page-1]))).convert('RGB')
            timer.rap("ZIPをREADしてPILに")
        
            # 縦横計算
            width, height = img_src.size
            if height < to_height:
                new_height = height
                new_width = width
            else:
                new_height = int(to_height)
                new_width = int(to_height / height * width)

            # 空の入れ物用意
            img_dst = BytesIO()
            # 変換
            new_img = img_src.resize((new_width, new_height), Image.LANCZOS)
            new_img.save(img_dst, format='JPEG')
            img_dst.seek(0)
            timer.rap("変換")

            return img_dst
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="本が存在しません",
        )

def create_book_page_cache(book_uuid, page, to_height, quality):
    timer = DebugTimer()
    # キャッシュ先にフォルダ作成
    os.makedirs(f"{DATA_ROOT}book_cache/{book_uuid}/", exist_ok=True)
    
    with zipfile.ZipFile(f'{DATA_ROOT}book_library/{book_uuid}.zip') as existing_zip:
        # 関係あるファイルパスのリストに変更
        file_list_in_zip = existing_zip.namelist()
        file_list_in_zip = [p for p in file_list_in_zip if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
        file_list_in_zip.sort()

        if page > len(file_list_in_zip):
            raise HTTPException(
                status_code=404,
                detail="ページが存在しません",
            )
        timer.rap("リストをソート")

        # 指定されたページだけ読み込んでPILに
        img_src = Image.open(BytesIO(existing_zip.read(file_list_in_zip[page-1]))).convert('RGB')
        timer.rap("ZIPをREADしてPILに")
    
        # 縦横計算
        width, height = img_src.size
        if height < to_height:
            new_height = height
            new_width = width
        else:
            new_height = int(to_height)
            new_width = int(to_height / height * width)

        # Tempパスを定義
        dst_path = f"{DATA_ROOT}book_cache/{book_uuid}/{to_height}_{str(page).zfill(4)}.jpg"
        temp_file = os.path.splitext(dst_path)[0]
        temp_ext = os.path.splitext(dst_path)[1]

        new_img = img_src.resize((new_width, new_height), Image.LANCZOS)
        new_img.save(f'{temp_file}.page_temp{temp_ext}', quality=quality)
        shutil.move(f'{temp_file}.page_temp{temp_ext}', dst_path)
        timer.rap("変換")

    


def image_convertor(src_path, dst_path, to_height, quality):
    img = Image.open(src_path).convert('RGB')

    width, height = img.size
    if height < to_height:
        new_height = height
        new_width = width
    else:
        new_height = int(to_height)
        new_width = int(to_height / height * width)

    new_img = img.resize((new_width, new_height), Image.LANCZOS)
    # Tempで保存
    temp_file = os.path.splitext(dst_path)[0]
    temp_ext = os.path.splitext(dst_path)[1]

    new_img.save(f'{temp_file}.temp{temp_ext}', quality=quality)
    # 戻す
    shutil.move(f'{temp_file}.temp{temp_ext}', dst_path)


def debug():
    pass


if __name__ == "__main__":
    debug()