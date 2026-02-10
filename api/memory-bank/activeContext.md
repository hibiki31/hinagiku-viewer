# Active Context - API Module

> **最終更新**: 2026/02/10  
> **親プロジェクトコンテキスト**: `/workspace/memory-bank/activeContext.md` を参照

## 現在の状態

### プロジェクトステータス
- **フェーズ**: 本番運用中、継続的改善
- **バージョン**: API_VERSION = '3.0.0'（settings.pyで管理）
- **安定性**: 安定稼働中
- **コードレビュー**: 2026/02/10完了 → `codeReview.md`参照

### 最近の主要変更
1. **コードレビュー実施** (2026/02/10)
   - 全ソースコード包括的レビュー
   - セキュリティ、パフォーマンス、コード品質の課題抽出
   - 優先度別改善計画策定（`codeReview.md`）

2. **テーブル名変更** (2025/08/30)
   - マイグレーション: `20250830_180124_568d3abf1cee_change_table_name.py`
   - データベーススキーマの整理

3. **お気に入り機能追加** (2024/01/05)
   - マイグレーション: `20240105_073810_43b53bf68b39_add_is_favorite.py`
   - ユーザーが書籍をお気に入り登録可能

4. **重複検出機能** (2023/09/29-30)
   - aHashによる画像ハッシュ（hash_size=16）
   - 重複テーブル追加、on_delete修正
   - 重複判定閾値: score < 10

## 現在の作業フォーカス

### Memory Bank整備（完了）
- ✅ APIディレクトリ専用のmemory-bank構築
- ✅ 親ディレクトリ（`/workspace/memory-bank/`）との連携
- ✅ 全ソースコードの包括的レビュー
- ✅ 課題と改善点の文書化（`codeReview.md`）

### 次のステップ（優先順位順）

#### 1. 即時対応（セキュリティ）🔴
- [ ] CORS設定の環境変数化（main.py）
- [ ] SECRET_KEY管理の改善（settings.py）
- [ ] 管理者権限チェックの追加（POST /api/users等）
- [ ] トークン有効期限の短縮検討（30日→15分〜1時間）

#### 2. 短期対応（1-2ヶ月）🟡
- [ ] エラーハンドリングの改善
- [ ] ログレベル設定の見直し
- [ ] テストカバレッジ向上
- [ ] パフォーマンス計測実装

#### 3. 中期対応（3-6ヶ月）🟢
- [ ] タイポのマイグレーション（chached→cached, is_shered→is_shared）
- [ ] リレーションシップ戦略の統一
- [ ] 重複チェックアルゴリズムの改善（O(n²)問題）
- [ ] ページネーション最適化

## アクティブな技術的課題

### 🔴 重大な問題（即時対応）

1. **CORS設定が緩い**（main.py）
   - 現状: `allow_origins=["*"]`
   - リスク: CSRF攻撃、認証情報の漏洩
   - 対応: 環境変数で制限

2. **SECRET_KEY管理**（settings.py）
   - 現状: 開発環境で`'DEV_KEY'`固定
   - リスク: JWT署名の脆弱性
   - 対応: 開発環境でも動的生成

3. **トークン有効期限30日**（users/router.py）
   - 現状: `ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30`
   - リスク: 漏洩時の被害拡大
   - 対応: 15分〜1時間に短縮 + リフレッシュトークン検討

4. **管理者権限チェック不足**
   - 現状: POST /api/usersで一般ユーザーも作成可能
   - リスク: 権限昇格
   - 対応: `current_user.is_admin`チェック追加

### 🟡 中程度の問題

1. **ファイル名長制限**
   - 症状: `OSError: [Errno 36] File name too long`
   - 発生箇所: Zip展開時（`mixins/convertor.py`）
   - 現状対応: エラーキャッチのみ
   - 要対応: パス長事前チェック、リトライ機構

2. **タイポの継続使用**
   - `chached` → cached
   - `is_shered` → is_shared
   - `comaier` → compared
   - フロントエンド型定義にも影響
   - 方針: 破壊的変更のため慎重にマイグレーション

3. **リレーションシップのlazy設定不統一**
   - books.tags: lazy=False（eager）
   - TagsModel.books: lazy=True（lazy）
   - リスク: N+1問題、パフォーマンス予測困難

4. **重複チェックの計算量O(n²)**（tasks/library_sim.py）
   - 現状: マルチプロセスで緩和
   - 課題: 大量データで処理時間爆発
   - 対応: ハッシュインデックス化、閾値フィルタ

5. **ページネーションの非効率**
   - 毎回`count()`で全件カウント
   - 対応: キャッシュ、概算カウント検討

### 🟢 軽微な問題
- ハードコードされた値（API_VERSION、マジックナンバー）
- 未使用のインポート
- docstring不足
- 型ヒント不完全
- テストカバレッジ未計測

## 重要な設定値（発見事項）

### 認証関連
- トークン有効期限: 30日（`ACCESS_TOKEN_EXPIRE_MINUTES`）
- JWT署名: SECRET_KEY（開発: 'DEV_KEY'、本番: 環境変数 or 自動生成）
- アルゴリズム: HS256

### 重複検出
- ハッシュサイズ: 16×16 = 256bit（`imagehash.average_hash(..., hash_size=16)`）
- 判定閾値: score < 10（ビット差分）
- 処理: マルチプロセス（CONVERT_THREAD並列）

### バックグラウンドワーカー
- 並列度: `CONVERT_THREAD = int(os.cpu_count())`
- タスク種別: import, export, delete, fixmetadata, sim, rule, cache
- 実行方法: subprocess.Popen経由

### ファイルパス
- 書籍: `/opt/data/book_library/{uuid}.zip`
- サムネイル: `/opt/data/book_thum/{uuid}.jpg`
- キャッシュ: `/opt/data/book_cache/{uuid}/{height}_{page}.jpg`
- 一時展開: `/tmp/hinav/`

## アーキテクチャ決定事項（直近）

### バックグラウンドワーカー
- 現状: `worker.py`のポーリング方式
- 検討: Celery移行？
- 判断保留: 現状で問題なし

### データベースマイグレーション
- Alembic継続使用
- 自動生成 + 手動レビュー方針

## 開発環境の状態

### 現在の設定
- Python 3.11+
- FastAPI 0.116.1
- SQLAlchemy 2.0.43
- PostgreSQL 16

### 依存関係の健全性
- 最終更新確認: 2026/02/10
- セキュリティアラート: 要確認

## Vue 3フロントエンドとの統合

### API型定義の同期
- フロントエンド: `vue/src/api.d.ts`
- 生成元: `/api/openapi.json`
- 同期方法: 手動実行（自動化検討中）

### 認証フロー
- JWT + Cookie方式
- フロントエンド: `stores/userData.ts`
- バックエンド: `users/router.py`

## 今後の展望

### 短期（1-2ヶ月）
- [x] Memory Bank完全整備
- [x] コードレビュー実施
- [ ] セキュリティ改善（CORS、SECRET_KEY、権限チェック）
- [ ] テストカバレッジ向上
- [ ] ドキュメント整備

### 中期（3-6ヶ月）
- [ ] パフォーマンス改善
- [ ] エラーハンドリング強化
- [ ] ロギング改善
- [ ] 監視・アラート整備
- [ ] タイポのマイグレーション

### 長期（6ヶ月以上）
- [ ] Redis導入検討
- [ ] Celery導入検討
- [ ] GraphQL検討
- [ ] マイクロサービス化検討

## チーム・コミュニケーション

### 主要ステークホルダー
- フロントエンド開発者（Vue 3）
- システム管理者
- エンドユーザー

### ドキュメント
- OpenAPI仕様: `/api`
- README.md: 開発者向け
- Memory Bank: Cline向け（最新更新: 2026/02/10）
- Code Review: `codeReview.md`

## 注意事項

### 変更時の必須対応
1. データベーススキーマ変更 → Alembicマイグレーション作成
2. API仕様変更 → フロントエンド型定義再生成
3. 認証ロジック変更 → フロントエンドとの調整
4. ログメッセージ → 日本語で記述

### コーディング規約
- ログは日本語
- Gitコミットメッセージは日本語
- コメントは日本語
- 型ヒント必須
- Pydanticスキーマでバリデーション

## 現在のブロッカー
- なし

## 質問・不明点
- 本番環境のSECRET_KEY設定状況（要確認）
- Nginx設定内容（セキュリティヘッダー、レート制限）
- PostgreSQLのインデックス設定詳細

## 最終更新日
2026-02-10: コードレビュー完了、課題抽出、Memory Bank更新完了
