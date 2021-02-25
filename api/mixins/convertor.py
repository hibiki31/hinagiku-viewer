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

from mixins.settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.database import SessionLocal
from mixins.purser import PurseResult, base_purser

from books.models import BookModel


logger = setup_logger(__name__)


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




def main():
    # unzip(unzip_file=zip_name, to_dir=dir_name)

    file_list = list_dir_files(search_dir=dir_name)

    new_list = [p for p in file_list if os.path.splitext(p)[1] in [".png", ".jpeg", ".jpg"]]

    for index, image_path in enumerate(new_list):
        image_convertor(image_path,f"temp/aaa_con/{str(index+1).zfill(4)}.jpg",to_height=1080,quality=90)



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
                image_convertor(src_path=f"{APP_ROOT}temp/{cover_path}",dst_path=f'{DATA_ROOT}book_library/{book_uuid}.jpg',to_height=640,quality=85)
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


def task_library():
    db = SessionLocal()
    # ディレクトリ作成
    os.makedirs(f"{DATA_ROOT}book_library/", exist_ok=True)
    os.makedirs(f"{DATA_ROOT}book_send/", exist_ok=True)
    os.makedirs(f"{DATA_ROOT}book_fail/", exist_ok=True)

    send_books_list = glob.glob(f"{DATA_ROOT}book_send/**", recursive=True)
    send_books_list = [p for p in send_books_list if os.path.splitext(p)[1].lower() in [".zip"]]

    for send_book in send_books_list:
        book_uuid = uuid.uuid4()
        page_len = 0

        try:
            with zipfile.ZipFile(send_book) as existing_zip:
                zip_content = [p for p in existing_zip.namelist() if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
                page_len = len(zip_content)
                zip_content.sort()
                cover_path = zip_content[0]
                existing_zip.extract(cover_path, f"{APP_ROOT}temp/")
                image_convertor(src_path=f"{APP_ROOT}temp/{cover_path}",dst_path=f'{DATA_ROOT}book_library/{book_uuid}.jpg',to_height=256,quality=85)
        except:
            logger.error(f'{send_book}はエラーが発生したため除外されました', exc_info=True)
            shutil.move(send_book, f'{DATA_ROOT}book_fail/{os.path.basename(send_book)}')
            continue


        get_genre = os.path.basename(os.path.dirname(send_book))
        if get_genre == "book_send":
            get_genre = "default"
        
        file_name_purse:PurseResult = base_purser(os.path.basename(send_book))
            
        model = BookModel(
            uuid = str(book_uuid),
            # ソフトメタデータ
            title = file_name_purse.title,
            author = file_name_purse.author,
            publisher = file_name_purse.publisher,
            series = None,
            series_no = None,
            rate = None,
            genre = None,
            library = get_genre,
            # ハードメタデータ
            size = os.path.getsize(send_book),
            page = page_len,
            add_date = datetime.datetime.now(),
            file_date = datetime.datetime.fromtimestamp(os.path.getmtime(send_book)),
            import_file_name = os.path.basename(send_book),
            # アクティブメタデータ
            cache_date = None,
            open_count = 0,
            open_date = None,
            state = "imported",
        )

        db.add(model)
        db.commit()
        shutil.move(send_book, f'{DATA_ROOT}book_library/{book_uuid}.zip')
        logger.info(f'ライブラリに追加: {DATA_ROOT}book_library/{book_uuid}.zip')
    
        shutil.rmtree(f"{APP_ROOT}temp/")
        os.mkdir(f"{APP_ROOT}temp/")
        
        # 応急処置として１件で終了するのでキャッシュ作成が止まらない
        break
    return



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

def task_export(book_model):
    book_uuid = book_model.uuid
    file_name = book_model.import_file_name
    logger.info(f'{book_uuid}をエクスポートします')
    export_file = f'{DATA_ROOT}book_library/{book_uuid}.zip'
    export_dir = f"{DATA_ROOT}book_export/"

    os.makedirs(export_dir, exist_ok=True)
    try:
        shutil.move(export_file, export_dir+file_name)
        os.remove(f'{DATA_ROOT}book_library/{book_uuid}.jpg')
    except:
        logger.error(f'{export_file}は存在しなかったためレコードの削除のみを行いました')



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



def list_dir_files(search_dir):

    return glob.glob(f"./temp/{search_dir}/**", recursive=True)



def hash():
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(sys.argv[1], 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha1.update(data)

    print("MD5: {0}".format(md5.hexdigest()))
    print("SHA1: {0}".format(sha1.hexdigest()))



def unzip(unzip_file, to_dir):
    with zipfile.ZipFile(f'send_books/{unzip_file}') as existing_zip:
        existing_zip.extractall(f'temp/{to_dir}')



if __name__ == "__main__":
    main()