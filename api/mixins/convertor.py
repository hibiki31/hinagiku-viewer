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


# ZIP内で対象とする画像拡張子
IMAGE_EXTENSIONS = {".png", ".jpeg", ".jpg"}


class NotContentZipError(Exception):
    """zipファイル内に画像ファイルが存在しません"""


def list_images_in_zip(zip_file: zipfile.ZipFile) -> list[str]:
    """ZIP内の画像ファイル一覧をソート済みで返す

    Args:
        zip_file: 開かれたZipFileオブジェクト

    Returns:
        ソート済みの画像ファイルパスリスト
    """
    file_list = [
        p for p in zip_file.namelist()
        if Path(p).suffix.lower() in IMAGE_EXTENSIONS
    ]
    file_list.sort()
    return file_list


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
        zip_content = list_images_in_zip(existing_zip)

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

        # ページ数取得（list_images_in_zipでソート済み）
        page_len = len(zip_content)
        # サムネイル作成
        if page_len == 0:
            raise NotContentZipError
        cover_path = zip_content[0]
        # Zipから直接メモリに読み込み（レースコンディション回避）
        img_src = Image.open(BytesIO(existing_zip.read(cover_path))).convert('RGB')
        # PIL ImageオブジェクトをそのままConvertorに渡す
        image_convertor(src_path=img_src, dst_path=f'{DATA_ROOT}/book_thum/{book_uuid}.jpg', to_height=600, quality=85)

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


def unzip_original(book_uuid: str) -> list[str]:
    """ZIPファイルを展開し、画像ファイルをoriginal_XXXX形式にリネームして返す

    Args:
        book_uuid: 書籍UUID

    Returns:
        リネーム後の画像ファイルパスリスト（ソート済み）
    """
    original_images = []
    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
        existing_zip.extractall(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp")

    tmp_path = Path(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp")
    file_list = [p for p in tmp_path.rglob("*") if p.suffix.lower() in IMAGE_EXTENSIONS]
    file_list.sort()

    for index, temp_file_path in enumerate(file_list):
        file_ext = temp_file_path.suffix.lower()
        file_path = f"{DATA_ROOT}/book_cache/{book_uuid}/original_{str(index+1).zfill(4)}{file_ext}"
        shutil.move(str(temp_file_path), file_path)
        original_images.append(file_path)

    shutil.rmtree(f"{DATA_ROOT}/book_cache/{book_uuid}/tmp/")
    return original_images


def create_book_page_cache(book_uuid: str, page: int, to_height: int, quality: int) -> None:
    """ZIPから指定ページを読み込み、リサイズしてキャッシュに保存する

    Args:
        book_uuid: 書籍UUID
        page: ページ番号（1始まり）
        to_height: リサイズ後の高さ
        quality: JPEG品質（1-100）

    Raises:
        FileNotFoundError: ZIPファイルが存在しない場合
        HTTPException: ページが存在しない場合
    """
    timer = DebugTimer()
    # キャッシュ先にフォルダ作成
    Path(f"{DATA_ROOT}/book_cache/{book_uuid}/").mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(f'{DATA_ROOT}/book_library/{book_uuid}.zip') as existing_zip:
        file_list_in_zip = list_images_in_zip(existing_zip)

        if page > len(file_list_in_zip):
            raise HTTPException(
                status_code=404,
                detail="ページが存在しません",
            )
        timer.lap("ZIPファイル一覧取得・ソート")

        # 指定されたページだけ読み込んでPILに
        img_src = Image.open(BytesIO(existing_zip.read(file_list_in_zip[page - 1]))).convert('RGB')
        timer.lap("ZIPからページ読み込み")

        # image_convertorを使ってリサイズ・保存（重複ロジック排除）
        dst_path = f"{DATA_ROOT}/book_cache/{book_uuid}/{to_height}_{str(page).zfill(4)}.jpg"
        image_convertor(src_path=img_src, dst_path=dst_path, to_height=to_height, quality=quality)
        timer.lap("変換・保存")




def image_convertor(src_path, dst_path, to_height, quality):
    """
    画像ファイルまたはPIL Imageオブジェクトをリサイズして保存

    Args:
        src_path: ソース画像パス（str/Path）またはPIL Imageオブジェクト
        dst_path: 保存先パス
        to_height: リサイズ後の高さ
        quality: JPEG品質（1-100）
    """
    # PIL Imageオブジェクトまたはパスを受け取る
    if isinstance(src_path, Image.Image):
        img = src_path
    else:
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


