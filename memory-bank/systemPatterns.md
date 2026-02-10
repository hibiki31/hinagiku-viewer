# System Patterns

## 全体構成
```
[ブラウザ] → [Nginx:80] → [Vue SPA 静的配信]
                        → [FastAPI:8000] (/api)
                              ↓
                        [PostgreSQL:5432]
                              ↑
                        [Worker (worker.py)]
```

## API アーキテクチャ
- **ドメイン分割**: `books/`, `users/`, `authors/`, `tags/`, `media/`, `user_datas/`
- **各ドメイン構成**: `models.py` + `router.py` + `schemas.py`
- **共通**: `mixins/`（DB接続、ログ、画像変換、パーサー、スキーマ基底クラス）
- **依存性注入**: `Depends(get_db)`, `Depends(get_current_user)`

## DB設計
- Books: UUID主キー、多対多（Authors, Tags）、多対一（Publisher, Series, Genre）
- UserBookData: 複合主キー（user_id, book_uuid）— 閲覧履歴・評価
- Duplication: 複合主キー（book_uuid_1, book_uuid_2）— 重複スコア
- リレーションシップ: 基本eager loading（N+1回避）

## タスクキュー
- `worker.py`がポーリング（10秒間隔）
- タスク: import, export, delete, fixmetadata, sim(重複), rule, cache
- 並列度: `CONVERT_THREAD`（CPUコア数）、subprocess.Popen実行

## 認証
- OAuth2 Password Flow → JWT発行 → Cookie送信
- トークン有効期限: 30日
- スコープベース権限（部分実装）

## スキーマ設計
- `BaseSchema`（`mixins/schema.py`）: `alias_generator=to_camel`でsnake_case↔camelCase自動変換
- `populate_by_name=True`で両方受け付け、`from_attributes=True`でORM変換対応

## 設計上の重要決定
1. **単一ポート公開**: Nginxで統合、CORS回避
2. **UUID主キー（Books）**: 分散環境での衝突回避
3. **DBベースタスクキュー**: 追加ミドルウェア不要（Celery等不使用）
4. **ログ日本語統一**: デバッグ効率優先
