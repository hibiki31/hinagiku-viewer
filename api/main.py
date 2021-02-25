import subprocess
import time
import uvicorn
import os

from fastapi import status, FastAPI, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.requests import Request
from typing import List, Optional

from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

from mixins.log import setup_logger
from mixins.database import SessionLocal, Engine, Base
from mixins.settings import DATA_ROOT, APP_ROOT
from mixins.convertor import create_book_page_cache

from books.router import app as books_router
from books.schemas import BookCacheCreate


logger = setup_logger(__name__)

worker_pool = []
converter_pool = []
library_pool = []

tags_metadata = [
    {
        "name": "book",
        "description": "",
    }
]

app = FastAPI(
    title="Hinagiku-Viewer",
    description="",
    version="1.1.0",
    openapi_tags=tags_metadata,
    docs_url="/api",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(books_router)

Base.metadata.create_all(bind=Engine)


@app.get("/media/books/{uuid}")
async def get_media_books_uuid(
        uuid: str
    ):
    file_path = f"{DATA_ROOT}book_cache/thum/{uuid}.jpg"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="ファイルが存在しません",
        )
    return FileResponse(file_path)


@app.get("/media/books/{uuid}/{page}")
def media_books_uuid_page(
        uuid: str,
        page: int,
        direct: bool = True,
        height: int = 1080,
    ):
    if direct:
        cache_file = f"{DATA_ROOT}book_cache/{uuid}/{height}_{str(page).zfill(4)}.jpg"
        if os.path.exists(cache_file):
            logger.debug(f"キャッシュから読み込み{uuid} {page}")
        else:
            create_book_page_cache(uuid, page, height, 85)
        return FileResponse(path=cache_file)


@app.patch("/media/books")
def patch_media_books_(
        model: BookCacheCreate
    ):
    for w in converter_pool:
        w.terminate()
    converter_pool.append(subprocess.Popen(["python3", APP_ROOT + "worker.py", "convert", model.uuid, str(model.height)]))
    return { "status": "ok", "model": model }

@app.patch("/media/library")
def patch_media_library():
    for i in library_pool:
        if i.poll() == None:
            return { "status": "allredy" }
    library_pool.append(subprocess.Popen(["python3", APP_ROOT + "worker.py", "library"]))
    return { "status": "ok"}

def worker_up():
    pass
    # worker_pool.append(subprocess.Popen(["python3", APP_ROOT + "worker.py"]))


def worker_down():
    for w in worker_pool:
        w.terminate()
    for w in converter_pool:
        w.terminate()


@app.on_event("startup")
async def startup_event():
    worker_up()

@app.on_event("shutdown")
async def shutdown_event():
    worker_down()
    

# 全てのリクエストで同じ処理が書ける
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # 処理前のログ記述
    start_time = time.time()
    
    # セッションを各リクエストに載せる
    request.state.db = SessionLocal()

    # 各関数で処理を行って結果を受け取る
    response = await call_next(request)

    # 処理後のログ
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.2f}'.format(process_time)
    logger.info(f"{request.method} {request.client.host} {response.status_code} {request.url.path} {formatted_process_time}ms")

    # 結果を返す
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True, access_log=False)