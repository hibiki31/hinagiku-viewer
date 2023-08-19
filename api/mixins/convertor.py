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

from settings import APP_ROOT, DATA_ROOT
from mixins.log import setup_logger
from mixins.database import SessionLocal
from mixins.purser import PurseResult, base_purser

from books.models import *
from users.models import UserModel

import json
import hashlib


logger = setup_logger(__name__)


os.makedirs(f"/tmp/hinav/", exist_ok=True)


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


class NotContentZip(Exception):
    """zipファイル内に画像ファイルが存在しません"""


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


def make_thum(send_book, book_uuid):
    """
    サムネイルの作成とページ数の取得 -> page_len
    """
    with zipfile.ZipFile(send_book) as existing_zip:
        zip_content = [p for p in existing_zip.namelist() if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
        # ページ数取得
        page_len = len(zip_content)
        zip_content.sort()
        # サムネイル作成
        if page_len == 0:
            raise NotContentZip
        cover_path = zip_content[0]
        existing_zip.extract(cover_path, f"/tmp/hinav/")
        image_convertor(src_path=f"/tmp/hinav/{cover_path}",dst_path=f'{DATA_ROOT}/book_thum/{book_uuid}.jpg',to_height=600,quality=85)
  
    return page_len


def task_convert(book_uuid, to_height=1080, mode=2):
    timer = DebugTimer()
    # キャッシュ先にフォルダ作成
    os.makedirs(f"{DATA_ROOT}/book_cache/{book_uuid}/", exist_ok=True)
    # 解凍
    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
        file_list_in_zip = existing_zip.namelist()
        file_list_in_zip = [p for p in file_list_in_zip if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
        file_list_in_zip.sort()

        for index, file_name in enumerate(file_list_in_zip):
            convert_path = f"{DATA_ROOT}/book_cache/{book_uuid}/{to_height}_{str(index+1).zfill(4)}.jpg"
            convert_tmep = f"{DATA_ROOT}/book_cache/{book_uuid}/{to_height}_{str(index+1).zfill(4)}.book_temp.jpg"
            
            if mode == 1:
                existing_zip.extract(file_name, f'/tmp/hinav/{book_uuid}')
                image_convertor(f'/tmp/hinav/{book_uuid}/{file_name}', convert_path, to_height=to_height,quality=85)
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
    shutil.rmtree(f"/tmp/hinav/")
    os.mkdir(f"/tmp/hinav/")
    timer.rap("変換終了")




def direct_book_page(book_uuid, page, to_height, quality):
    timer = DebugTimer()
    try:
        with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
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
    os.makedirs(f"{DATA_ROOT}/book_cache/{book_uuid}/", exist_ok=True)
    
    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
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
        dst_path = f"{DATA_ROOT}/book_cache/{book_uuid}/{to_height}_{str(page).zfill(4)}.jpg"
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