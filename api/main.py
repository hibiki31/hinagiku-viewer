import subprocess
import time
import uvicorn
import os

from fastapi import status, FastAPI, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.requests import Request
from typing import List, Optional
from asyncio import sleep

from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

from mixins.log import setup_logger
from mixins.database import SessionLocal, Engine, Base
from mixins.settings import DATA_ROOT, APP_ROOT

from books.router import app as books_router


logger = setup_logger(__name__)

worker_pool = []

tags_metadata = [
    {
        "name": "book",
        "description": "",
    }
]

app = FastAPI(
    title="Hinagiku-Viewer",
    description="",
    version="0.0.1",
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


@app.get("/media/books/{uuid}/{page}")
async def main(
        uuid: str = None,
        page: int = None,
    ):
    if uuid == None:
        raise HTTPException(
            status_code=404,
            detail="BOOK_IDを指定してください",
        )
    
    if page == None:
        some_file_path = f"{DATA_ROOT}book_library/{uuid}.jpg"
    else:
        some_file_path = f"{DATA_ROOT}book_cache/{uuid}/{str(page).zfill(4)}.jpg"
    
    for i in range(0,300):
        if not os.path.exists(some_file_path):
            await sleep(0.1)
            continue
        try:
            return FileResponse(some_file_path)
        except:
            await sleep(0.1)
            continue
    raise HTTPException(
        status_code=404,
        detail="ファイルが存在しません",
    )

@app.get("/media/books/{uuid}")
async def get_media_books_uuid(
        uuid: str = None
    ):
    if uuid == None:
        raise HTTPException(
            status_code=404,
            detail="BOOK_IDを指定してください",
        )
    
    some_file_path = f"{DATA_ROOT}book_library/{uuid}.jpg"

    try:
        return FileResponse(some_file_path)
    except:
        raise HTTPException(
            status_code=404,
            detail="ファイルが存在しません",
        )

def worker_up():
    worker_pool.append(subprocess.Popen(["python3", APP_ROOT + "worker.py"]))


def worker_down():
    for w in worker_pool:
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