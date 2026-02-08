# Project Brief - Vue 3 フロントエンド

## 重要: プロジェクト全体のドキュメントを参照

このファイルは `vue/` ディレクトリのVue 3フロントエンド固有のプロジェクト概要です。
**プロジェクト全体の情報は `/workspaces/hinagiku-viewer/memory-bank/projectbrief.md` を参照してください。**

プロジェクトルートのprojectbriefには以下が含まれます：
- hinagiku-viewerプロジェクト全体の概要
- 主要目標とコア機能
- 技術スタック全体（バックエンド + フロントエンド）
- アーキテクチャ原則とプロジェクト構造

## Vue 3フロントエンドのスコープ

### プロジェクト名
hinagiku-viewer Vue 3 フロントエンド（主力）

### 概要
Vue 3 + Vite + Vuetify 3で構築されたhinagiku-viewerのWebフロントエンドアプリケーション。
Vue 2（web/）からの移行先として開発され、現在主力フロントエンドとして位置付けられている。

### 位置付け
- **Vue 3（vue/）**: 主力フロントエンド ← **このディレクトリ**
- **Vue 2（web/）**: 旧本番環境（将来的に置き換え予定）
- **Nuxt 3（nuxt/）**: 移行実験（非推奨、使用しない）

### 主要目標
1. Vue 2からVue 3への完全移行
2. 型安全な開発環境の構築（TypeScript）
3. 開発者体験の向上（Vite、自動インポート、ファイルベースルーティング）
4. モダンなUI/UX（Vuetify 3）
5. 保守性の高いコードベース

## コア機能（フロントエンド視点）

### 実装済み
1. **書籍一覧ページ** (`src/pages/index.vue`)
   - 検索・フィルタ・ソート
   - サムネイル/テーブル表示切替
   - ページネーション
   - 評価機能

2. **書籍リーダーページ** (`src/pages/books/[uuid].vue`)
   - ページ送り（単ページ/見開き）
   - 画像先読みシステム
   - 閲覧設定の永続化
   - 評価更新

3. **ログインページ** (`src/pages/login.vue`)
   - JWT認証
   - Cookie管理
   - 自動セットアップダイアログ

4. **重複管理ページ** (`src/pages/duplicate.vue`)
   - 重複検出実行
   - 重複グループ表示
   - 個別削除

### 未実装（移行予定）
- ユーザー設定管理UI
- 管理者機能UI
- 外部メタデータ連携UI

## 技術スタック（Vue 3固有）

### フレームワーク・ライブラリ
- **Vue 3.4+**: Composition API, `<script setup>`
- **Vite 5**: 高速ビルドツール
- **TypeScript 5.6**: 型安全
- **Vuetify 3.6+**: Material Design UIフレームワーク
- **Pinia 2.1+**: 状態管理
- **Vue Router 4.4+**: ルーティング

### 開発ツール
- **unplugin-vue-router 0.10**: ファイルベースルーティング
- **unplugin-auto-import 0.17**: Vue API自動インポート
- **unplugin-vue-components 0.27**: コンポーネント自動インポート
- **vite-plugin-vue-layouts 0.11**: レイアウトシステム
- **pnpm**: パッケージマネージャー

### API通信
- **Axios 1.8+**: 現在のメインクライアント
- **openapi-fetch 0.13+**: 型安全クライアント（移行先）

## プロジェクト構造
```
vue/
├── .clinerules              # Vue固有のClineルール
├── memory-bank/             # Vue固有のメモリーバンク ← このディレクトリ
├── src/
│   ├── pages/               # ページコンポーネント（ファイルベースルーティング）
│   ├── components/          # 再利用可能コンポーネント
│   ├── composables/         # Composition APIユーティリティ
│   ├── stores/              # Piniaストア
│   ├── func/                # 関数・クライアント
│   ├── layouts/             # レイアウト
│   ├── plugins/             # プラグイン
│   └── router/              # ルーター設定
├── vite.config.mts          # Vite設定
├── tsconfig.json            # TypeScript設定
└── package.json             # 依存関係
```

## 開発環境
- **作業ディレクトリ**: `/workspaces/hinagiku-viewer/vue`
- **開発サーバー**: `pnpm dev` → http://localhost:3000
- **DevContainer**: Node.js + pnpm環境
