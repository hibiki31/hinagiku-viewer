# Active Context - API Module

## 現在の状態（2026-02-10）
- 本番稼働中、安定
- コードレビュー・リファクタリング完了（フェーズ1,2,4,5）

## 優先課題

### セキュリティ 🔴
- CORS: `allow_origins=["*"]` → 環境変数で制限（main.py）
- SECRET_KEY: 開発時'DEV_KEY'固定 → 動的生成推奨
- 権限: POST /api/usersに管理者チェック未実装
- トークン: 30日 → 短縮 + リフレッシュトークン検討

### パフォーマンス 🟡
- 重複チェック: O(n²) → ハッシュインデックス化
- ページネーション: 毎回count() → キャッシュ検討
- lazy loading不統一（N+1リスク）

### コード品質 🟢
- テストカバレッジ未計測（pytest + coverage導入）
- API docstring不足
- ハードコード値（API_VERSION、マジックナンバー）

## 未完了リファクタリング
- フェーズ3: DBカラム名タイポ修正（chached→cached, is_shered→is_shared）— 破壊的変更のため保留

## 変更時の必須対応
1. DBスキーマ変更 → Alembicマイグレーション
2. API仕様変更 → フロントエンド型定義再生成
3. ログ → 日本語で記述
