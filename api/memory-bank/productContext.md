# Product Context - API Module

## APIの役割
```
[Vue Frontend] →HTTP→ [FastAPI Router] → [SQLAlchemy] → [PostgreSQL]
                       [Worker]        → [ファイルシステム] → [PostgreSQL]
```

## 提供価値
- **データ一元化**: Zip書籍への統一的アクセス、リレーショナルDB管理
- **マルチユーザー**: JWT認証、ユーザー別閲覧履歴・評価、ライブラリ共有
- **非同期処理**: 重い処理（Zipインポート、ハッシュ計算、サムネイル生成）をWorkerに分離
- **フロントエンド支援**: OpenAPI仕様自動生成 → 型安全なクライアント生成

## 技術選定理由
- **FastAPI**: 高速、OpenAPI自動生成、Pydantic型安全性
- **PostgreSQL**: 複雑なリレーション、トランザクション保証
- **Workerプロセス**: API応答への影響回避、追加ミドルウェア不要
