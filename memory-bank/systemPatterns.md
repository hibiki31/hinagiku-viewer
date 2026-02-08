# System Patterns

## システムアーキテクチャ

### 全体構成
```
┌─────────────────────────────────────────┐
│           ユーザー（ブラウザ）          │
└────────────────┬────────────────────────┘
                 │ HTTP/HTTPS (Port 80)
┌────────────────▼────────────────────────┐
│           Nginx（Webサーバー）          │
│  - 静的ファイル配信（Vue.jsアプリ）     │
│  - APIリバースプロキシ (/api → API)     │
└─────────┬──────────────┬────────────────┘
          │              │
          │              │ プロキシ
┌─────────▼─────┐  ┌────▼──────────────────┐
│  静的ファイル  │  │   FastAPI（API）      │
│  (Vue.js SPA)  │  │   - RESTful API       │
└────────────────┘  │   - JWT認証           │
                    │   - データベース操作   │
                    └──────┬────────────────┘
                           │
                    ┌──────▼────────────────┐
                    │  Worker（バックグラウンド）│
                    │  - タスクキュー処理    │
                    │  - ファイルインポート  │
                    │  - ハッシュ計算        │
                    │  - キャッシュ生成      │
                    └──────┬────────────────┘
                           │
                    ┌──────▼────────────────┐
                    │   PostgreSQL（DB）     │
                    │  - メタデータ保存      │
                    │  - ユーザー情報        │
                    │  - タスクキュー        │
                    └───────────────────────┘
```

### マイクロサービス構成

#### 1. Webサーバー（Nginx）
- **役割**: フロントエンドの配信とAPIリバースプロキシ
- **技術**: Nginx
- **ポート**: 80（外部公開）
- **設定**:
  - 静的ファイルを/usr/share/nginx/htmlから配信
  - /api/*をAPIサーバーにプロキシ
  - ログを/var/log/nginx/に出力

#### 2. APIサーバー（FastAPI）
- **役割**: RESTful APIの提供
- **技術**: FastAPI + Uvicorn/Gunicorn
- **ポート**: 8000（内部のみ）
- **責務**:
  - 認証・認可
  - CRUD操作
  - データバリデーション
  - データベースクエリ

#### 3. Workerサーバー
- **役割**: バックグラウンドタスクの処理
- **技術**: Python マルチプロセス
- **実行**: worker.py
- **責務**:
  - ファイル監視・インポート
  - ハッシュ計算
  - サムネイル生成
  - 重複チェック
  - エクスポート処理

#### 4. データベース（PostgreSQL）
- **役割**: 永続化層
- **技術**: PostgreSQL 16
- **ポート**: 5432（内部のみ）
- **データ**:
  - 書籍メタデータ
  - ユーザー情報
  - タスクキュー
  - マスタデータ

## データベース設計パターン

### エンティティ関係図（主要テーブル）

```
Users ──┬──< Books (user_id)
        └──< Libraries (user_id)

Libraries ──< Books (library_id)
          ──>< Users (library_to_user) ※共有

Books ──>< Tags (tag_to_book)
      ──>< Authors (book_to_author)
      ──< Genres (genre_id)
      ──< Publishers (publisher_id)
      ──< Series (series_id)
      ──< BookUserMetadata (book_uuid, user_id)

Books ──>< Books (duplication) ※重複関係
```

### テーブル設計パターン

#### 1. マスタテーブル（Master Tables）
- `authors`: 著者マスタ
- `tags`: タグマスタ
- `genres`: ジャンルマスタ
- `publishers`: 出版社マスタ
- `series`: シリーズマスタ

**パターン**: 正規化、UNIQUE制約で重複防止

#### 2. メインテーブル（Main Tables）
- `books`: 書籍の中心テーブル
  - UUID主キー
  - ハードメタデータ（ファイル情報）
  - ソフトメタデータ（編集可能）
  - 状態フラグ

#### 3. 中間テーブル（Junction Tables）
- `tag_to_book`: 書籍とタグの多対多
- `book_to_author`: 書籍と著者の多対多
- `library_to_user`: ライブラリとユーザーの多対多

#### 4. ユーザーデータテーブル
- `book_metadatas`: ユーザー固有の書籍データ
  - 複合主キー（user_id, book_uuid）
  - 閲覧履歴、評価等

#### 5. 関係テーブル
- `duplication`: 書籍間の重複関係
  - 複合主キー（book_uuid_1, book_uuid_2）
  - スコア保存

### データベースアクセスパターン

#### SQLAlchemy ORM使用
```python
# mixins/database.pyで定義
from sqlalchemy.orm import declarative_base

Base = declarative_base()
Engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=Engine)
```

#### リレーションシップのLazy Loading戦略
- デフォルト: `lazy=False`（Eager Loading）
  - 理由: N+1問題を回避、レスポンス速度優先
- 例外: 大量データの場合は`lazy=True`

## APIアーキテクチャパターン

### ルーター分割
各ドメインごとにルーターを分割：
- `users.router`: 認証・ユーザー管理
- `books.router`: 書籍CRUD
- `authors.router`: 著者管理
- `tags.router`: タグ管理
- `media.router`: メディアファイル配信
- `user_datas.router`: ユーザー固有データ
- `mixins.router`: ユーティリティAPI

### RESTful設計原則
```
GET    /api/books          # 一覧取得
GET    /api/books/{uuid}   # 詳細取得
POST   /api/books          # 新規作成
PUT    /api/books          # 更新（複数対応）
DELETE /api/books/{uuid}   # 削除
PATCH  /api/books          # 部分更新
```

### レスポンススキーマ統一
Pydanticスキーマで型安全性確保：
- `BaseSchema`: 共通基底クラス（mixins/schema.py）
- CamelCase ↔ snake_case自動変換
- バリデーション自動実行

### 認証パターン
```python
# JWT + OAuth2 Password Flow
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# 依存性注入でユーザー取得
def get_current_user(token: str = Depends(oauth2_scheme)):
    # トークン検証
    # ユーザー取得
    return user
```

## ファイル処理パターン

### ディレクトリ構造（データ）
```
/opt/data/
├── book_library/      # インポート済み書籍（永続保存）
├── book_cache/        # サムネイルキャッシュ
├── book_send/         # インポート監視フォルダ
├── book_export/       # エクスポート先
├── book_fail/         # 失敗したファイル
└── app_data/          # ログ・DB等
```

### ファイルインポートフロー
```python
# tasks/library_import.py
1. book_send/からZipファイル検出
2. Zipファイル解析（画像ファイル抽出）
3. SHA1ハッシュ計算
4. 重複チェック
5. book_library/にコピー
6. サムネイル生成 → book_cache/
7. DBに登録
8. book_send/から削除
9. エラー時 → book_fail/に移動
```

### サムネイル生成パターン
```python
# mixins/convertor.py
def make_thum(zip_path, uuid):
    # Zipから最初の画像抽出
    # /tmp/hinav/に一時展開
    # Pillow/OpenCVでリサイズ
    # book_cache/{uuid}/に保存
    # 高さ指定で複数サイズ対応
```

## タスクキューパターン

### ワーカープロセス設計
```python
# worker.py
while True:
    # タスク種別ごとに処理
    library_import.main(db)      # インポート
    library_export.main(db)      # エクスポート
    library_fixmetadata.main(db) # メタデータ修正
    library_sim.main(db)         # 重複チェック
    library_delete.main(db)      # 削除
    media_cache.main(db)         # キャッシュ生成
    
    time.sleep(10)  # ポーリング間隔
```

### タスク状態管理
- `BookModel.state`: 処理状態
  - 例: "importing", "processing", "completed", "error"
- データベースベースのキュー
- マルチプロセス対応（CONVERT_THREAD設定）

## ログパターン

### ログ設定（mixins/log.py）
```python
def setup_logger(name):
    # 標準出力 + ファイル出力
    # フォーマット: [時刻] [レベル] [モジュール] メッセージ
    # 日本語メッセージ統一
    # DEBUGレベルは環境変数で制御
```

### ログレベル使い分け
- **DEBUG**: 詳細な処理フロー（開発時のみ）
- **INFO**: 通常の処理開始・終了
- **WARNING**: 注意が必要だが継続可能
- **ERROR**: エラー発生、処理失敗
- **CRITICAL**: システム全体に影響する重大エラー

### Workerログの特殊ルール
- 対象不存在でスキップする場合は出力しない
  - 理由: ループで大量出力を避ける

## セキュリティパターン

### パスワード管理
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ハッシュ化
hashed = pwd_context.hash(password)
# 検証
pwd_context.verify(plain_password, hashed_password)
```

### JWT発行
```python
from jose import jwt

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

### CORS設定
```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発環境用、本番は制限推奨
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## フロントエンド設計パターン

### Vue 3アーキテクチャ（vue/）— 主力

#### ファイルベースルーティング
`unplugin-vue-router`により`src/pages/`配下の`.vue`ファイルからルートを自動生成:
```
src/pages/
├── index.vue           → /          （書籍一覧）
├── login.vue           → /login     （ログイン）
├── duplicate.vue       → /duplicate （重複管理）
└── books/
    └── [uuid].vue      → /books/:uuid（書籍リーダー）
```

#### レイアウトシステム
`vite-plugin-vue-layouts`で`src/layouts/`のレイアウトを適用。デフォルトレイアウト`default.vue`。

#### コンポーネント設計パターン
- `<script setup lang="ts">` + Composition API
- Vue API自動インポート（`ref`, `computed`, `watch`等）
- Vuetify/カスタムコンポーネント自動インポート
- ダイアログは`ref`で参照し`openDialog()`メソッドで開く

```typescript
// ダイアログパターン例
const searchDialogRef = ref()
// テンプレートから: searchDialogRef?.openDialog()
```

#### 状態管理（Pinia）
```
stores/
├── userData.ts     # 認証（Cookie永続化）
├── readerState.ts  # 書籍一覧・リーダー（localStorage永続化）
├── auth.ts         # 認証設定
└── app.ts          # アプリ全般
```

**認証ストア（userData）パターン:**
- Cookie `accessToken` でセッション管理
- `authenticaitonSuccessful()`: Cookie設定 + axiosヘッダー設定
- `authenticaitonFail()`: Cookie削除 + ヘッダー削除

**リーダーストア（readerState）パターン:**
- `searchQuery`をlocalStorageに自動永続化
- 初期化時にlocalStorageから復元
- `serachBooks()`でAPI呼び出し + 結果格納

#### API通信パターン（2クライアント共存）

**Axiosクライアント（現在のメイン）:**
```typescript
// func/axios.ts
const api = axios.create({
  baseURL: import.meta.env.VITE_APP_API_HOST || '',
})
// App.vueでインターセプター設定（401→自動ログアウト）
```

**openapi-fetchクライアント（型安全・移行先）:**
```typescript
// func/client.ts
const client = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_ENDPOINT,
})
// Bearerトークンミドルウェア付き
```

**移行方針**: 新規コードはopenapi-fetchを優先。既存Axiosは段階的に移行。

#### 認証フロー
```
App.vue mount
  ├─ Cookie "accessToken" 確認
  │   ├─ あり → GET /api/auth/validate
  │   │          ├─ 成功 → authenticaitonSuccessful()
  │   │          │         ├─ /login にいる → / にリダイレクト
  │   │          │         └─ それ以外 → そのまま
  │   │          └─ 失敗 → authenticaitonFail()
  │   └─ なし → authenticaitonFail()
  └─ バージョンチェック → GET /api/version → 不一致で自動リロード
```

#### ルーターガード
```
beforeEach:
  ├─ 認証済み + /login → / にリダイレクト
  ├─ 未認証 + /login以外 → /login にリダイレクト
  └─ その他 → 通過
```

#### 書籍リーダーの先読みパターン
```
onMounted → getDLoadingPage()
  ├─ 現在ページから cachePage 分先まで確認
  ├─ 未ロードページを発見 → Blobとして取得
  ├─ mulchLoad（並列数）まで同時リクエスト
  ├─ 成功 → URL.createObjectURL() で img src に設定
  ├─ 失敗 → 1秒後にリトライ
  └─ 設定はlocalStorage "readerSettings" に永続化
```

#### 通知パターン
```typescript
// @kyvg/vue3-notification + Vuetify v-alert
const { pushNotice } = usePushNotice()
pushNotice('メッセージ', 'success')  // type: 'success'|'error'|'info'|'warn'
```

### Vue 2アーキテクチャ（web/）— レガシー
```
src/
├── main.js           # エントリーポイント
├── App.vue           # ルートコンポーネント
├── router/           # Vue Router設定
├── store/            # Vuex状態管理
├── views/            # ページコンポーネント
├── components/       # 再利用可能コンポーネント
├── axios/            # API通信設定
└── plugins/          # Vuetify等のプラグイン
```
※ Vue 2は旧本番環境。Vue 3（vue/）への移行で置き換え予定。

## デプロイパターン

### Docker Compose構成
```yaml
services:
  api:      # FastAPIアプリケーション
  web:      # Nginx + Vue.js
  db:       # PostgreSQL
  # worker: api serviceと同じイメージでworker.py実行
```

### ボリュームマウント戦略
- コード: ビルド時にコピー（本番）
- データ: ボリュームマウント（永続化）
- ログ: ボリュームマウント（デバッグ用）

### 環境変数管理
- `.env`ファイル
- `docker-compose.yml`のenvironment
- `settings.py`で一元管理

## 設計上の重要な決定

### 1. 単一ポート公開
**決定**: NginxでフロントエンドとAPIを統合、ポート80のみ公開
**理由**: 
- ファイアウォール設定簡素化
- CORS問題の回避
- デプロイの簡素化

### 2. UUIDベース主キー（Books）
**決定**: 書籍IDに自動生成UUIDを使用
**理由**: 
- 分散環境での衝突回避
- ファイル名との関連付け
- セキュリティ（推測不可）

### 3. Eager Loading優先
**決定**: SQLAlchemyのリレーションシップでlazy=False
**理由**: 
- N+1問題の回避
- API レスポンス速度優先
- 書籍データは関連情報込みで返すことが多い

### 4. タスクキュー方式
**決定**: データベースベースのタスクキュー
**理由**: 
- 追加ミドルウェア不要（RabbitMQ, Celery等）
- シンプルな構成
- 小規模用途には十分

### 5. ログの日本語統一
**決定**: ログメッセージは日本語で記述
**理由**: 
- 主要ユーザーが日本語話者
- デバッグ効率向上
- コミットメッセージも日本語統一

## パフォーマンス最適化パターン

### 1. キャッシュ戦略
- サムネイル画像のファイルシステムキャッシュ
- `chached`フラグで生成済み判定

### 2. マルチプロセス処理
- Workerは`CONVERT_THREAD`設定で並列度調整
- デフォルト: CPU コア数

### 3. データベースインデックス
- `books.uuid`: PRIMARY KEY
- `books.user_id`: FOREIGN KEY (INDEX自動)
- `books.sha1`: 重複チェック高速化

### 4. ページネーション
- 書籍一覧はlimit/offsetでページング
- 大量データでもメモリ効率的
