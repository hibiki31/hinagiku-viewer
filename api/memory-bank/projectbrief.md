# Project Brief - API Module

> **Note**: このAPIモジュールは `/workspace/` ルートディレクトリの hinagiku-viewer プロジェクトのサブモジュールです。
> プロジェクト全体のコンテキストについては、`/workspace/memory-bank/` を参照してください。

## モジュール概要
hinagiku-viewerのバックエンドAPIサーバー。FastAPIを使用したRESTful APIを提供し、書籍管理、メタデータ管理、認証、バックグラウンドタスク処理を担当。

## 主要責務
1. **RESTful APIの提供**: 書籍、著者、タグ、ユーザーデータのCRUD操作
2. **認証・認可**: JWT認証、OAuth2 Password Flow、スコープベースの権限管理
3. **データベース管理**: PostgreSQL + SQLAlchemy 2.0、Alembicマイグレーション
4. **メディア処理**: Zipファイルからの画像抽出、サムネイル生成、キャッシング
5. **バックグラウンドタスク**: インポート、エクスポート、重複チェック、ハッシュ計算
6. **画像処理**: OpenCV、Pillow、ImageHashを使用した画像解析

## APIエンドポイント構成
- `/api/auth` - 認証エンドポイント
- `/api/users` - ユーザー管理
- `/api/books` - 書籍管理
- `/api/authors` - 著者管理
- `/api/tags` - タグ管理
- `/api/media` - メディア配信（画像、キャッシュ）
- `/api/user_datas` - ユーザー固有データ
- `/api/mixin` - ユーティリティエンドポイント

## 主要モジュール
- `main.py` - FastAPIアプリケーションエントリーポイント
- `settings.py` - 環境設定
- `worker.py` - バックグラウンドワーカー
- `books/` - 書籍関連ロジック
- `users/` - ユーザー・認証ロジック
- `authors/` - 著者管理
- `tags/` - タグ管理
- `media/` - メディア配信
- `user_datas/` - ユーザーデータ
- `mixins/` - 共通ユーティリティ
- `tasks/` - バックグラウンドタスク
- `alembic/` - データベースマイグレーション

## 技術制約
- Python 3.11+
- PostgreSQL 16必須
- Docker環境での動作を想定
- ファイル名長の制限（OSError: File name too long対策必要）

## 開発・デプロイ
- 開発: `python3 main.py`（uvicorn自動リロード）
- 本番: `gunicorn --config ./mixins/gnicorn_config.py`
- Docker: `docker-compose up api`
- ポート: 8000（コンテナ内）
