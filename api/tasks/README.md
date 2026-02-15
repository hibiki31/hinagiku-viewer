# Tasks モジュール - コーディング規約

## 概要

- **実行**: FastAPIが `subprocess.Popen` で `worker.py` を起動
- **進捗管理**: `tasks.utility.update_task_status()` でDB更新

## 基本構造

```python
from typing import Optional
from sqlalchemy.orm import Session
from mixins.log import setup_logger
from tasks.utility import update_task_status

logger = setup_logger(__name__)

def main(db: Session, task_id: Optional[str] = None, **params):
    """タスクの説明"""
    try:
        # 初期化
        if task_id:
            update_task_status(db, task_id, status="running", progress=0, message="初期化中")

        # 対象取得
        items = db.query(Model).all()
        total = len(items)

        if total == 0:
            if task_id:
                update_task_status(db, task_id, status="completed", progress=100, message="対象なし")
            return

        if task_id:
            update_task_status(db, task_id, progress=5, total_items=total)

        # 処理ループ
        success_count = error_count = skip_count = 0
        for idx, item in enumerate(items, 1):
            try:
                # 処理
                success_count += 1
            except Exception as e:
                logger.error(f"[{idx}/{total}] エラー: {e}")
                error_count += 1

            # 進捗更新（定期）
            if task_id and (idx % min(100, max(1, total // 100)) == 0 or idx == total):
                progress = 5 + int((idx / total) * 90)
                update_task_status(db, task_id, progress=progress, current_item=idx)

        db.commit()

        # 完了
        if task_id:
            update_task_status(
                db, task_id, status="completed", progress=100,
                message=f"完了: 成功{success_count}件/エラー{error_count}件/スキップ{skip_count}件"
            )

    except Exception as e:
        logger.error(f"タスクエラー: {e}", exc_info=True)
        if task_id:
            update_task_status(db, task_id, status="failed", error_message=str(e))
        raise
```

## update_task_status

```python
update_task_status(
    db: Session,
    task_id: str,
    status: Optional[str] = None,          # "running"|"completed"|"failed"
    progress: Optional[int] = None,        # 0-100
    current_step: Optional[str] = None,    # ステップ名
    current_item: Optional[int] = None,    # 現在の処理番号
    total_items: Optional[int] = None,     # 総数（初回のみ設定）
    message: Optional[str] = None,         # ユーザー向けメッセージ
    error_message: Optional[str] = None    # エラー時
)
```

### 呼び出しパターン

```python
# 開始
update_task_status(db, task_id, status="running", progress=0, message="初期化中")

# 進捗
update_task_status(db, task_id, progress=50, current_item=500)

# 完了（結果を分類して明記）
update_task_status(db, task_id, status="completed", progress=100,
    message=f"完了: 成功{success}件/エラー{error}件/スキップ{skip}件")

# 失敗
update_task_status(db, task_id, status="failed", error_message=str(e))
```

## 完了メッセージフォーマット

**必須**: 結果を分類して記載

```python
# ✅ 良い
message=f"完了: 成功{success_count}件/エラー{error_count}件/スキップ{skip_count}件"
message=f"完了: ロスト{missing}件/重複{duplicate}件/修復{normal}件"

# ❌ 悪い
message="処理が完了しました"  # 結果が不明
```

## 進捗管理

### 更新頻度

```python
# 1%刻み または 100件ごと
update_interval = min(100, max(1, total // 100))

if idx % update_interval == 0 or idx == total:
    progress = 5 + int((idx / total) * 90)
    update_task_status(db, task_id, progress=progress, current_item=idx)
```

### 複数フェーズの場合

```python
# フェーズ1: ハッシュ計算 (5-30%)
update_task_status(db, task_id, progress=5, current_step="ハッシュ計算中")
# ... 処理 ...
update_task_status(db, task_id, progress=30)

# フェーズ2: 候補抽出 (30-60%)
update_task_status(db, task_id, progress=40, current_step="候補抽出中")
# ... 処理 ...
```

## エラーハンドリング

```python
# タスク全体
try:
    # 処理
except Exception as e:
    logger.error(f"タスクエラー: {e}", exc_info=True)
    if task_id:
        update_task_status(db, task_id, status="failed", error_message=str(e))
    raise  # 重要: workerに通知

# アイテム個別（続行）
for item in items:
    try:
        process(item)
    except Exception as e:
        logger.error(f"処理エラー {item.id}: {e}")
        error_count += 1
        # continue
```

## ログ出力規約

```python
# ✅ 日本語、情報豊富
logger.info("処理開始: 対象書籍数 1000")
logger.warning(f"[{idx}/{total}] 重複登録（ファイル欠損）: {uuid}")
logger.error(f"ハッシュ計算エラー {uuid}: {e}")

# ❌ 英語、情報不足
logger.info("Starting")
```

### スキップ時はログ出力しない

```python
# ✅ スキップ時はログなし
for item in items:
    if not should_process(item):
        skip_count += 1
        continue  # ログなし
    logger.info(f"処理完了: {item.id}")

# ❌ 大量ログ発生
for item in items:
    if not should_process(item):
        logger.info(f"スキップ: {item.id}")  # 不要
```

## 並列処理

### ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from settings import CONVERT_THREAD

def process_single_item(item_data: dict, lock: threading.Lock, counters: dict):
    db = SessionLocal()  # 各スレッドで独立セッション
    try:
        # 処理
        with lock:
            counters["success_count"] += 1
        return {"success": True}
    except Exception as e:
        with lock:
            counters["error_count"] += 1
        return {"success": False}
    finally:
        db.close()

def main(db: Session, task_id: Optional[str] = None):
    progress_lock = threading.Lock()
    counters = {"success_count": 0, "error_count": 0}
    
    with ThreadPoolExecutor(max_workers=CONVERT_THREAD) as executor:
        futures = {executor.submit(process_single_item, item, progress_lock, counters): item 
                   for item in items}
        
        for future in as_completed(futures):
            result = future.result()
            if task_id:
                with progress_lock:
                    processed = counters["success_count"] + counters["error_count"]
                    update_task_status(db, task_id, current_item=processed)
```

### MultiProcessing

```python
from multiprocessing import Pool

def process_batch(args: Tuple[List, int, int]) -> List:
    items, start, end = args
    return [process(item) for item in items[start:end]]

# CPU集約的処理向け
with Pool(CONVERT_THREAD) as pool:
    results = pool.map(process_batch, batches)
```

## 参考実装

- **library_integrity_check.py**: シンプルなループ、3分類（ロスト/重複/修復）
- **library_sim_lsh.py**: 複数フェーズ、マルチプロセス、複雑アルゴリズム
- **thumbnail_recreate.py**: ThreadPoolExecutor、スレッドセーフ進捗管理

## チェックリスト

- [ ] `main(db: Session, ..., task_id: Optional[str] = None)` 実装
- [ ] 日本語docstring
- [ ] `update_task_status` で進捗更新
- [ ] 完了メッセージに結果分類を含める
- [ ] エラーハンドリング（try-except + failed status）
- [ ] ログ出力（日本語、適切なレベル）
- [ ] 型ヒント
- [ ] 対象なし時の処理
- [ ] 並列処理時は個別DBセッション
- [ ] ruff チェック通過
