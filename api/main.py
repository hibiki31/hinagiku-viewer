import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from authors.router import app as authors_router
from books.router import app as books_router
from media.router import app as media_router
from mixins.router import app as mixins_router
from media.router import converter_pool, library_pool
from mixins.database import SessionLocal, get_db
from mixins.log import setup_logger
from settings import API_VERSION, APP_ROOT, DATA_ROOT
from tags.router import app as tags_router
from user_datas.router import app as user_datas_router
from users.router import app as users_router


logger = setup_logger(__name__)


tags_metadata = [
    { "name": "Auth"},
    { "name": "Mixin"},
    { "name": "User"},
    { "name": "Library", "description": "本は必ずライブラリに所属する"},
    { "name": "Book", "description": "本は必ず１人のユーザが所有する"},
    { "name": "Author", "description": "本は著者を0以上持ちnullの場合もある"},
]

app = FastAPI(
    title="Hinagiku-Viewer",
    description="",
    version=API_VERSION,
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

app.include_router(router=users_router)
app.include_router(router=books_router)
app.include_router(router=media_router)
app.include_router(router=tags_router)
app.include_router(router=authors_router)
app.include_router(router=user_datas_router)
app.include_router(router=mixins_router)


@app.on_event("startup")
def startup_event():
    pass


@app.on_event("shutdown")
def shutdown_event():
    for w in library_pool:
        w.terminate()
    for w in converter_pool:
        w.terminate()


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    # 処理前のログ記述
    start_time = time.time()

    # 各関数で処理を行って結果を受け取る
    response = await call_next(request)

    # 処理後のログ
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = '{0:.1f}'.format(process_time)
    logger.info(f"{request.method.rjust(5)} {response.status_code} {formatted_process_time.rjust(5)}ms {request.client.host} {request.url.path}")

    # 結果を返す
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=False)