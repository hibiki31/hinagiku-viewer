# PWA対応ドキュメント

## 概要
HinaV（Hinagiku Viewer）をProgressive Web App (PWA)として利用可能にしました。

## 実装内容

### 1. パッケージのインストール
```bash
pnpm add -D vite-plugin-pwa workbox-window
```

### 2. Web App Manifest
- **ファイル**: `public/manifest.webmanifest`
- **設定内容**:
  - アプリ名: "HinaV - Hinagiku Viewer"
  - 表示モード: standalone（アプリライクな表示）
  - テーマカラー: #1867c0（Vuetifyのプライマリカラー）
  - アイコン: 192x192, 256x256, 384x384, 512x512サイズ
  - 画面向き: portrait-primary（縦向き優先）

### 3. Service Worker設定
- **ファイル**: `vite.config.mts`
- **機能**:
  - 自動更新（registerType: 'autoUpdate'）
  - 静的アセットのプリキャッシュ（JS, CSS, HTML, アイコン、フォント等）
  - ランタイムキャッシング戦略:
    - **Google Fonts**: CacheFirst（1年間キャッシュ）
    - **API呼び出し**: NetworkFirst（5分間キャッシュ、10秒でタイムアウト）

### 4. アプリケーション統合
- **ファイル**: `src/main.ts`
- Service Workerの登録とライフサイクルイベントのハンドリング:
  - `onNeedRefresh`: 新バージョン利用可能時
  - `onOfflineReady`: オフライン利用可能時
  - `onRegistered`: 登録完了時
  - `onRegisterError`: 登録エラー時

### 5. 型定義
- **ファイル**: `src/pwa.d.ts`
- TypeScript用のPWA型定義を追加

### 6. HTMLメタタグ
- **ファイル**: `index.html`
- PWA必須メタタグの追加:
  - `theme-color`: アプリのテーマカラー
  - `description`: アプリの説明
  - `manifest`: Web App Manifestへのリンク

## ビルド結果

ビルド時に以下のファイルが生成されます：
- `dist/sw.js` - Service Worker本体
- `dist/workbox-*.js` - Workboxランタイム
- `dist/manifest.webmanifest` - Web App Manifest

## インストール方法

### ユーザー向け
1. ブラウザでアプリにアクセス
2. アドレスバーまたはメニューに表示される「インストール」ボタンをクリック
3. ホーム画面にアプリアイコンが追加されます

### サポートブラウザ
- Chrome / Edge (Windows, Android, Mac)
- Safari (iOS 16.4+, macOS)
- Firefox

## オフライン機能

PWA対応により以下が可能になります：
- **静的アセット**: オフラインでも画面表示が可能
- **Google Fonts**: オフラインでもフォント読み込み可能
- **API**: 最近のレスポンスをキャッシュから取得（NetworkFirstストラテジー）

## 開発時の注意

### 開発サーバーでのPWA
デフォルトでは開発環境ではPWAは無効化されています。
有効化する場合は `vite.config.mts` で以下を変更：
```typescript
devOptions: {
  enabled: true,
}
```

### Service Workerのデバッグ
- Chrome DevTools → Application → Service Workers
- 登録状況、キャッシュストレージを確認可能

### キャッシュのクリア
開発時にキャッシュをクリアする場合：
1. Chrome DevTools → Application → Storage
2. "Clear site data" をクリック

## 更新方法

アプリが更新された場合：
1. Service Workerが新バージョンを検出
2. バックグラウンドでダウンロード
3. 自動的に新バージョンに更新（autoUpdate設定）

## カスタマイズ

### キャッシュ戦略の変更
`vite.config.mts` の `workbox.runtimeCaching` で設定可能：
- **CacheFirst**: キャッシュ優先（静的リソース向け）
- **NetworkFirst**: ネットワーク優先（API向け）
- **StaleWhileRevalidate**: キャッシュを返しつつバックグラウンド更新

### テーマカラーの変更
- `public/manifest.webmanifest` の `theme_color`
- `index.html` の `<meta name="theme-color">`

## トラブルシューティング

### Service Workerが登録されない
- HTTPSまたはlocalhostでアクセスしているか確認
- ブラウザコンソールでエラーを確認

### 古いキャッシュが残る
- Service Workerをアンレジスター
- ブラウザのキャッシュをクリア
- ページを再読み込み

## 参考リンク
- [vite-plugin-pwa](https://vite-pwa-org.netlify.app/)
- [Workbox](https://developer.chrome.com/docs/workbox)
- [Web App Manifest](https://developer.mozilla.org/ja/docs/Web/Manifest)
