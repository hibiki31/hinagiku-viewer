import subprocess, os, glob, re

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from mixins.database import get_db
from mixins.log import setup_logger
from sqlalchemy.orm import Session, aliased, exc, query, selectinload
from settings import DATA_ROOT, APP_ROOT, CONVERT_THREAD
from mixins.convertor import create_book_page_cache, image_convertor

from books.schemas import BookCacheCreate, LibraryPatch
from users.router import get_current_user
from users.schemas import UserCurrent
from books.models import DuplicationModel, BookModel

app = APIRouter()
logger = setup_logger(__name__)


converter_pool = []
library_pool = []


@app.get("/media/books/cache", tags=["Media"], summary="キャッシュサイズの確認")
def get_media_books_cache(
        current_user:UserCurrent = Depends(get_current_user)
    ):

    original_size = 0
    convert_size = 0
    
    for file in glob.glob(f"{DATA_ROOT}/book_cache/**", recursive=True):
        file_name = os.path.basename(file)
        if re.fullmatch(r"^original_.*",file_name):
            original_size += os.path.getsize(file)
        else:
            convert_size += os.path.getsize(file)
    
    return {"original_mb": original_size/1024/1024, "convert_mb": convert_size/1024/1024}


@app.get("/media/books/duplicate", tags=["Media"], summary="重複本の確認")
def get_media_books_duplicate(
        db: Session = Depends(get_db),
        current_user:UserCurrent = Depends(get_current_user)
    ):

    book_model_1 = aliased(BookModel)
    book_model_2 = aliased(BookModel)

    duplication_books = db.query(
        DuplicationModel,
        book_model_1,
        book_model_2
    ).join(
        book_model_1, book_model_1.uuid==DuplicationModel.book_uuid_1
    ).join(
        book_model_2, book_model_2.uuid==DuplicationModel.book_uuid_2
    )

    # print(duplication_books.statement.compile())

    res = {}

    for dup, book_1, book_2 in duplication_books.all():
        if dup.duplication_id in res:
            res[dup.duplication_id].append(book_1)
            res[dup.duplication_id].append(book_2)
        else:
            res[dup.duplication_id] = [book_1, book_2]
    

    res_list = []
    for key, value in res.items():
        res_list.append({
            "duplicate_uuid": key,
            "books": value
        })


    return res_list
    


@app.get("/media/books/{uuid}", tags=["Media"], summary="サムネイル取得")
def get_media_books_uuid(
        uuid: str
    ):
    file_path = f"{DATA_ROOT}/book_thum/{uuid}.jpg"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="ファイルが存在しません",
        )
    return FileResponse(file_path)


@app.get("/media/books/{uuid}/{page}", tags=["Media"], summary="ページ取得")
def media_books_uuid_page(
        uuid: str,
        page: int,
        height: int = 1080,
    ):
    
    cache_file = f"{DATA_ROOT}/book_cache/{uuid}/{height}_{str(page).zfill(4)}.jpg"
    original_file = f"{DATA_ROOT}/book_cache/{uuid}/original_{str(page).zfill(4)}*"

    if os.path.exists(cache_file):
        logger.debug(f"完全キャッシュから読み込み{uuid} {page}")
    elif glob.glob(original_file):
        logger.debug(f"部分キャッシュから読み込み{uuid} {page}")
        image_convertor(glob.glob(original_file)[0], cache_file, to_height=height, quality=85)
    else:
        create_book_page_cache(uuid, page, height, 85)
    return FileResponse(path=cache_file)


@app.patch("/media/books", tags=["Media"], summary="本の一括変換タスク実行")
def patch_media_books_(
        model: BookCacheCreate,
        current_user:UserCurrent = Depends(get_current_user)
    ):
    
    for i, w in enumerate(converter_pool):
        if w.poll() != None:
            logger.debug(f"完了したプロセスをプールから削除 {w.args}")
            del converter_pool[i]

    # [:-CONVERT_THREAD]で4を超える要素を先頭から（古いプロセスから）切っていける
    for w in converter_pool[:-CONVERT_THREAD]:
        logger.warn(f"最大並行数：{CONVERT_THREAD}を超える{w.args[3]}を強制終了させました")
        w.terminate()

    converter_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "convert", model.uuid, str(model.height)]))
    return { "status": "ok", "model": model }


@app.patch("/media/library", tags=["Media"], summary="ライブラリのロードやエクスポート")
def patch_media_library(
        model: LibraryPatch,
        current_user:UserCurrent = Depends(get_current_user)
    ):
    """
    - state=load ライブラリのロード
    - state=export ライブラリのエクスポート
    """
    for i in library_pool:
        if i.poll() == None:
            return { "status": "allredy" }
    if model.state == "load":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "load", current_user.id]))
    elif model.state == "fixmetadata":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "fixmetadata", current_user.id]))
    elif model.state == "export":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "export"]))
    elif model.state == "export_uuid":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "export_uuid"]))
    elif model.state == "sim_all":
        library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "sim", "all"]))

    return { "status": "ok" }