import hashlib
import shutil
import zipfile
from io import BytesIO
from pathlib import Path
from time import sleep, time

from fastapi import HTTPException
from PIL import Image, ImageFile
from sqlalchemy.orm import Session

from books.models import *
from mixins.log import setup_logger
from settings import DATA_ROOT
from system.utility import get_setting

logger = setup_logger(__name__)


Path("/tmp/hinav/").mkdir(parents=True, exist_ok=True)
# OSError: image file is truncated (2 bytes not processed)を回避
ImageFile.LOAD_TRUNCATED_IMAGES = True

class DebugTimer:
    """デバッグ用のラップタイム計測クラス"""
    def __init__(self):
        self.time = time()

    def lap(self, message, level='debug'):
        """ラップタイムを記録する"""
        now_time = time()
        run_time = (now_time - self.time) * 1000
        if level == 'info':
            logger.info(f'{run_time:.1f}ms - {message}')
        else:
            logger.debug(f'{run_time:.1f}ms - {message}')
        self.time = now_time
        return run_time


class NotContentZipError(Exception):
    """zipファイル内に画像ファイルが存在しません"""


def debug():
    pass


def get_hash(path):
    # ハッシュアルゴリズム決定
    algo = 'sha1'
    # ハッシュオブジェクト作成
    h = hashlib.new(algo)
    # 分割する長さをブロックサイズの整数倍で指定
    Length = hashlib.new(algo).block_size * 0x800

    with Path(path).open('rb') as f:
        BinaryData = f.read(Length)

        # データがなくなるまでループ
        while BinaryData:
            # ハッシュオブジェクトに追加して計算
            h.update(BinaryData)
            # データの続きを読み込む
            BinaryData = f.read(Length)

    return h.hexdigest()


def is_copying(file_path):
    """
    ファイルがコピー中かどうかを確認する
    ファイルサイズの変更がなくなるまで待機する

    Returns:
        bool: コピー中ならTrue
    """
    path = Path(file_path)
    for _i in range(1,10):
        seize_point1 = path.stat().st_size
        sleep(1)
        seize_point2 = path.stat().st_size

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


def make_thumbnail(send_book, book_uuid, db: Session):
    """
    サムネイルの作成とページ数の取得
    マルチハッシュ（ahash, phash, dhash）も計算して返す

    Args:
        send_book: Zipファイルのパス
        book_uuid: 書籍UUID
        db: DBセッション

    Returns:
        tuple: (page_len, ahash, phash, dhash)
    """
    import imagehash

    # 除外ファイル名リストを取得
    exclude_filenames_str = get_setting(db, 'thumbnail_exclude_filenames', default='')
    exclude_filenames = [name.strip() for name in exclude_filenames_str.split(',') if name.strip()]

    with zipfile.ZipFile(send_book) as existing_zip:
        zip_content = [p for p in existing_zip.namelist() if Path(p).suffix.lower() in [".png", ".jpeg", ".jpg"]]

        # 除外ファイルをフィルタリング
        if exclude_filenames:
            filtered_content = []
            for file_path in zip_content:
                file_name = Path(file_path).name
                # ファイル名に除外文字列が含まれていないかチェック
                should_exclude = False
                for exclude_name in exclude_filenames:
                    if exclude_name in file_name:
                        should_exclude = True
                        logger.debug(f"サムネイル候補から除外: {file_name} (パターン: {exclude_name})")
                        break
                if not should_exclude:
                    filtered_content.append(file_path)
            zip_content = filtered_content

        # ページ数取得
        page_len = len(zip_content)
        zip_content.sort()
        # サムネイル作成
        if page_len == 0:
            raise NotContentZipError
        cover_path = zip_content[0]
        existing_zip.extract(cover_path, "/tmp/hinav/")
        image_convertor(src_path=f"/tmp/hinav/{cover_path}",dst_path=f'{DATA_ROOT}/book_thum/{book_uuid}.jpg',to_height=600,quality=85)

    # マルチハッシュを計算
    try:
        image = Image.open(f'{DATA_ROOT}/book_thum/{book_uuid}.jpg')
        ahash = str(imagehash.average_hash(image, hash_size=16))
        phash = str(imagehash.phash(image, hash_size=16))
        dhash = str(imagehash.dhash(image, hash_size=16))
        logger.debug(f"ハッシュ計算完了 {book_uuid}: ahash={ahash}, phash={phash}, dhash={dhash}")
        return page_len, ahash, phash, dhash
    except Exception as e:
        logger.warning(f"ハッシュ計算失敗 {book_uuid}: {e}")
        return page_len, None, None, None


def task_convert(book_uuid, to_height=1080, mode=3):
    timer = DebugTimer()
    # キャッシュ先にフォルダ作成
    Path(f"{DATA_ROOT}/book_cache/{book_uuid}/").mkdir(parents=True, exist_ok=True)

    # 解凍
    original_images = unzip_original(book_uuid=book_uuid)
    original_images.sort()

    # 変換
    for index, original_image in enumerate(original_images):
        convert_path = f"{DATA_ROOT}/book_cache/{book_uuid}/{to_height}_{str(index+1).zfill(4)}.jpg"
        image_convertor(original_image, convert_path, to_height=to_height, quality=85)
    timer.lap(f"変換終了: {book_uuid}")


def unzip_original(book_uuid):
    original_images = []
    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
        existing_zip.extractall(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp")

    tmp_path = Path(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp")
    file_list = [p for p in tmp_path.rglob("*") if p.suffix.lower() in [".png", ".jpeg", ".jpg"]]
    file_list.sort()

    for index, temp_file_path in enumerate(file_list):
        file_ext = temp_file_path.suffix.lower()
        file_path = f"{DATA_ROOT}/book_cache/{book_uuid}/original_{str(index+1).zfill(4)}{file_ext}"
        shutil.move(str(temp_file_path), file_path)
        original_images.append(file_path)

    shutil.rmtree(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp/")
    return original_images


def unzip_single_file(book_uuid):
    original_images = []

    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
        # zip内の画像パスをリスト化
        file_list_in_zip = existing_zip.namelist()
        file_list_in_zip = [p for p in file_list_in_zip if Path(p).suffix.lower() in [".png", ".jpeg", ".jpg"]]
        file_list_in_zip.sort()

        for index, file_name in enumerate(file_list_in_zip):
            file_ext = Path(file_name).suffix.lower()
            convert_path = f"{DATA_ROOT}/book_cache/{book_uuid}/original_{str(index+1).zfill(4)}{file_ext}"
            convert_tmep = f"{DATA_ROOT}/book_cache/{book_uuid}/original_{str(index+1).zfill(4)}.book_temp{file_ext}"
            existing_zip.extract(file_name, convert_tmep)

            original_images.append(convert_path)

    return original_images


def zip_to_image(existing_zip, file_name, to_height, convert_tmep, convert_path):
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


def direct_book_page(book_uuid, page, to_height, quality):
    timer = DebugTimer()
    try:
        with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
            # 関係あるファイルパスのリストに変更
            file_list_in_zip = existing_zip.namelist()
            file_list_in_zip = [p for p in file_list_in_zip if Path(p).suffix.lower() in [".png", ".jpeg", ".jpg"]]
            file_list_in_zip.sort()

            if page > len(file_list_in_zip):
                raise HTTPException(
                    status_code=404,
                    detail="ページが存在しません",
                )
            timer.lap("リストをソート")

            # 指定されたページだけ読み込んでPILに
            img_src = Image.open(BytesIO(existing_zip.read(file_list_in_zip[page-1]))).convert('RGB')
            timer.lap("ZIPをREADしてPILに")

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
            timer.lap("変換")

            return img_dst
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="本が存在しません",
        ) from None

def create_book_page_cache(book_uuid, page, to_height, quality):
    timer = DebugTimer()
    # キャッシュ先にフォルダ作成
    Path(f"{DATA_ROOT}/book_cache/{book_uuid}/").mkdir(parents=True, exist_ok=True)


    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
        # 関係あるファイルパスのリストに変更
        file_list_in_zip = existing_zip.namelist()
        file_list_in_zip = [p for p in file_list_in_zip if Path(p).suffix.lower() in [".png", ".jpeg", ".jpg"]]
        file_list_in_zip.sort()

        if page > len(file_list_in_zip):
            raise HTTPException(
                status_code=404,
                detail="ページが存在しません",
            )
        timer.lap("リストをソート")

        # 指定されたページだけ読み込んでPILに
        img_src = Image.open(BytesIO(existing_zip.read(file_list_in_zip[page-1]))).convert('RGB')
        timer.lap("ZIPをREADしてPILに")

        # 縦横計算
        width, height = img_src.size
        if height < to_height:
            new_height = height
            new_width = width
        else:
            new_height = int(to_height)
            new_width = int(to_height / height * width)

        # Tempパスを定義
        dst_path = Path(f"{DATA_ROOT}/book_cache/{book_uuid}/{to_height}_{str(page).zfill(4)}.jpg")
        temp_file = dst_path.stem
        temp_ext = dst_path.suffix

        new_img = img_src.resize((new_width, new_height), Image.LANCZOS)
        temp_path = dst_path.parent / f'{temp_file}.page_temp{temp_ext}'
        new_img.save(str(temp_path), quality=quality)
        shutil.move(str(temp_path), str(dst_path))
        timer.lap("変換")




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
    dst_path_obj = Path(dst_path)
    temp_file = dst_path_obj.stem
    temp_ext = dst_path_obj.suffix

    temp_path = dst_path_obj.parent / f'{temp_file}.temp{temp_ext}'
    new_img.save(str(temp_path), quality=quality)
    # 戻す
    shutil.move(str(temp_path), dst_path)


if __name__ == "__main__":
    debug()
