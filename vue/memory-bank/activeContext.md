# Active Context - Vue 3 フロントエンド

## 重要: プロジェクト全体のコンテキストを参照

このファイルは `vue/` ディレクトリのVue 3フロントエンド固有の現在のコンテキストです。
**プロジェクト全体の情報は `/workspaces/hinagiku-viewer/memory-bank/activeContext.md` を参照してください。**

## 現在の作業フォーカス（Vue 3固有）

### 日付
2026-02-10

### 状態
- Vue 3フロントエンドの主要4ページが実装完了
- **重要更新**: 主要パッケージのメジャーバージョンアップ完了
  - Vite 7.3.1、Vue Router 5.0.2、Pinia 3.0.4
  - unplugin系も最新版に更新済み
- APIクライアントをopenapi-fetchに完全統一（Axios完全排除済み）
- PWA対応完了（オフライン機能実装）
- Docker本番環境への統合完了
- 本番切り替え準備完了

## 最近の変更（Vue 3固有）

### 2026-02-10: 主要パッケージメジャーアップデート完了 🎉
- **Vite 5 → 7**: ビルドツールのメジャー更新（2段階アップ）
- **Vue Router 4 → 5**: ルーティングライブラリ更新
- **Pinia 2 → 3**: 状態管理ライブラリ更新
- **unplugin-auto-import**: 0.17 → 21.0.0
- **unplugin-vue-components**: 0.27 → 31.0.0
- **unplugin-vue-router**: 0.10 → 0.19
- **@vitejs/plugin-vue**: 5 → 6
- **vue-tsc**: 2 → 3
- その他: TypeScript, Sass, ESLint, openapi-fetch等も更新
- **動作確認**: 全機能正常動作を確認済み

### 2026-02-09: PWA対応完了
- **vite-plugin-pwa**導入：オフライン対応、Service Worker自動生成
- マニフェストファイル追加（manifest.webmanifest）
- 各種アイコン追加（192x192, 256x256, 384x384, 512x512, apple用）
- PWA.mdドキュメント作成

### 2026-02-08: 書籍ビューアー大幅強化
- **ページタイトル動的設定**: composables/title.ts追加、全ページで実装
- **Docker本番環境対応**: Dockerfile、nginx.conf追加
- **ビューアーUI全面刷新**: 設定メニューの改善
- **見開き自動判定機能**: 画像アスペクト比から自動判定
- **ジェスチャー機能**: composables/gesture.ts追加（マウス・タッチ対応）
- **ドロワーメニュー改善**: UI構造化
- **バージョン番号注入**: package.jsonのバージョンをビルド時に自動注入
- **メモリーバンク構造化**: vue/memory-bank/ ディレクトリを作成

### 実装済みページ
1. **書籍一覧** (`src/pages/index.vue`)
2. **書籍リーダー** (`src/pages/books/[uuid].vue`)
3. **ログイン** (`src/pages/login.vue`)
4. **重複管理** (`src/pages/duplicate.vue`)

## 現在のシステム状態（Vue 3固有）

### 開発環境
- **作業ディレクトリ**: `/workspaces/hinagiku-viewer/vue`
- **パッケージマネージャー**: pnpm
- **開発サーバー**: ポート3000
- **DevContainer**: 設定済み

### 実装状況
| カテゴリ | 状態 | 備考 |
|---------|------|------|
| 基盤構築 | ✅ 完了 | Vite 7, TypeScript, Vuetify 3 |
| ルーティング | ✅ 完了 | ファイルベース、型安全（Vue Router 5） |
| 状態管理 | ✅ 完了 | Pinia 3 - 4ストア |
| API通信 | ✅ 完了 | openapi-fetch統一（Axios完全排除済み） |
| 認証フロー | ✅ 完了 | JWT + Cookie |
| 主要ページ | ✅ 完了 | 4ページ実装済み |
| PWA対応 | ✅ 完了 | オフライン機能実装済み |
| Docker本番環境 | ✅ 完了 | Nginx設定完了 |
| パッケージ更新 | ✅ 完了 | メジャー更新完了（2026-02-10） |
| 管理者UI | ❌ 未実装 | 移行予定 |
| テーマ切替 | ❌ 未実装 | 検討中 |

## アクティブな決定と考慮事項（Vue 3固有）

### 1. メジャーパッケージ更新完了 🎉
**現状**: Vite 7, Vue Router 5, Pinia 3などメジャー更新完了（2026-02-10）
**成果**:
- ビルドシステムの最新化（Vite 7）
- パフォーマンス向上
- 新機能の活用が可能に
- 型安全性の向上
- Sass modern-compilerが自動適用（Vite 7）
- 全機能の動作確認済み

### 2. PWA対応完了
**現状**: オフライン機能が完全実装済み（2026-02-09）
**成果**:
- Service Worker自動生成（vite-plugin-pwa）
- アプリキャッシュ戦略（NetworkFirst）
- オフライン動作可能
- インストール可能なWebアプリ（ホーム画面追加対応）
- 詳細は `PWA.md` 参照

### 3. APIクライアント統一完了
**現状**: openapi-fetchに完全統一済み（2026-02-08）
**成果**: 
- `func/client.ts` (openapi-fetch) で全API呼び出しを統一
- Axios完全排除（パッケージ削除済み、ソースコードから完全消去）
- 401エラーハンドリングミドルウェア統合
- 型安全なAPI呼び出し（`paths`型によるエンドポイント型推論）

### 4. ページタイトル動的設定
**決定**: composables/title.ts で動的にページタイトルを設定
**実装**:
- `useSetTitle(title)`: ページタイトル設定
- ページ遷移時に自動更新
- 全主要ページで実装済み

### 5. Docker本番環境対応
**決定**: Nginx + 静的ビルドでの本番デプロイ
**実装**:
- `vue/Dockerfile`: マルチステージビルド
- `vue/nginx.conf`: SPA用フォールバック設定
- ビルド最適化済み

### 6. コンポーネント自動インポート
**決定**: `unplugin-vue-components`で自動インポート
**理由**: 
- importステートメント削減
- 開発効率向上
- 型定義は自動生成

### 7. ジェスチャー認識
**決定**: composables/gesture.ts で統一されたジェスチャー処理
**実装**:
- マウスドラッグ、タッチスワイプ対応
- 方向判定（left/right/up/down）
- しきい値設定可能
- 書籍リーダーで活用

### 8. localStorage活用
**決定**: 検索条件とリーダー設定をlocalStorageに永続化
**実装場所**: 
- `stores/readerState.ts`: searchQuery永続化
- `pages/books/[uuid].vue`: readerSettings永続化

## 次のステップ候補（Vue 3固有）

### 短期（1-2週間）
1. ~~未実装ページの移植~~ → 主要機能は完了
2. ~~環境変数の統一~~ → VITE_APP_API_HOSTに統一済み
3. ~~パッケージメジャー更新~~ → ✅ 完了（2026-02-10）
4. バージョン番号のタイポ修正（authenticaiton → authentication）
5. テーマ切替機能の実装検討
6. E2Eテストの準備

### 中期（1-3ヶ月）
1. ~~Docker環境への統合~~ → ✅ 完了（2026-02-08）
2. ~~PWA対応~~ → ✅ 完了（2026-02-09）
3. E2Eテスト実施
4. 未実装管理画面の移植
5. Vue 2（web/）からの本番切り替え

## 作業時の重要な注意事項（Vue 3固有）

### ファイル配置ルール
- **ページ**: `src/pages/` → 自動ルーティング
- **コンポーネント**: `src/components/` → 自動インポート
- **Composable**: `src/composables/` → 手動インポート
- **ストア**: `src/stores/` → 手動インポート

### コーディング規約
- `<script setup lang="ts">` を使用
- Vue APIは自動インポート（`ref`, `computed`等）
- Vuetifyコンポーネントは自動インポート
- API型は `src/api.d.ts` から取得

### 通知とユーティリティ
- 通知: `usePushNotice()` 
- カバー画像: `useGetCoverURL()`
- 日付フォーマット: `useConvertDateFormat()`
- 数値フォーマット: `useConvertNumFormat()`

## 依存関係・ブロッカー（Vue 3固有）

### 外部依存
- バックエンドAPI（FastAPI）の稼働
- `src/api.d.ts` の型定義（OpenAPIスキーマから生成）

### 技術的負債
1. ~~バージョン番号のハードコード~~ → ✅ 解決済み（ビルド時注入）
2. `authenticaitonSuccessful`/`authenticaitonFail` のタイポ（要修正）
3. テストカバレッジなし
4. 書籍リーダーのBlob取得が素のfetch（openapi-fetchのparseAs非対応のため）

## 最終更新日
2026-02-10: メジャーパッケージ更新完了（Vite 7, Vue Router 5, Pinia 3等）
