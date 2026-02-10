# System Patterns - API Module

## アーキテクチャ
- **ドメイン分割**: 各ドメインが `models.py` + `router.py` + `schemas.py` を持つ
- **Mixinパターン**: `mixins/` に共通機能集約（database, log, convertor, parser, schema, utility等）
- **依存性注入**: `Depends(get_db)`, `Depends(get_current_user)`
- **レイヤード**: Router層 → ビジネスロジック → SQLAlchemy ORM → PostgreSQL

## スキーマパターン

### BaseSchema（推奨）
```python
from mixins.schema import BaseSchema  # alias_generator=to_camel, from_attributes=True, populate_by_name=True

class BookSearchParams(BaseSchema):
    file_name_like: str | None = None  # → API: fileNameLike
    library_id: int = 1                # → API: libraryId
```

### クエリパラメータはPydanticクラスで定義
```python
@app.get("/api/books")
async def list_books(db: Session = Depends(get_db), params: BookSearchParams = Depends()):
    ...
```

## 認証パターン
- POST `/api/auth` → JWT発行 → Cookie送信
- 以降のリクエスト: Cookie自動送信 → JWT検証 → ユーザー情報取得
- トークン有効期限: 30日（`ACCESS_TOKEN_EXPIRE_MINUTES`）

## タスクパターン
- `worker.py`: 無限ループでポーリング（10秒間隔）
- タスク種別: import, export, delete, fixmetadata, sim, rule, cache
- 並列度: `CONVERT_THREAD`（CPUコア数）

## エラーハンドリング
- ファイル名長制限: OSError発生時キャッチしてスキップ
- タイポ維持: `authenticaitonSuccessful`/`authenticaitonFail`（互換性）
- DBタイポ: `chached`/`is_shered` — マイグレーション作成済み（20260210）

## 設計原則
1. シンプルさ優先（過度な抽象化を避ける）
2. 型安全性（Pydantic + 型ヒント必須）
3. Python側snake_case / API側camelCase（BaseSchema自動変換）
4. ログは日本語統一
