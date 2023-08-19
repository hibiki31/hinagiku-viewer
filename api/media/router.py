import subprocess, os, asyncio

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse

from mixins.log import setup_logger
from settings import DATA_ROOT, APP_ROOT
from mixins.convertor import create_book_page_cache

from books.schemas import BookCacheCreate, LibraryPatch
from users.router import get_current_user
from users.schemas import UserCurrent

app = APIRouter()
logger = setup_logger(__name__)


converter_pool = []
library_pool = []


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        print(f'[{cmd!r} exited with {proc.returncode}]')
        if stdout:
            print(f'[stdout]\n{stdout.decode()}')
        if stderr:
            print(f'[stderr]\n{stderr.decode()}')


@app.get("/media/books/{uuid}", tags=["Media"], summary="test")
def get_media_books_uuid(
        uuid: str
    ):
    file_path = f"{DATA_ROOT}book_thum/{uuid}.jpg"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="ファイルが存在しません",
        )
    return FileResponse(file_path)


@app.get("/media/books/{uuid}/{page}", tags=["Media"])
def media_books_uuid_page(
        uuid: str,
        page: int,
        height: int = 1080,
    ):
    
    cache_file = f"{DATA_ROOT}book_cache/{uuid}/{height}_{str(page).zfill(4)}.jpg"
    if os.path.exists(cache_file):
        logger.debug(f"キャッシュから読み込み{uuid} {page}")
    else:
        create_book_page_cache(uuid, page, height, 85)
    return FileResponse(path=cache_file)


# @app.get("/media/books/async/{uuid}/{page}")
# async def media_books_async_uuid_page(
#         uuid: str,
#         page: int,
#         height: int = 1080,
#     ):
    
#     cache_file = f"{DATA_ROOT}book_cache/{uuid}/{height}_{str(page).zfill(4)}.jpg"
#     if await AsyncPath(cache_file).exists():
#         logger.debug(f"キャッシュから読み込み{uuid} {page}")
#     else:
#         cmd = f"python3 {APP_ROOT}worker.py page {uuid} {str(height)} {str(page)}"
#         await run(cmd)
#     return FileResponse(path=cache_file)


@app.patch("/media/books", tags=["Media"])
def patch_media_books_(
        model: BookCacheCreate,
        current_user:UserCurrent = Depends(get_current_user)
    ):
    for w in converter_pool:
        w.terminate()
    converter_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "convert", model.uuid, str(model.height)]))
    return { "status": "ok", "model": model }


@app.patch("/media/library", tags=["Media"])
def patch_media_library(
        model: LibraryPatch,
        current_user:UserCurrent = Depends(get_current_user)
    ):
    """
    load or export
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

    return { "status": "ok" }