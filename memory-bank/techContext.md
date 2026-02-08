# Tech Context

## 技術スタック

### バックエンド
- **言語**: Python 3.11+
- **Webフレームワーク**: FastAPI 0.116.1
- **ASGI Server**: Uvicorn 0.35.0（開発） / Gunicorn 23.0.0（本番）
- **ORM**: SQLAlchemy 2.0.43
- **マイグレーション**: Alembic 1.16.5
- **DBドライバ**: psycopg2 2.9.10
- **認証**: PyJWT 2.8.0 + passlib 1.7.4（bcrypt）
- **画像処理**: Pillow 11.3.0 + opencv-contrib-python 4.8.0.76 + imagehash 4.3.1
- **その他**: httpx 0.24.1, pandas 2.0.3, rapidfuzz 3.6.1, python-multipart 0.0.20

### フロントエンド（主力: vue/）

#### Vue 3 + Vite（vue/）— 主力
- **フレームワーク**: Vue 3.4+
- **ビルドツール**: Vite 5
- **UIフレームワーク**: Vuetify 3.6+
- **言語**: TypeScript 5.6
- **状態管理**: Pinia 2.1+
- **ルーティング**: Vue Router 4.4+（ファイルベース: unplugin-vue-router 0.10）
- **HTTP通信**: 
  - Axios 1.8+（現在のメインクライアント）
  - openapi-fetch 0.13+（型安全クライアント、移行先）
- **自動インポート**: unplugin-auto-import 0.17, unplugin-vue-components 0.27
- **レイアウト**: vite-plugin-vue-layouts 0.11
- **スタイル**: Sass 1.77（modern-compiler API）
- **通知**: @kyvg/vue3-notification 3.4
- **Cookie**: js-cookie 3.0
- **アイコン**: @mdi/font 7.4
- **パッケージマネージャー**: pnpm

#### Vue 2（web/）— レガシー本番
- **フレームワーク**: Vue.js 2.6.11
- **UIフレームワーク**: Vuetify 2.x
- **状態管理**: Vuex 3.4.0
- **ルーティング**: Vue Router 3.2.0
- **HTTP通信**: Axios 0.21.4
- **ビルドツール**: Vue CLI 4.5.0
- **パッケージマネージャー**: npm

#### Nuxt 3（nuxt/）— 移行実験（非推奨）
- Nuxt 3 + Vue 3 + Vuetify 3
- 今後は使用せず、vue/に注力

### データベース
- **RDBMS**: PostgreSQL 16

### Webサーバー
- **Nginx**: リバースプロキシ & 静的ファイル配信

### コンテナ化
- **Docker** + **Docker Compose**

## Vue 3フロントエンド詳細（vue/）

### プロジェクト構造
```
vue/
├── .devcontainer/          # DevContainer設定
│   ├── devcontainer.json
│   ├── Dockerfile
│   └── post.sh
├── .claude/                # Claude Code設定
├── src/
│   ├── main.ts             # エントリーポイント
│   ├── App.vue             # ルートコンポーネント（認証初期化、インターセプター）
│   ├── api.d.ts            # OpenAPI自動生成型定義
│   ├── auto-imports.d.ts   # 自動インポート型定義（生成）
│   ├── components.d.ts     # コンポーネント型定義（生成）
│   ├── typed-router.d.ts   # ルーター型定義（生成）
│   ├── pages/              # ファイルベースルーティング
│   │   ├── index.vue       # 書籍一覧
│   │   ├── login.vue       # ログイン
│   │   ├── duplicate.vue   # 重複管理
│   │   └── books/
│   │       └── [uuid].vue  # 書籍リーダー
│   ├── components/         # 再利用可能コンポーネント
│   │   ├── BooksListTable.vue
│   │   ├── BooksListThum.vue
│   │   ├── BaseAuthorChip.vue
│   │   ├── AppFooter.vue
│   │   └── dialog/
│   │       ├── SearchDialog.vue
│   │       ├── BookDetailDialog.vue
│   │       ├── RangeChangeDialog.vue
│   │       └── SetupDialog.vue
│   ├── composables/        # Composition API ユーティリティ
│   │   ├── utility.ts      # 通知、URL生成、フォーマット等
│   │   └── rules.ts        # バリデーションルール
│   ├── func/               # 関数・クライアント
│   │   ├── axios.ts        # Axiosインスタンス
│   │   ├── client.ts       # openapi-fetchクライアント
│   │   ├── auth.ts         # 認証ユーティリティ
│   │   └── sleep.ts        # スリープ関数
│   ├── stores/             # Pinia ストア
│   │   ├── index.ts
│   │   ├── userData.ts     # 認証状態
│   │   ├── readerState.ts  # 書籍一覧・リーダー状態
│   │   ├── auth.ts         # 認証設定
│   │   └── app.ts          # アプリ全般
│   ├── layouts/            # レイアウト
│   │   └── default.vue
│   ├── plugins/            # プラグイン
│   │   ├── index.ts
│   │   └── vuetify.ts      # Vuetify設定（テーマ等）
│   ├── router/             # ルーター
│   │   └── index.ts        # ガード設定
│   ├── styles/
│   │   └── settings.scss   # Vuetify SCSS設定
│   └── assets/             # 静的アセット
├── public/                 # 公開静的ファイル
├── index.html              # HTMLテンプレート
├── vite.config.mts         # Vite設定
├── tsconfig.json           # TypeScript設定
├── eslint.config.js        # ESLint設定
├── package.json            # 依存関係
├── pnpm-lock.yaml          # ロックファイル
├── CLAUDE.md               # Claude Code向けガイド
└── .env.local              # 環境変数（Git管理外）
```

### Vite設定（vite.config.mts）
- **プラグイン**: VueRouter（ファイルベース）, Layouts, AutoImport, Components, Vue, Vuetify, Fonts
- **エイリアス**: `@` → `src/`
- **開発サーバー**: ポート3000
- **SCSS**: modern-compiler API

### 環境変数
```bash
# .env.local
VITE_APP_API_HOST=http://localhost   # Axiosクライアント用
VITE_API_ENDPOINT=http://localhost   # openapi-fetchクライアント用
```

### API型生成
```bash
npx openapi-typescript https://hinav.hinagiku.me/api/openapi.json -o ./src/api.d.ts
```
生成された`api.d.ts`は`paths`（エンドポイント）と`components`（スキーマ）をエクスポート。
使用例: `type BookBase = components['schemas']['BookBase']`

### 主要なPiniaストア設計

#### userData（認証）
```typescript
state: { isLoaded, isAuthed, accessToken, username, isAdmin }
actions: authenticaitonSuccessful(token), authenticaitonFail(), authVerification()
```
- accessTokenはCookieに保存（有効期限365日）
- ログイン成功時にaxiosデフォルトヘッダーに設定

#### readerState（書籍一覧・リーダー）
```typescript
state: { booksList, booksCount, readerPage, showListMode, openBook, searchQuery }
actions: setBooksResult(), setSearchQuery(), setOpenBook(), setShowListMode(), serachBooks()
```
- searchQueryはlocalStorageに永続化
- 初期化時にlocalStorageから復元

## 開発環境セットアップ

### DevContainer（推奨）
vue/ディレクトリ内の`.devcontainer/`に設定済み:
- Node.js環境
- pnpmプリインストール
- ポート3000フォワード
- Claude Code拡張
- Volar, ESLint, Prettier等のVS Code拡張

### 開発コマンド
```bash
cd vue/
pnpm install          # 依存関係インストール
pnpm dev              # 開発サーバー（http://localhost:3000）
pnpm build            # ビルド（型チェック + Viteビルド並列）
pnpm build-only       # Viteビルドのみ
pnpm type-check       # vue-tsc --build --force
pnpm lint             # ESLint --fix
```

### バックエンド開発
```bash
cd api/
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 main.py       # 開発サーバー
python3 worker.py     # Worker起動
```

### Docker開発
```bash
cp docker-compose.example.yml compose.yaml
docker compose build
docker compose up -d
docker compose exec api alembic upgrade head  # 初回マイグレーション
```

## API構造（api/）
```
api/
├── main.py                 # FastAPIアプリ
├── worker.py               # バックグラウンドワーカー
├── settings.py             # 環境設定
├── requirements.txt        # Python依存関係
├── alembic/                # DBマイグレーション
├── mixins/                 # 共通ユーティリティ
│   ├── database.py         # DB接続・セッション
│   ├── log.py              # ロガー設定
│   ├── schema.py           # 共通スキーマ（CamelCase変換）
│   ├── convertor.py        # 画像変換・サムネイル
│   ├── purser.py           # ファイル名パース
│   └── router.py           # ユーティリティAPI
├── books/                  # 書籍ドメイン
├── users/                  # ユーザードメイン
├── authors/                # 著者ドメイン
├── tags/                   # タグドメイン
├── media/                  # メディア配信
├── user_datas/             # ユーザー固有データ
├── tasks/                  # バックグラウンドタスク
└── tests/                  # テスト
```

## 環境変数

### API（api/.env）
| 変数 | 説明 | デフォルト |
|------|------|-----------|
| SQLALCHEMY_DATABASE_URL | DB接続文字列 | postgresql://postgres:password@db:5432/mydatabase |
| DATA_ROOT | データディレクトリ | /opt/data |
| APP_ROOT | アプリルート | /opt/app |
| IS_DEV | 開発モード | false |
| DEBUG_LOG | デバッグログ | false |
| GNICORN_WORKERS | Gunicornワーカー数 | 4 |
| CONVERT_THREAD | 変換スレッド数 | CPUコア数 |
| SECRET_KEY | JWT秘密鍵 | （要変更） |

### Vue 3（vue/.env.local）
| 変数 | 説明 |
|------|------|
| VITE_APP_API_HOST | APIホスト（Axiosクライアント用） |
| VITE_API_ENDPOINT | APIエンドポイント（openapi-fetchクライアント用） |

## ポート使用状況
| ポート | サービス | 用途 |
|--------|----------|------|
| 80 | Nginx | 外部公開（本番） |
| 3000 | Vite | Vue 3開発サーバー |
| 8000 | FastAPI | APIサーバー（内部） |
| 8080 | Vue CLI | Vue 2開発サーバー |
| 5432 | PostgreSQL | データベース（内部） |

## トラブルシューティング

### よくあるエラー

| エラー | 原因 | 対処 |
|--------|------|------|
| OSError: [Errno 36] | ファイル名長すぎ | ファイル名短縮 or パス制限確認 |
| Alembicマイグレーションエラー | モデルとDB不一致 | `alembic downgrade base` → `alembic upgrade head` |
| Docker起動エラー | ポート競合/権限 | `docker compose down` → `docker compose up -d` → ログ確認 |
| 401エラー | JWT期限切れ | 再ログイン / CORS設定確認 |
| Vite HMRエラー | 動的インポート失敗 | ページリロード（router.onErrorで自動リトライ済み） |

### デバッグツール
- **API**: FastAPI自動ドキュメント `/api`、ログファイル `data/app_data/logs/`
- **フロントエンド**: Vue Devtools、ブラウザDevTools
- **DB**: `docker compose exec db psql -U postgres -d mydatabase`

## 最終更新日
2026-02-08: Vue 3フロントエンド詳細追加、構造整理
