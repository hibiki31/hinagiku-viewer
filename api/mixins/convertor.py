import sys
import hashlib

import zipfile

import glob
from PIL import Image, ImageFilter
import os
import uuid

import datetime

import shutil

from mixins.settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.database import SessionLocal

from books.models import BookModel


logger = setup_logger(__name__)


def main():
    # unzip(unzip_file=zip_name, to_dir=dir_name)

    file_list = list_dir_files(search_dir=dir_name)

    new_list = [p for p in file_list if os.path.splitext(p)[1] in [".png", ".jpeg", ".jpg"]]

    for index, image_path in enumerate(new_list):
        image_convertor(image_path,f"temp/aaa_con/{str(index+1).zfill(4)}.jpg",height=1080,quality=90)


def task_library():
    db = SessionLocal()
    send_books_list = glob.glob(f"{DATA_ROOT}send_books/**", recursive=True)
    send_books_list = [p for p in send_books_list if os.path.splitext(p)[1] in [".zip"]]

    for send_book in send_books_list:
        book_uuid = uuid.uuid4()
        with zipfile.ZipFile(send_book) as existing_zip:
            zip_content = [p for p in existing_zip.namelist() if os.path.splitext(p)[1] in [".png", ".jpeg", ".jpg"]]
            cover_path = zip_content[0]
            existing_zip.extract(cover_path, f"{APP_ROOT}temp/")
            image_convertor(src_path=f"{APP_ROOT}temp/{cover_path}",dst_path=f'{DATA_ROOT}book_library/{book_uuid}.jpg',height=320,quality=85)
            
        
        
        model = BookModel(
            uuid = str(book_uuid),
            add_date = datetime.datetime.now(),
            import_file_name = os.path.basename(send_book)
        )
        db.add(model)
        db.commit()
        shutil.move(send_book, f'{DATA_ROOT}book_library/{book_uuid}.zip')
        logger.info(f'ライブラリに追加: {DATA_ROOT}book_library/{book_uuid}.zip')


    return

def task_convert(book_uuid):
    logger.info(book_uuid)
    with zipfile.ZipFile(f'{DATA_ROOT}book_library/{book_uuid}.zip') as existing_zip:
        existing_zip.extractall(f'{APP_ROOT}temp/{book_uuid}/')

    file_list =  glob.glob(f'{APP_ROOT}temp/{book_uuid}/**', recursive=True)
    new_list = [p for p in file_list if os.path.splitext(p)[1] in [".png", ".jpeg", ".jpg"]]

    os.makedirs(f"{DATA_ROOT}book_cache/{book_uuid}/", exist_ok=True)

    for index, image_path in enumerate(new_list):
        logger.debug(image_path)
        image_convertor(image_path,f"{DATA_ROOT}book_cache/{book_uuid}/{str(index+1).zfill(4)}.jpg",height=1080,quality=90)



def image_convertor(src_path, dst_path, height, quality):
    im = Image.open(src_path)

    # print(im.format, im.size, im.mode)

    width, height = im.size

    new_height = int(height)
    new_width = int(width / height * new_height)
    
    new_im: Image = im.resize((new_width, new_height), Image.LANCZOS)



    new_im.save(dst_path, quality=quality)






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