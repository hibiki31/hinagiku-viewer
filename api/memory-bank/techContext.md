# Tech Context - API Module

> **親プロジェクト技術スタック**: `/workspace/memory-bank/techContext.md` を参照

## コア技術スタック

### FastAPI 0.116.1
- **役割**: Webフレームワーク、APIサーバー
- **理由**: 高速、型安全、OpenAPI自動生成
- **特徴**:
  - 非同期処理対応（async/await）
  - Pydanticによる自動バリデーション
  - 依存性注入システム
  - Swagger UI組み込み

### Python 3.11+
- **理由**: 型ヒント改善、パフォーマンス向上
- **必須バージョン**: 3.11以降

### PostgreSQL 16
- **役割**: メインデータベース
- **接続**: psycopg2 2.9.10
- **特徴**:
  - 複雑なリレーション管理
  - トランザクション保証
  - 全文検索機能

### SQLAlchemy 2.0.43
- **役割**: ORM（Object-Relational Mapping）
- **スタイル**: 2.0新スタイル（`Mapped`型アノテーション）
- **特徴**:
  - 型安全なクエリ
  - リレーションシップ管理
  - マイグレーション基盤

### Alembic 1.16.5
- **役割**: データベースマイグレーション管理
- **使用方法**:
  ```bash
  alembic revision --autogenerate -m "変更内容"
  alembic upgrade head
  alembic downgrade -1  # ロールバック
  ```

## 認証・セキュリティ

### PyJWT 2.8.0
- **役割**: JWT（JSON Web Token）生成・検証
- **用途**: ユーザー認証トークン

### passlib 1.7.4 + bcrypt 4.0.1
- **役割**: パスワードハッシュ化
- **アルゴリズム**: bcrypt

### OAuth2 Password Flow
- FastAPI標準実装
- Cookie経由でのトークン送信

## 画像処理

### Pillow 11.3.0
- **役割**: 基本的な画像処理
- **用途**: サムネイル生成、画像リサイズ

### OpenCV (opencv-contrib-python) 4.8.0.76
- **役割**: 高度な画像処理
- **用途**: 画像解析、変換

### ImageHash 4.3.1
- **役割**: 知覚的ハッシュ生成
- **用途**: 重複画像検出（aHash）

## データ処理

### pandas 2.0.3
- **役割**: データ分析・処理
- **用途**: CSV処理、データ変換

### matplotlib
- **役割**: グラフ生成
- **用途**: 統計情報の可視化（将来的な機能）

## テキスト処理

### rapidfuzz 3.6.1
- **役割**: 高速ファジー文字列マッチング
- **用途**: 類似タイトル検索、重複チェック

## Webサーバー

### Uvicorn 0.35.0
- **役割**: ASGIサーバー（開発用）
- **使用**: `python main.py`で起動
- **特徴**: ホットリロード対応

### Gunicorn 23.0.0
- **役割**: WSGIサーバー（本番用）
- **使用**: `gunicorn --config ./mixins/gnicorn_config.py`
- **設定**: `mixins/gnicorn_config.py`

## ユーティリティ

### httpx 0.24.1
- **役割**: 非同期HTTPクライアント
- **用途**: 外部API呼び出し

### python-multipart 0.0.20
- **役割**: マルチパートフォームデータ処理
- **用途**: ファイルアップロード

## 開発環境

### ディレクトリ構造
```
/workspace/api/
├── main.py              # エントリーポイント
├── settings.py          # 環境設定
├── worker.py            # バックグラウンドワーカー
├── requirements.txt     # 依存関係
├── alembic.ini         # Alembic設定
├── dev.py              # 開発用スクリプト
├── dev.sh              # 開発用シェル
├── Dockerfile          # Dockerイメージ
├── .env                # 環境変数
├── {domain}/           # ドメインモジュール
├── mixins/             # 共通ユーティリティ
├── tasks/              # バックグラウンドタスク
├── tests/              # テストコード
└── alembic/versions/   # マイグレーションファイル
```

### 環境変数（settings.py）
主要な設定項目:
- `DATABASE_URL` - PostgreSQL接続文字列
- `SECRET_KEY` - JWT署名キー
- `API_VERSION` - APIバージョン
- `MEDIA_PATH` - メディアファイルパス
- `CACHE_PATH` - キャッシュファイルパス

### Docker環境
- ベースイメージ: Python 3.11-slim
- ポート: 8000
- ボリューム: `/data` (メディアファイル)
- ネットワーク: docker-compose.yml定義

## 開発コマンド

### サーバー起動
```bash
# 開発（自動リロード）
python3 main.py

# 本番
gunicorn --config ./mixins/gnicorn_config.py
```

### データベース
```bash
# マイグレーション作成
alembic revision --autogenerate -m "変更内容"

# マイグレーション適用
alembic upgrade head

# ロールバック
alembic downgrade -1

# リセット
alembic downgrade base
```

### 依存関係管理
```bash
# インストール
pip install -r requirements.txt

# 更新確認
pip install pip-review
pip-review
```

## API仕様

### OpenAPI仕様
- エンドポイント: `/api/openapi.json`
- Swagger UI: `/api`
- ReDoc: `/api/redoc`

### フロントエンド型生成
```bash
# Vue 3フロントエンドで実行
npx openapi-typescript https://hinav.hinagiku.me/api/openapi.json -o ./src/api.d.ts
```

## パフォーマンス考慮

### キャッシュ戦略
- サムネイル画像のファイルシステムキャッシュ
- データベースクエリの最適化
- N+1問題対策（eager loading）

### 非同期処理
- FastAPIの非同期エンドポイント
- バックグラウンドワーカーによる重い処理の分離

## 技術的制約

### ファイル名長制限
- OSの制約: 255文字
- 対策: パス短縮、エラーハンドリング

### Zipファイル処理
- 対応: 画像ファイルのみ
- フォーマット: JPG, PNG, WebP等

### データベース依存
- PostgreSQL必須
- SQLite非対応（リレーション複雑度のため）

## テスト環境

### テストツール
- pytest（予定）
- テストデータ: `tests/dump/`

### テストシナリオ
- `test_01_startup.py` - 起動テスト
- `test_02_library.py` - ライブラリ機能
- `test_10_scenario.py` - シナリオテスト
- `test_index.py` - インデックス

## 今後の技術的展望

### 検討中の改善
- Redis導入（キャッシュ層）
- Celery導入（タスクキュー）
- ElasticSearch（全文検索強化）
- GraphQL（クエリ柔軟性）

### メンテナンス方針
- 依存関係の定期更新
- セキュリティパッチの適用
- Python最新バージョン追従
