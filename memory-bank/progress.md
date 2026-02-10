# Progress

## 実装済み

### バックエンド（API）
- ✅ 書籍CRUD + 検索/フィルタ/ページネーション + 評価/お気に入り
- ✅ メタデータ管理（著者・タグ・ジャンル・出版社・シリーズ、多対多対応）
- ✅ JWT認証 + OAuth2 + bcrypt + スコープ権限
- ✅ バックグラウンドWorker（import/export/delete/sim/cache/fixmetadata）
- ✅ メディア配信（Zip画像抽出、サムネイル、動的リサイズ、キャッシュ）
- ✅ 重複検出（SHA1 + aHash、hash_size=16、閾値score<10）
- ✅ Docker Compose + Alembicマイグレーション + 日本語ログ

### フロントエンド（Vue 3 — vue/）
- ✅ 基盤: Vue 3 + Vite + Vuetify 3 + Pinia + ファイルベースルーティング
- ✅ 書籍一覧（検索・フィルタ・サムネイル/テーブル切替）
- ✅ 書籍リーダー（ページ送り・先読み・見開き・設定永続化）
- ✅ ログイン（JWT認証・セットアップ）
- ✅ 重複管理（検出・削除・一覧）
- ✅ ダイアログ: SearchDialog, BookDetailDialog, RangeChangeDialog, SetupDialog

### リファクタリング（2026/02/10完了）
- ✅ フェーズ1: 内部命名改善（purser→parser, make_thum→make_thumbnail等）
- ✅ フェーズ2: Pydanticエイリアス対応（snake_case↔camelCase自動変換）
- ✅ フェーズ4: series_number等の命名統一
- ✅ フェーズ5: エンドポイント関数名のRESTful化

## 未完了

### Vue 3残作業
- [ ] ユーザー設定UI、管理者機能、メタデータ一括編集完全性
- [ ] Axios→openapi-fetch移行
- [ ] 本番切り替え（Docker統合、Nginx設定、E2Eテスト）

### 技術的改善
- [ ] セキュリティ（CORS制限、SECRET_KEY、権限チェック、トークン期限）
- [ ] テストカバレッジ向上（pytest + coverage）
- [ ] CI/CD構築
- [ ] パフォーマンス（重複チェックO(n²)、count()最適化）

### 将来
- [ ] フェーズ3: DBカラムタイポ修正（破壊的変更）
- [ ] Redis/Celery導入検討
- [ ] Vue 2廃止
