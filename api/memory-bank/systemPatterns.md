# System Patterns - API Module

> **親プロジェクトパターン**: `/workspace/memory-bank/systemPatterns.md` を参照

## アーキテクチャパターン

### 1. ルーターベース設計
各ドメインが独立したルーターモジュールを持つ：

```
books/
  ├── models.py      # SQLAlchemyモデル
  ├── router.py      # FastAPIルーター
  └── schemas.py     # Pydanticスキーマ

users/
  ├── models.py
  ├── router.py
  └── schemas.py
```

**パターン**: ドメイン駆動設計の簡易版。各機能領域が独立。

### 2. Mixinパターン
共通機能を `mixins/` に集約：

- `database.py` - DBセッション管理
- `log.py` - ロガー設定
- `convertor.py` - 画像変換・サムネイル生成
- `purser.py` - Zipファイルパース
- `utility.py` - ユーティリティ関数
- `router.py` - 共通ルーター（ヘルスチェック等）
- `file_server.py` - ファイル配信
- `fastapi_file.py` - FastAPIファイル応答

### 3. レイヤードアーキテクチャ

```
Router層（router.py）
  ↓ HTTPリクエスト処理
  ↓ 認証・バリデーション
ビジネスロジック層
  ↓ データ操作ロジック
  ↓ ドメインルール適用
データアクセス層（models.py）
  ↓ SQLAlchemy ORM
データベース層（PostgreSQL）
```

### 4. 依存性注入パターン
FastAPIの`Depends`を使用：

```python
from mixins.database import get_db

@app.get("/books")
def get_books(db: Session = Depends(get_db)):
    # dbセッションが自動注入される
```

### 5. マイグレーション管理
Alembicによるバージョン管理：

```
alembic/versions/
  ├── 20211224_*.py  # 初期マイグレーション
  ├── 20220108_*.py
  ├── 20230822_*.py  # cached_status追加
  ├── 20230929_*.py  # ahash追加
  ├── 20230929_*.py  # duplication_table追加
  ├── 20230930_*.py  # on_delete修正
  ├── 20240105_*.py  # is_favorite追加
  └── 20250830_*.py  # テーブル名変更
```

**重要ルール**: データベース変更は必ずマイグレーションファイル作成

## データモデルパターン

### リレーションシップ設計

```
User (1) ─┬─ (N) Book
          └─ (N) Library

Book (N) ─── (N) Author    # 多対多
Book (N) ─── (N) Tag       # 多対多
Book (N) ─── (1) Publisher
Book (N) ─── (1) Series

Book (1) ─── (1) UserBookData  # ユーザー固有データ
```

### SQLAlchemy 2.0スタイル
- 新しい`Mapped`型アノテーション使用
- `relationship()`による明示的リレーション定義
- `Session.execute(select())`パターン

## タスクパターン

### バックグラウンドワーカー
`worker.py`が無限ループでタスクをポーリング：

```python
# tasks/library_import.py
def main(task_id: str):
    # タスク実行
    # データベース更新
    # ステータス更新
```

**タスク種類**:
- `library_import` - Zipファイルインポート
- `library_export` - 書籍エクスポート
- `library_delete` - 書籍削除
- `library_fixmetadata` - メタデータ修正
- `library_sim` - 重複チェック
- `media_cache` - キャッシュ生成

## 認証パターン

### OAuth2 Password Flow + JWT
1. POST `/api/auth` → `username` + `password`
2. JWT生成 → Cookie設定
3. 以降のリクエスト → Cookie自動送信
4. JWT検証 → ユーザー情報取得

### スコープベース権限
- `library:read` - ライブラリ読み取り
- `library:write` - ライブラリ書き込み
- 今後の拡張可能性を考慮

## ログパターン

### 日本語統一ルール
```python
from mixins.log import setup_logger

logger = setup_logger(__name__)
logger.info("書籍をインポートしました")
logger.error("ファイルの読み込みに失敗しました")
```

### Workerログ特殊ルール
- 対象不存在でスキップする場合：ログ出力しない
- エラー時：必ずログ出力

## エラーハンドリングパターン

### 既知のエラー対策

#### OSError: File name too long
- Zip内のパスが長すぎる場合
- 一時ディレクトリ展開時に発生
- 現状：キャッチして処理スキップ
- 対策：パス短縮処理の検討

#### タイポの継続使用
- `authenticaitonSuccessful` / `authenticaitonFail`
- 正しくは`authentication`だが既存コード全体で使用中
- **変更しない方針**（互換性維持）

## 設計原則

1. **シンプルさ優先**: 過度な抽象化を避ける
2. **型安全性**: Pydanticスキーマで入出力を保証
3. **分離**: ルーター/ビジネスロジック/データアクセスの分離
4. **テスタビリティ**: `tests/`ディレクトリで自動テスト
5. **ドキュメント**: OpenAPI自動生成 + Swagger UI
