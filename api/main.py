import time, uvicorn

from fastapi import FastAPI, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from mixins.log import setup_logger
from mixins.database import SessionLocal
from mixins.settings import DATA_ROOT, APP_ROOT

from books.router import app as books_router
from users.router import app as users_router
from media.router import app as media_router

from media.router import library_pool, converter_pool


logger = setup_logger(__name__)


tags_metadata = [
    { "name": "book", "description": "The book is managed by uuid and has an owner"},
    { "name": "library", "description": "Books always belong to one library"}
]

app = FastAPI(
    title="Hinagiku-Viewer",
    description="",
    version="1.2.0",
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


@app.on_event("startup")
def startup_event():
    pass


@app.on_event("shutdown")
def shutdown_event():
    for w in library_pool:
        w.terminate()
    for w in converter_pool:
        w.terminate()

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