# Project Brief - hinagiku-viewer

## 概要
Zipファイルで管理された書籍（電子書籍・コミック等）を一元管理し、メタデータの表示・検索・閲覧ができるWebアプリケーション。

## コア機能
1. **書籍管理**: Zipインポート（監視フォルダ自動取り込み）、ライブラリ管理、サムネイル自動生成
2. **メタデータ**: 著者・タグ・ジャンル・出版社・シリーズの管理（多対多対応）
3. **重複検出**: SHA1ハッシュ + aHash（知覚的ハッシュ）
4. **検索**: 全文検索、複数条件フィルタリング、ソート、ページネーション
5. **認証**: JWT + OAuth2 Password Flow、スコープベース権限、ライブラリ共有
6. **バックグラウンド処理**: DBベースタスクキュー（インポート/エクスポート/重複チェック等）

## 技術スタック
- **API**: FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL 16（Python 3.11+）
- **フロントエンド**: Vue 3 + Vite + Vuetify 3 + TypeScript + Pinia（★主力: `vue/`）
- **レガシー**: Vue 2（`web/`）、Nuxt 3（`nuxt/` 非推奨）
- **デプロイ**: Docker Compose + Nginx（単一ポート公開）

## プロジェクト構造
```
/workspace/
├── api/          # FastAPI バックエンド + Worker
├── vue/          # Vue 3 + Vite（主力フロントエンド）
├── web/          # Vue 2（レガシー）
├── nuxt/         # Nuxt 3（非推奨）
├── data/         # データディレクトリ（ボリュームマウント）
└── compose.yaml  # Docker Compose設定
```

## 制約事項
- Zipファイル内の画像ファイルのみ対応
- ファイル名長制限（OS制約: 255文字）
- PostgreSQL必須
