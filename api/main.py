import warnings

# Pydantic v2のalias_generator関連の警告を抑制
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")

import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.router import app as auth_router
from authors.router import app as authors_router
from books.router import app as books_router
from media.router import app as media_router
from mixins.log import setup_logger
from mixins.router import app as mixins_router
from settings import API_VERSION
from system.router import app as system_router
from tags.router import app as tags_router
from tasks.router import app as tasks_router
from user_datas.router import app as user_datas_router
from users.router import app as users_router

logger = setup_logger(__name__)


tags_metadata = [
    {
        "name": "Auth",
        "description": "認証・認可機能。JWT認証、ログイン、トークン検証、初期セットアップを提供します"
    },
    {
        "name": "Mixin",
        "description": "共通機能。システムバージョン情報、初期化状態の確認を行います"
    },
    {
        "name": "User",
        "description": "ユーザー管理。ユーザーの作成、一覧取得、現在のユーザー情報取得を提供します"
    },
    {
        "name": "Library",
        "description": "ライブラリ管理。書籍を分類・管理するためのライブラリ機能を提供します。各書籍は必ず1つのライブラリに所属します"
    },
    {
        "name": "Book",
        "description": "書籍管理。書籍の検索、更新、削除、ダウンロード機能を提供します。高度なフィルタリング・ソート・ページネーション機能を含みます"
    },
    {
        "name": "Author",
        "description": "著者管理。著者情報の管理、書籍との関連付けを行います。お気に入り著者の設定、著者別書籍数の集計などの機能を提供します"
    },
    {
        "name": "Tag",
        "description": "タグ管理。書籍の分類・整理のためのタグ機能を提供します"
    },
    {
        "name": "User data",
        "description": "ユーザーデータ管理。書籍の評価、閲覧履歴、読書進捗などのユーザー固有データを管理します"
    },
    {
        "name": "Media",
        "description": "メディア処理。画像キャッシュ、サムネイル、ページ画像の配信、重複検出機能を提供します。動的な画像リサイズとキャッシング機構を含みます"
    },
    {
        "name": "Task",
        "description": "タスク管理。ライブラリインポート、エクスポート、類似度計算、整合性チェックなど長時間実行タスクの管理機能を提供します"
    },
    {
        "name": "System",
        "description": "システム設定管理。動的に追加・変更可能なKey-Value型の設定ストレージ。カテゴリ別管理、型変換、公開設定などの機能を提供します"
    },
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

app.include_router(router=auth_router)
app.include_router(router=users_router)
app.include_router(router=books_router)
app.include_router(router=media_router)
app.include_router(router=tags_router)
app.include_router(router=authors_router)
app.include_router(router=user_datas_router)
app.include_router(router=mixins_router)
app.include_router(router=tasks_router)
app.include_router(router=system_router)


if __name__ == "__main__":
    # OpenAPI JSONをファイルとして保存
    openapi_schema = app.openapi()
    with Path("openapi.json").open("w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
    logger.info("OpenAPI JSONを openapi.json として保存しました")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, access_log=False)
