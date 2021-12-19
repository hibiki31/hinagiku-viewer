from django.http import HttpResponse
from django.http import Http404 as NotFound
from django.core.exceptions import BadRequest
from django.conf import settings

from subprocess import run, PIPE
from time import time
import os

from PIL import Image, ImageFilter, ImageOps
from zipfile import ZipFile
from io import BytesIO 





def index(request, book_uuid, book_page):
    # book_page = int(request.GET.get(key="page"))

    output:str = run(["ls", "-la"], stdout=PIPE, stderr=PIPE, text=True).stdout
    output = output.replace("\n", "<br>")

    return get_book_page_response(book_uuid, page=book_page)


def get_book_page_response(book_uuid, page=1, to_height=1000, quality=80):
    try:
        with ZipFile(f'{settings.BOOK_LIBRARY_PATH}/{book_uuid}.zip') as existing_zip:
            # 関係あるファイルパスのリストに変更
            file_list_in_zip = [p for p in existing_zip.namelist() if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
            file_list_in_zip.sort()
            
            if page > len(file_list_in_zip):
                raise BadRequest("Page number is out of range")
            # 指定されたページだけ読み込んでPILに
            img_src = Image.open(BytesIO(existing_zip.read(file_list_in_zip[page-1]))).convert('RGB')
            
            # 縦横計算
            width, height = img_src.size
            if height > to_height:
                width = int(to_height / height * width)
                height = int(to_height)

            response = HttpResponse(content_type="image/jpeg")
            new_img = img_src.resize((width, height), Image.LANCZOS)
            new_img.save(response, "JPEG",quality=quality)

            return response

    except FileNotFoundError:
        raise NotFound("Book uuid not found")



def task_convert(book_uuid, to_height=1080, mode=2):
    os.makedirs(f"{settings.APP_TEMP_PATH}/", exist_ok=True)
    os.makedirs(f"{settings.BOOK_CACHE_PATH}/{book_uuid}/", exist_ok=True)
    # 解凍
    with zipfile.ZipFile(f'{settings.BOOK_LIBRARY_PATH}/{book_uuid}.zip') as existing_zip:
        file_list_in_zip = existing_zip.namelist()
        file_list_in_zip = [p for p in file_list_in_zip if os.path.splitext(p)[1].lower() in [".png", ".jpeg", ".jpg"]]
        file_list_in_zip.sort()

        for index, file_name in enumerate(file_list_in_zip):
            convert_path = f"{settings.BOOK_CACHE_PATH}/{book_uuid}/{to_height}_{str(index+1).zfill(4)}.jpg"
            convert_tmep = f"{settings.BOOK_CACHE_PATH}/{book_uuid}/{to_height}_{str(index+1).zfill(4)}.book_temp.jpg"
            
            if mode == 1:
                existing_zip.extract(file_name, f'{settings.APP_TEMP_PATH}/{book_uuid}')
                image_convertor(f'{settings.APP_TEMP_PATH}/{book_uuid}/{file_name}', convert_path, to_height=to_height,quality=85)
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
                return img_src.resize((new_width, new_height), Image.LANCZOS)
                new_img.save(convert_tmep, format='JPEG')
                shutil.move(convert_tmep, convert_path)
                logger.debug(convert_path)
    shutil.rmtree(f"{settings.APP_TEMP_PATH}/")