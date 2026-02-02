# Tech Context

## 技術スタック

### バックエンド
- **言語**: Python 3.11+
- **Webフレームワーク**: FastAPI 0.116.1
- **ASGI Server**: 
  - Uvicorn 0.35.0（開発環境）
  - Gunicorn 23.0.0（本番環境）
- **ORM**: SQLAlchemy 2.0.43
- **マイグレーション**: Alembic 1.16.5
- **データベースドライバ**: psycopg2 2.9.10
- **認証**: 
  - PyJWT 2.8.0
  - passlib 1.7.4（bcryptでハッシュ化）
- **HTTP通信**: httpx 0.24.1
- **画像処理**: 
  - Pillow 11.3.0
  - opencv-contrib-python 4.8.0.76
  - imagehash 4.3.1
- **データ処理**: 
  - pandas 2.0.3
  - matplotlib
- **文字列比較**: rapidfuzz 3.6.1
- **その他**: python-multipart 0.0.20

### フロントエンド

#### メインアプリ（web/）
- **フレームワーク**: Vue.js 2.6.11
- **UIフレームワーク**: Vuetify 2.x
- **状態管理**: Vuex 3.4.0
- **ルーティング**: Vue Router 3.2.0
- **HTTP通信**: Axios 0.21.4
- **ビルドツール**: Vue CLI 4.5.0
- **スタイル**: 
  - Sass 1.32.12
  - node-sass 4.12.0
- **その他**: 
  - vue-cookies 1.7.4
  - vue-notification 1.3.20
  - vue-jwt-decode 0.1.0
  - vue2-hammer 2.1.2（タッチジェスチャー）
  - velocity-animate 1.5.2（アニメーション）

#### 次世代アプリ（開発中）
- **nuxt/**: Nuxt 3 + Vue 3 + Vuetify 3
- **vue/**: Vue 3 + Vite + Vuetify 3

### データベース
- **RDBMS**: PostgreSQL 16
- **理由**: 
  - ACID準拠の堅牢性
  - JSON型サポート
  - 高度なインデックス機能
  - オープンソース

### Webサーバー
- **Nginx**: リバースプロキシ & 静的ファイル配信

### コンテナ化
- **Docker**: コンテナ化
- **Docker Compose**: オーケストレーション

## 開発環境セットアップ

### 必須ツール
- Docker & Docker Compose
- Git
- （オプション）Node.js & npm（フロントエンド開発時）
- （オプション）Python 3.11+（API開発時）

### リポジトリクローン
```bash
git clone https://github.com/hibiki31/hinagiku-viewer.git
cd hinagiku-viewer
```

### 設定ファイル準備
```bash
# Docker Compose設定をコピー
cp docker-compose.example.yml compose.yaml

# API環境変数（必要に応じて）
cp api/.env.example api/.env
```

### データディレクトリ作成
```bash
mkdir -p data/{book_library,book_cache,book_send,book_export,book_fail,app_data,nginx,postgres_data}
```

### 起動
```bash
# ビルド & 起動
docker compose build
docker compose up -d

# ログ確認
docker compose logs -f

# 状態確認
docker compose ps
```

### データベースマイグレーション
```bash
# 初回のみ
docker compose exec api alembic upgrade head
```

### アクセス
- Webアプリ: http://localhost
- API ドキュメント: http://localhost/api

## 開発ワークフロー

### バックエンド開発（API）

#### ローカル開発（Dockerなし）
```bash
cd api

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# 開発サーバー起動（自動リロード）
python3 main.py
# または
python3 dev.py

# Worker起動
python3 worker.py
```

#### Docker開発
```bash
# API再ビルド
docker compose build api

# 再起動
docker compose restart api

# ログ確認
docker compose logs -f api
```

#### データベースマイグレーション
```bash
# マイグレーションファイル作成
docker compose exec api alembic revision --autogenerate -m "変更内容"

# 適用
docker compose exec api alembic upgrade head

# ロールバック
docker compose exec api alembic downgrade -1

# リセット（全削除）
docker compose exec api alembic downgrade base
```

#### テスト実行
```bash
cd api/tests

# 全テスト実行
python test.py

# 個別テスト
python test_01_startup.py
python test_02_library.py
python test_10_scenario.py
```

### フロントエンド開発（Web）

#### ローカル開発
```bash
cd web

# 依存関係インストール
npm install

# 開発サーバー起動
npm run serve
# → http://localhost:8080

# ビルド
npm run build

# リント
npm run lint
```

#### Docker開発
```bash
# Webサーバー再ビルド
docker compose build web

# 再起動
docker compose restart web
```

### 次世代フロントエンド開発（Nuxt/Vue3）

#### Nuxt 3（nuxt/）
```bash
cd nuxt

# 依存関係インストール
yarn install

# 開発サーバー起動
yarn dev
```

#### Vue 3 + Vite（vue/）
```bash
cd vue

# 依存関係インストール
pnpm install

# 開発サーバー起動
pnpm dev
```

## プロジェクト構造詳細

### API（api/）
```
api/
├── main.py                 # FastAPIアプリケーション
├── worker.py               # バックグラウンドワーカー
├── settings.py             # 環境設定
├── requirements.txt        # Python依存関係
├── Dockerfile              # コンテナイメージ定義
├── alembic.ini             # Alembicマイグレーション設定
├── alembic/
│   ├── env.py
│   └── versions/           # マイグレーションファイル
├── mixins/                 # 共通ユーティリティ
│   ├── database.py         # DB接続・セッション管理
│   ├── log.py              # ロガー設定
│   ├── schema.py           # 共通スキーマ
│   ├── convertor.py        # 画像変換・サムネイル生成
│   ├── purser.py           # ファイル名パース
│   ├── utility.py          # 汎用ユーティリティ
│   └── router.py           # ユーティリティAPI
├── books/                  # 書籍ドメイン
│   ├── models.py           # SQLAlchemyモデル
│   ├── schemas.py          # Pydanticスキーマ
│   └── router.py           # APIエンドポイント
├── users/                  # ユーザードメイン
├── authors/                # 著者ドメイン
├── tags/                   # タグドメイン
├── media/                  # メディア配信
├── user_datas/             # ユーザー固有データ
├── tasks/                  # バックグラウンドタスク
│   ├── library_import.py   # インポート処理
│   ├── library_export.py   # エクスポート処理
│   ├── library_delete.py   # 削除処理
│   ├── library_fixmetadata.py # メタデータ修正
│   ├── library_sim.py      # 重複チェック
│   ├── library_rule.py     # ルール適用
│   └── media_cache.py      # キャッシュ生成
└── tests/                  # テストコード
```

### Web（web/）
```
web/
├── src/
│   ├── main.js             # エントリーポイント
│   ├── App.vue             # ルートコンポーネント
│   ├── router/             # ルーティング設定
│   ├── store/              # Vuex ストア
│   ├── views/              # ページコンポーネント
│   ├── components/         # 再利用可能コンポーネント
│   ├── axios/              # API通信設定
│   ├── mixins/             # Vue mixins
│   └── plugins/            # プラグイン（Vuetify等）
├── public/                 # 静的ファイル
├── Dockerfile              # Nginxイメージ
├── nginx.conf              # Nginx設定
├── package.json            # npm依存関係
└── vue.config.js           # Vue CLI設定
```

## 環境変数

### API（api/.env）
```bash
# データベース接続
SQLALCHEMY_DATABASE_URL=postgresql://postgres:password@db:5432/mydatabase

# データディレクトリルート
DATA_ROOT=/opt/data

# アプリケーションルート
APP_ROOT=/opt/app

# 開発モード
IS_DEV=false

# デバッグログ
DEBUG_LOG=false

# Gunicorn ワーカー数
GNICORN_WORKERS=4

# 変換スレッド数（CPUコア数が推奨）
# CONVERT_THREAD=4

# JWT秘密鍵（本番環境では必ず変更）
SECRET_KEY=ランダムな文字列
```

### Docker Compose（compose.yaml）
```yaml
environment:
  SQLALCHEMY_DATABASE_URL: postgresql://user:pass@db:5432/dbname
  DATA_ROOT: /opt/data
  IS_DEV: "false"
```

## 技術的な制約

### Python
- バージョン: 3.11以上推奨
- 非同期処理: asyncio使用可能だが現状は同期処理中心

### データベース
- PostgreSQL 16推奨
- SQLAlchemy 2.0の新しいAPI使用
- Pydantic V2対応

### フロントエンド
- Vue 2はレガシー、Vue 3への移行検討中
- Vuetify 2（Vue 2用）→ Vuetify 3（Vue 3用）への移行必要

### ファイルシステム
- Zipファイル内の画像のみ対応
- ファイル名の長さ制限（OS依存）
- /tmp/hinav/を一時ディレクトリとして使用

### Docker
- マルチステージビルド使用
- アルパインベースではなく標準イメージ使用（ネイティブライブラリのため）

## 依存関係管理

### Python（api/）
```bash
# 依存関係の追加
pip install パッケージ名
pip freeze > requirements.txt

# パッケージ更新確認
pip install pip-review
pip-review

# 更新適用
pip-review --auto
```

### Node.js（web/）
```bash
# 依存関係の追加
npm install パッケージ名
npm install --save-dev パッケージ名

# 更新確認
npm outdated

# 更新
npm update
```

## パフォーマンスチューニング

### Gunicorn設定（api/mixins/gnicorn_config.py）
- Workers: CPU コア数 × 2 + 1
- Worker class: uvicorn.workers.UvicornWorker
- Timeout: 120秒

### PostgreSQL
- 接続プーリング: SQLAlchemyのデフォルト
- インデックス: 主キー、外部キー、検索頻度の高いカラム

### Nginx
- gzip圧縮有効化
- 静的ファイルキャッシュ
- リバースプロキシバッファリング

### Worker
- マルチプロセス: CONVERT_THREAD設定
- ポーリング間隔: 10秒

## セキュリティ対策

### 認証
- JWT + OAuth2 Password Flow
- bcryptでパスワードハッシュ化
- トークン有効期限管理

### CORS
- 開発環境: 全許可（`allow_origins=["*"]`）
- 本番環境: 必要なオリジンのみ許可推奨

### SQLインジェクション
- SQLAlchemy ORM使用で対策
- パラメータバインディング

### XSS
- Vueの自動エスケープ機能
- v-htmlの使用は最小限

### ファイルアップロード
- 拡張子チェック
- ファイルサイズ制限
- Zipファイルのみ許可

## トラブルシューティング

### よくあるエラー

#### OSError: [Errno 36] File name too long
- **原因**: Zipファイル内のファイル名が長すぎる
- **対処**: ファイル名を短縮するか、ファイルシステムの制限を確認

#### Alembicマイグレーションエラー
- **原因**: モデル定義とDB状態の不一致
- **対処**: 
  ```bash
  alembic downgrade base  # リセット
  alembic upgrade head    # 再適用
  ```

#### Docker起動エラー
- **原因**: ポート競合、ボリューム権限
- **対処**:
  ```bash
  docker compose down
  docker compose up -d
  docker compose logs
  ```

#### API接続エラー
- **原因**: CORS設定、JWT有効期限切れ
- **対処**: 
  - ブラウザコンソールで詳細確認
  - 再ログイン
  - CORS設定確認

## デバッグツール

### API
- FastAPI自動生成ドキュメント: `/api`
- ログファイル: `data/app_data/logs/`
- SQLAlchemy echo: `create_engine(..., echo=True)`

### フロントエンド
- Vue Devtools（ブラウザ拡張）
- ブラウザデベロッパーツール
- Vuex状態確認

### データベース
```bash
# PostgreSQLコンテナに接続
docker compose exec db psql -U postgres -d mydatabase

# テーブル一覧
\dt

# スキーマ確認
\d books

# クエリ実行
SELECT * FROM books LIMIT 10;
```

## CI/CD（現状）
- 現在は手動デプロイ
- GitHub Actionsの設定は未実装
- 将来的な自動化を検討

## モニタリング・ログ
- アプリケーションログ: `data/app_data/logs/`
- Nginxログ: `data/nginx/`
- PostgreSQLログ: Docker Composeログ経由
- メトリクス収集: 未実装（将来検討）

## バックアップ戦略
- データベース: `pg_dump`でバックアップ
- 書籍ファイル: `data/book_library/`をバックアップ
- 設定ファイル: Gitで管理
- Docker ボリューム: 定期バックアップ推奨
