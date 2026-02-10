import warnings
# Pydantic v2のalias_generator関連の警告を抑制
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from authors.router import app as authors_router
from books.router import app as books_router
from media.router import app as media_router
from mixins.router import app as mixins_router
from mixins.log import setup_logger
from settings import API_VERSION
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
    title="HinavAPI",
    description="",
    version=API_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/api",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    servers=[{"url": "", "description": "Default"}]
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=False)