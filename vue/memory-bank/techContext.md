# Tech Context - Vue 3 フロントエンド

## 重要: プロジェクト全体の技術情報を参照

このファイルは `vue/` ディレクトリのVue 3フロントエンド固有の技術コンテキストです。
**プロジェクト全体の情報は `/workspaces/hinagiku-viewer/memory-bank/techContext.md` を参照してください。**

プロジェクトルートのtechContextには以下が含まれます：
- バックエンド技術スタック（FastAPI, SQLAlchemy, Alembic等）
- データベース（PostgreSQL）
- Webサーバー（Nginx）
- Docker構成
- 環境変数
- ポート使用状況
- トラブルシューティング

## Vue 3フロントエンド技術スタック

### コアフレームワーク
- **Vue 3.4+**: Composition API, `<script setup lang="ts">`
- **Vite 5**: 高速開発サーバー、HMR、高速ビルド
- **TypeScript 5.6**: 型安全、IDE補完

### UIフレームワーク
- **Vuetify 3.6+**: Material Design コンポーネント
- **@mdi/font 7.4**: Material Design Icons
- **Sass 1.77**: スタイリング（modern-compiler API使用）

### 状態管理・ルーティング
- **Pinia 2.1+**: Vue 3公式推奨の状態管理
- **Vue Router 4.4+**: 公式ルーター

### ビルドツール・プラグイン
- **unplugin-vue-router 0.10**: ファイルベースルーティング自動生成
- **unplugin-auto-import 0.17**: Vue API自動インポート
- **unplugin-vue-components 0.27**: コンポーネント自動インポート
- **vite-plugin-vue-layouts 0.11**: レイアウトシステム
- **vite-plugin-vuetify 2**: Vuetify設定自動化
- **vite-plugin-fonts 0.7**: Webフォント最適化
- **vite-plugin-pwa 0.20**: PWA対応、Service Worker自動生成

### HTTP通信
- **Axios 1.8+**: HTTP クライアント（現在のメイン）
- **openapi-fetch 0.13+**: 型安全なOpenAPIクライアント（移行先）
- **openapi-typescript 7+**: OpenAPIスキーマから型定義生成

### ユーティリティ
- **@kyvg/vue3-notification 3.4**: トースト通知
- **js-cookie 3.0**: Cookie管理

### 開発ツール
- **pnpm**: 高速パッケージマネージャー
- **ESLint 9**: コード品質チェック
- **@vue/tsconfig 0.6**: TypeScript設定ベース

## プロジェクト構造詳細

```
vue/
├── .devcontainer/          # DevContainer設定
│   ├── devcontainer.json   # VS Code設定
│   ├── Dockerfile          # 開発環境イメージ
│   └── post.sh             # 起動後スクリプト
│
├── .clinerules             # Clineルール
├── memory-bank/            # メモリーバンク ← このディレクトリ
├── PWA.md                  # PWA対応ドキュメント
├── Dockerfile              # Docker本番環境用
├── nginx.conf              # Nginx設定
│
├── public/                 # 公開静的ファイル
│   ├── favicon.ico
│   ├── icon-*.png          # PWA用アイコン
│   ├── icon-apple.png      # Apple用アイコン
│   └── manifest.webmanifest # PWAマニフェスト
│
├── src/
│   ├── main.ts             # エントリーポイント
│   ├── App.vue             # ルートコンポーネント
│   │
│   ├── api.d.ts            # OpenAPI型定義（自動生成）
│   ├── auto-imports.d.ts   # 自動インポート型定義（自動生成）
│   ├── components.d.ts     # コンポーネント型定義（自動生成）
│   ├── typed-router.d.ts   # ルーター型定義（自動生成）
│   ├── pwa.d.ts            # PWA型定義
│   │
│   ├── pages/              # ページ（ファイルベースルーティング）
│   │   ├── index.vue
│   │   ├── login.vue
│   │   ├── duplicate.vue
│   │   └── books/
│   │       └── [uuid].vue
│   │
│   ├── components/         # 再利用可能コンポーネント
│   │   ├── BooksListTable.vue
│   │   ├── BooksListThum.vue
│   │   ├── BaseAuthorChip.vue
│   │   ├── AppFooter.vue
│   │   └── dialog/
│   │       ├── SearchDialog.vue
│   │       ├── BookDetailDialog.vue
│   │       ├── RangeChangeDialog.vue
│   │       └── SetupDialog.vue
│   │
│   ├── composables/        # Composition APIユーティリティ
│   │   ├── utility.ts      # 通知、URL生成、フォーマット等
│   │   ├── rules.ts        # バリデーションルール
│   │   ├── title.ts        # ページタイトル動的設定
│   │   └── gesture.ts      # マウス・タッチジェスチャー認識
│   │
│   ├── func/               # 関数・クライアント
│   │   ├── axios.ts        # Axiosインスタンス
│   │   ├── client.ts       # openapi-fetchクライアント
│   │   ├── auth.ts         # 認証ユーティリティ
│   │   └── sleep.ts        # スリープ関数
│   │
│   ├── stores/             # Piniaストア
│   │   ├── index.ts        # ストアエクスポート
│   │   ├── userData.ts     # 認証状態
│   │   ├── readerState.ts  # 書籍一覧・リーダー状態
│   │   ├── auth.ts         # 認証設定
│   │   └── app.ts          # アプリ全般
│   │
│   ├── layouts/            # レイアウト
│   │   └── default.vue
│   │
│   ├── plugins/            # プラグイン
│   │   ├── index.ts        # プラグイン統合
│   │   └── vuetify.ts      # Vuetify設定
│   │
│   ├── router/             # ルーター
│   │   └── index.ts        # ルーター設定・ガード
│   │
│   ├── styles/             # スタイル
│   │   └── settings.scss   # Vuetify SCSS設定
│   │
│   └── assets/             # 静的アセット
│       ├── logo.png
│       └── logo.svg
│
├── index.html              # HTMLテンプレート
├── vite.config.mts         # Vite設定
├── tsconfig.json           # TypeScript設定（ルート）
├── tsconfig.app.json       # アプリ用TypeScript設定
├── tsconfig.node.json      # Node用TypeScript設定
├── eslint.config.js        # ESLint設定
├── package.json            # 依存関係
├── pnpm-lock.yaml          # ロックファイル
├── .browserslistrc         # ブラウザターゲット
├── .editorconfig           # エディタ設定
├── .gitignore              # Git除外設定
├── README.md               # プロジェクト説明
│
└── scripts/                # ユーティリティスクリプト
    └── export-cline-history.py  # Clineタスク履歴エクスポート
```

## Vite設定（vite.config.mts）

### プラグイン構成
```typescript
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import VueRouter from 'unplugin-vue-router/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Layouts from 'vite-plugin-vue-layouts'
import { VueRouterAutoImports } from 'unplugin-vue-router'

export default defineConfig({
  plugins: [
    VueRouter(),       // ファイルベースルーティング
    Layouts(),         // レイアウトシステム
    AutoImport({       // 自動インポート
      imports: ['vue', VueRouterAutoImports],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({       // コンポーネント自動インポート
      dts: 'src/components.d.ts',
    }),
    vue(),
    vuetify({ autoImport: true }),
    VitePWA({          // PWA対応
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'icon-*.png'],
      manifest: {
        name: 'Hinagiku Viewer',
        short_name: 'Hinagiku',
        description: '電子書籍ビューアー',
        theme_color: '#082240',
        icons: [
          { src: 'icon-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icon-512x512.png', sizes: '512x512', type: 'image/png' }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000
  },
  css: {
    preprocessorOptions: {
      scss: { api: 'modern-compiler' }
    }
  },
  define: {
    '__APP_VERSION__': JSON.stringify(process.env.npm_package_version)
  }
})
```

### エイリアス
- `@` → `src/`

### 開発サーバー
- ポート: 3000
- HMR有効
- ホスト: localhost

## TypeScript設定

### tsconfig.json（ルート）
- `composite: true`
- プロジェクト参照（app, node）

### tsconfig.app.json
- `target: "ES2020"`
- `strict: true`
- `jsx: "preserve"`
- 自動生成型定義を含む

## 環境変数

### .env.local（Git管理外）
```bash
VITE_APP_API_HOST=http://localhost   # APIホスト（統一済み）
```

### 使用方法
```typescript
import.meta.env.VITE_APP_API_HOST      # APIホスト
__APP_VERSION__                         # バージョン番号（ビルド時注入）
```

### バージョン番号の動的注入
vite.config.mtsで`__APP_VERSION__`を定義し、package.jsonのバージョンを自動注入：
```typescript
// 使用例
const version = __APP_VERSION__  // "1.0.0" など
```

## API型生成

### OpenAPIスキーマから型定義生成
```bash
npx openapi-typescript https://hinav.hinagiku.me/api/openapi.json -o ./src/api.d.ts
```

### 生成された型の使用
```typescript
import type { paths, components } from '@/api'

// スキーマ型
type BookBase = components['schemas']['BookBase']

// エンドポイント型（openapi-fetch用）
import createClient from 'openapi-fetch'
const client = createClient<paths>({ baseUrl: '...' })
```

## 開発コマンド

### インストール
```bash
cd vue/
pnpm install
```

### 開発サーバー
```bash
pnpm dev
# http://localhost:3000 で起動
```

### ビルド
```bash
pnpm build          # 型チェック + ビルド（並列）
pnpm build-only     # ビルドのみ（型チェックなし）
pnpm type-check     # 型チェックのみ
```

### リント
```bash
pnpm lint           # ESLint --fix
```

### Docker（本番環境）
```bash
# イメージビルド
docker build -t hinagiku-vue .

# コンテナ起動
docker run -p 80:80 hinagiku-vue
```

## DevContainer環境

### 構成
- **ベースイメージ**: Node.js
- **パッケージマネージャー**: pnpm（プリインストール）
- **ポートフォワード**: 3000
- **VS Code拡張**:
  - Vue.volar
  - Vue.vscode-typescript-vue-plugin
  - dbaeumer.vscode-eslint
  - esbenp.prettier-vscode
  - saoudrizwan.claude-dev

### 起動後スクリプト（post.sh）
```bash
pnpm install
```

## Vuetify設定

### テーマカスタマイズ（src/plugins/vuetify.ts）
```typescript
import { createVuetify } from 'vuetify'

export default createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#082240',    // カスタムプライマリ色
          success: '#22663f',    // カスタム成功色
        }
      }
    }
  }
})
```

### SCSS設定（src/styles/settings.scss）
Vuetify変数のカスタマイズ

## 既知の技術的特徴

### 自動生成ファイル（Git管理対象）
以下のファイルは自動生成されるが、リポジトリにコミット：
- `src/auto-imports.d.ts`
- `src/components.d.ts`
- `src/typed-router.d.ts`
- `src/api.d.ts`（手動生成）

**理由**: 型安全性とIDEサポート向上のため

### タイポの存在
- `authenticaitonSuccessful` / `authenticaitonFail`（正: `authentication`）
- 既存コード全体で使用されているため、現状維持

### PWA対応の特徴
- **Service Worker**: vite-plugin-pwaが自動生成
- **オフライン対応**: キャッシュ戦略はNetworkFirst
- **自動更新**: registerType: 'autoUpdate'
- **マニフェスト**: インストール可能なWebアプリ
- **詳細**: PWA.md参照

### Docker本番環境の特徴
- **マルチステージビルド**: Node.js（ビルド） + Nginx（実行）
- **軽量イメージ**: Alpine Linux使用
- **SPA対応**: Nginxでフォールバック設定（nginx.conf）

## トラブルシューティング

### よくあるエラー

| エラー | 原因 | 対処 |
|--------|------|------|
| Vite HMRエラー | 動的インポート失敗 | ページリロード |
| 型エラー（api.d.ts） | OpenAPIスキーマ変更 | 型定義再生成 |
| 401エラー | JWT期限切れ | 再ログイン（自動リロード） |
| コンポーネント未定義 | 自動インポート失敗 | 開発サーバー再起動 |

### デバッグツール
- **Vue Devtools**: ブラウザ拡張
- **Viteログ**: ターミナル確認
- **Network タブ**: API通信確認
- **Console**: エラーログ確認

## 最終更新日
2026-02-09: PWA対応、Docker本番環境、バージョン番号自動注入、ジェスチャー機能追加
