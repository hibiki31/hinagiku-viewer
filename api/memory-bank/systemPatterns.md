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

## タスクパターン（バックグラウンド処理）

### タスク実装の基本フロー
1. **タスクファイル作成**: `tasks/task_name.py` に `main(db, task_id=None)` 関数を実装
2. **進捗管理**: `tasks.utility.update_task_status()` で進捗・ステータス更新
3. **スキーマ追加**: `books/schemas.py` の `LibraryPatchEnum` にタスク種別を追加
4. **ルーター登録**: `media/router.py` の `patch_media_library()` にタスク起動処理を追加
5. **Worker登録**: `worker.py` にタスク実行処理を追加

### タスク実装例（参考: `tasks/library_integrity_check.py`）
```python
from tasks.utility import update_task_status

def main(db: Session, task_id: Optional[str] = None):
    try:
        if task_id:
            update_task_status(db, task_id, status="running", progress=0, message="処理開始")
        
        # メイン処理
        for idx, item in enumerate(items):
            # 処理...
            if task_id:
                progress = int((idx / total) * 100)
                update_task_status(db, task_id, progress=progress, current_item=idx, message=f"{idx}/{total}完了")
        
        if task_id:
            update_task_status(db, task_id, status="completed", progress=100, message="完了")
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)
        if task_id:
            update_task_status(db, task_id, status="failed", error_message=str(e))
        raise
```

### タスク起動（サブプロセス）
```python
# media/router.py
from uuid import uuid4
from tasks.utility import create_task

task_id = str(uuid4())
create_task(db=db, task_id=task_id, task_type="task_name", user_id=current_user.id)
library_pool.append(subprocess.Popen(["python3", f"{APP_ROOT}/worker.py", "task_name", task_id]))
```

### Worker登録
```python
# worker.py
from tasks.task_name import main as task_task_name

if args[1] == "task_name":
    task_id = args[2] if len(args) > 2 else None
    logger.info(f'ワーカでタスク開始 (task_id={task_id})')
    task_task_name(db=db, task_id=task_id)
    logger.info('ワーカでタスク完了')
```

### 既存タスク
- `load`: ライブラリ追加、`export`: エクスポート、`sim_all`: 重複検索
- `thumbnail_recreate`: サムネイル再作成、`integrity_check`: 整合性確認
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
