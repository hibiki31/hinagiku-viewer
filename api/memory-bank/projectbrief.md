# Project Brief - API Module

hinagiku-viewerのバックエンドAPIサーバー。プロジェクト全体は `/workspace/memory-bank/` を参照。

## 主要責務
1. RESTful API提供（書籍・著者・タグ・ユーザーのCRUD）
2. JWT認証 + OAuth2 Password Flow
3. PostgreSQL + SQLAlchemy 2.0 + Alembicマイグレーション
4. メディア処理（Zip画像抽出、サムネイル生成、キャッシュ）
5. バックグラウンドタスク（import/export/重複チェック/ハッシュ計算）

## モジュール構成
```
api/
├── main.py / settings.py / worker.py   # エントリーポイント
├── books/   users/   authors/   tags/  # ドメインモジュール
├── media/   user_datas/                # メディア・ユーザーデータ
├── mixins/                             # 共通（DB, ログ, 画像変換, パーサー, スキーマ）
├── tasks/                              # バックグラウンドタスク
├── alembic/                            # マイグレーション
└── tests/                              # テスト
```

## エンドポイント
`/api/auth`, `/api/users`, `/api/books`, `/api/authors`, `/api/tags`, `/api/media`, `/api/user_datas`, `/api/mixin`
