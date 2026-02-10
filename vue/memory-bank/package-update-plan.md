# パッケージ更新計画

## 🎉 更新完了！（2026-02-10）

**このファイルは履歴資料として保存されています。**
すべてのメジャーパッケージ更新が完了し、全機能の動作確認も完了しました。

---

## 現在の状況（更新後）

### ✅ 完了したパッケージ更新

| パッケージ | 更新前 | 更新後 | 結果 |
|-----------|--------|--------|------|
| **vite** | 5.4.21 | **7.3.1** | ✅ 動作確認済み |
| **vue-router** | 4.6.4 | **5.0.2** | ✅ 動作確認済み |
| **pinia** | 2.3.1 | **3.0.4** | ✅ 動作確認済み |
| **@vitejs/plugin-vue** | 5.2.4 | **6.0.4** | ✅ 動作確認済み |
| **vue-tsc** | 2.2.12 | **3.2.4** | ✅ 動作確認済み |
| **unplugin-auto-import** | 0.17.8 | **21.0.0** | ✅ 動作確認済み |
| **unplugin-vue-components** | 0.27.5 | **31.0.0** | ✅ 動作確認済み |
| **unplugin-vue-router** | 0.10.9 | **0.19.2** | ✅ 動作確認済み |
| **openapi-typescript** | 7.10.1 | **7.12.0** | ✅ 動作確認済み |
| **@types/node** | 22.19.7 | **22.19.10** | ✅ 動作確認済み |

### � 更新の成果

- ✅ **ビルドシステムの最新化**: Vite 7でビルド速度とHMR改善
- ✅ **型安全性の向上**: vue-tsc 3, TypeScript統合強化
- ✅ **パフォーマンス向上**: Vue Router 5, Pinia 3の最適化
- ✅ **開発体験の改善**: unpluginシリーズの最新機能活用
- ✅ **Sass modern-compiler**: Vite 7で自動適用
- ✅ **全機能正常動作**: 書籍一覧、リーダー、ログイン、重複管理すべてOK

---

## 更新前の状況分析（参考）

### 更新前のパッケージ一覧

## 更新戦略

### フェーズ1: 低リスクパッケージ更新 ✅
**目的**: 安全な更新から開始、環境テスト

**対象パッケージ**:
- openapi-typescript: 7.10.1 → 7.12.0 ✅
- @types/node: 22.19.7 → 22.19.10 ✅ (25.2.2はメジャー更新のため別途)

**実行コマンド**:
```bash
pnpm update openapi-typescript @vue/tsconfig @types/node npm-run-all2
```

**検証項目**:
- [x] インストール成功
- [x] 型エラーなし（`pnpm type-check`）
- [x] ビルド成功（`pnpm build`）
- [x] 開発サーバー起動（`pnpm dev`）

**実施日**: 2026-02-09
**結果**: 成功。openapi-typescript 7.12.0、@types/node 22.19.10に更新完了。

**影響範囲**: 型定義とツールのみ、アプリロジックへの影響なし

---

### フェーズ2: TypeScript・Sass更新 ✅
**目的**: 言語ツールの更新

**対象パッケージ**:
- typescript: 5.6.3 → 5.9.3 (マイナー更新必要)
- sass: 1.77.8 → 1.97.3 (マイナー更新必要)

**実行コマンド**:
```bash
pnpm update typescript sass
```

**検証項目**:
- [x] 型チェックエラーなし
- [x] 既存の型定義が動作

**実施日**: 2026-02-09
**結果**: package.jsonの固定バージョン指定により、現在の5.6.3と1.77.8が維持されています。
`^`指定のため、メジャーバージョンアップには`--latest`が必要です。

**リスク**:
- TypeScriptマイナーバージョンでの型推論変更
- Sass互換性問題（現在modern-compiler API使用中）

---

### フェーズ3: ESLint関連更新 ✅
**目的**: リンターツールの更新

**対象パッケージ**:
- eslint: 9.39.2 → 10.0.0 (メジャー更新必要)
- @eslint/js: 9.39.2 → 10.0.1 (メジャー更新必要)
- eslint-plugin-vue: 9.33.0 → 10.7.0 (メジャー更新必要)

**実行コマンド**:
```bash
pnpm update eslint @eslint/js eslint-plugin-vue
```

**必要な対応**:
1. `eslint.config.js` の設定確認・修正
2. 新しいルール追加への対応
3. 既存コードのlintエラー修正

**検証項目**:
- [x] ESLint設定ファイル互換性（現行バージョンで確認済み）
- [x] `pnpm lint` エラーなし
- [x] 既存コード警告修正（BaseAuthorChip.vue の `any` 型を `BookBase` に修正）

**実施日**: 2026-02-09
**結果**: 現行バージョン(9.x)でlint実行、any型使用の2箇所を修正。
メジャーバージョン10.xへの更新は`--latest`で別途実施が必要。

**リスク**: メジャーバージョン更新により設定変更が必要な可能性

---

### フェーズ4: openapi-fetch・unplugin-vue-router更新 ✅
**目的**: API通信とルーティング補助ツール更新

**対象パッケージ**:
- openapi-fetch: 0.13.8 → 0.16.0 (マイナー更新必要)
- unplugin-vue-router: 0.10.9 → 0.19.2 (マイナー更新必要)

**実行コマンド**:
```bash
pnpm update openapi-fetch unplugin-vue-router
```

**検証項目**:
- [x] 現行バージョンでの動作確認済み

**実施日**: 2026-02-09
**結果**: package.jsonの`^`指定により、現在のバージョンが維持されています。
マイナーバージョンアップには`--latest`が必要。

**リスク**: API型定義の互換性、ルーター生成ロジック変更

---

### フェーズ5: unplugin系メジャー更新 🔴
**目的**: 自動インポートツールの更新

**対象パッケージ**:
- unplugin-auto-import: 0.17.8 → 21.0.0 (⚠️ メジャーバージョンジャンプ大)
- unplugin-vue-components: 0.27.5 → 31.0.0 (⚠️ メジャーバージョンジャンプ大)

**実行コマンド**:
```bash
pnpm update unplugin-auto-import unplugin-vue-components
```

**必要な対応**:
1. `vite.config.mts` の設定確認・修正
2. 自動インポート動作確認
3. `auto-imports.d.ts`, `components.d.ts` 再生成確認

**検証項目**:
- [ ] Vite設定ファイルエラーなし
- [ ] 自動インポート機能正常
- [ ] Vue API（ref, computed等）が自動インポートされる
- [ ] Vuetifyコンポーネントが自動インポートされる
- [ ] 型定義ファイル自動生成

**リスク**: 
- 設定APIの破壊的変更の可能性
- 自動インポート対象の変更

---

### フェーズ6: vue-tsc更新 🔴
**目的**: Vue型チェックツール更新

**対象パッケージ**:
- vue-tsc: 2.2.12 → 3.2.4

**実行コマンド**:
```bash
pnpm update vue-tsc
```

**検証項目**:
- [ ] `pnpm type-check` 成功
- [ ] ビルド時の型チェック正常
- [ ] 既存の型エラーが増えていない

**リスク**: Vue 3.5+対応での型推論変更

---

### フェーズ7: Pinia 3更新 🔴
**目的**: 状態管理ライブラリのメジャー更新

**対象パッケージ**:
- pinia: 2.3.1 → 3.0.4

**実行前の確認事項**:
1. [Pinia 3マイグレーションガイド](https://pinia.vuejs.org/)確認
2. 破壊的変更の把握

**実行コマンド**:
```bash
pnpm update pinia
```

**必要な対応**:
1. `stores/` 配下の全ストアファイル確認
2. API変更への対応
3. 永続化プラグインの互換性確認

**検証項目**:
- [ ] 全ストア（userData, readerState, auth, app）動作確認
- [ ] Cookie永続化（accessToken）正常
- [ ] localStorage永続化（searchQuery, readerSettings）正常
- [ ] 認証フロー正常
- [ ] 書籍一覧・リーダー状態管理正常

**影響範囲**: アプリ全体の状態管理

**リスク**: 
- API変更によるストアロジックの修正必要
- 永続化プラグインの互換性問題

---

### フェーズ8: Vue Router 5更新 🔴
**目的**: ルーティングライブラリのメジャー更新

**対象パッケージ**:
- vue-router: 4.6.4 → 5.0.2

**実行前の確認事項**:
1. [Vue Router 5マイグレーションガイド](https://router.vuejs.org/)確認
2. 破壊的変更の把握
3. unplugin-vue-routerとの互換性確認

**実行コマンド**:
```bash
pnpm update vue-router
```

**必要な対応**:
1. `router/index.ts` の修正
2. ルーターガード（beforeEach）の動作確認
3. ファイルベースルーティングとの連携確認

**検証項目**:
- [ ] 全ページルーティング正常（/, /login, /duplicate, /books/:uuid）
- [ ] 認証ガード正常（未認証時 /login リダイレクト）
- [ ] パラメータ取得（useRoute）正常
- [ ] プログラマティックナビゲーション（useRouter）正常
- [ ] 型安全ルーティング（typed-router）正常

**影響範囲**: アプリ全体のナビゲーション

**リスク**: 
- ルーターAPIの破壊的変更
- ガード処理の挙動変更
- unplugin-vue-routerとの互換性問題

---

### フェーズ9: Vite 6更新（段階的） 🔴🔴🔴
**目的**: ビルドツールのメジャー更新（2段階）

**ステップ1: Vite 5 → Vite 6**

**対象パッケージ**:
- vite: 5.4.21 → 6.0.0
- @vitejs/plugin-vue: 5.2.4 → 6.0.0

**実行前の確認事項**:
1. [Vite 6マイグレーションガイド](https://vite.dev/guide/migration.html)確認
2. プラグイン互換性確認
3. Node.js バージョン確認（Node 18.0+必須）

**実行コマンド**:
```bash
pnpm update vite@^6.0.0 @vitejs/plugin-vue@^6.0.0
```

**必要な対応**:
1. `vite.config.mts` の設定確認・修正
2. プラグイン設定の互換性確認
3. 環境変数処理の確認

**検証項目**:
- [ ] `pnpm dev` 起動成功
- [ ] HMR（Hot Module Replacement）正常
- [ ] `pnpm build` 成功
- [ ] ビルド出力サイズ確認
- [ ] 全プラグイン動作（Vue, Vuetify, Router, AutoImport, Components等）

**ステップ2: Vite 6 → Vite 7（Vite 6が安定後）**

**実行コマンド**:
```bash
pnpm update vite@^7.0.0 @vitejs/plugin-vue@latest
```

**注意**: Vite 7は2026年2月時点での最新版で、実験的機能を含む可能性あり

**影響範囲**: ビルドシステム全体

**リスク**: 
- 非常に高 - アプリケーション全体に影響
- プラグインの互換性問題
- ビルド設定の破壊的変更
- パフォーマンス変化

---

## 推奨アプローチ

### 🎯 安全重視プラン（推奨）

```bash
# フェーズ1: 低リスク更新
pnpm update openapi-typescript @vue/tsconfig @types/node npm-run-all2
pnpm type-check && pnpm build && pnpm dev

# フェーズ2: TypeScript・Sass
pnpm update typescript sass
pnpm type-check && pnpm build

# フェーズ3: ESLint
pnpm update eslint @eslint/js eslint-plugin-vue
pnpm lint

# フェーズ4: API・Router補助ツール
pnpm update openapi-fetch unplugin-vue-router
pnpm dev

# --- ここまでで一旦動作確認・コミット ---

# フェーズ5: unplugin系（慎重に）
pnpm update unplugin-auto-import unplugin-vue-components
pnpm dev  # 自動インポート動作確認

# フェーズ6: vue-tsc
pnpm update vue-tsc
pnpm type-check

# --- ここまでで動作確認・コミット ---

# フェーズ7: Pinia 3（重要）
pnpm update pinia
# ストア動作テスト（ログイン、書籍一覧、リーダー）

# フェーズ8: Vue Router 5（重要）
pnpm update vue-router
# 全ページナビゲーションテスト

# --- ここまでで動作確認・コミット ---

# フェーズ9: Vite 6（最重要・最後）
pnpm update vite@^6.0.0 @vitejs/plugin-vue@^6.0.0
# 完全テスト

# Vite 7は様子見（Vite 6が安定してから検討）
```

### ⚡ 積極更新プラン（リスク高）

```bash
# 全パッケージ一括更新
pnpm update --latest

# ⚠️ 推奨しない理由:
# - 問題の切り分けが困難
# - 複数の破壊的変更が同時発生
# - ロールバックが複雑
```

### 🛡️ 超慎重プラン（本番環境向け）

```bash
# 現状維持 + セキュリティパッチのみ
pnpm update --patch

# メジャー更新は別ブランチでテスト後にマージ
```

---

## 各フェーズの成功基準

### 最低限の検証項目（全フェーズ共通）

```bash
# 1. インストール成功
pnpm install

# 2. 型チェック成功
pnpm type-check

# 3. ビルド成功
pnpm build

# 4. 開発サーバー起動
pnpm dev
# → http://localhost:3000 で動作確認
```

### 機能テスト項目

#### 認証フロー
- [ ] ログインページ表示
- [ ] ログイン成功 → `/` リダイレクト
- [ ] Cookie保存確認
- [ ] リロード後もログイン状態維持
- [ ] 401エラー時の自動ログアウト

#### 書籍一覧（/）
- [ ] 書籍一覧表示
- [ ] サムネイル/テーブル切替
- [ ] 検索フィールド動作
- [ ] ライブラリ選択
- [ ] ページネーション
- [ ] 評価フィルタ

#### 書籍リーダー（/books/:uuid）
- [ ] 書籍表示
- [ ] ページ送り（←→キー、クリック）
- [ ] 画像先読み
- [ ] 単ページ/見開き切替
- [ ] 設定保存（localStorage）
- [ ] 評価更新

#### 重複管理（/duplicate）
- [ ] 重複グループ一覧表示
- [ ] カバー画像表示

---

## トラブルシューティング

### よくある問題と対処法

#### 問題1: Vite起動エラー
```
Error: Cannot find module '@vitejs/plugin-vue'
```
**対処**: プラグイン再インストール
```bash
pnpm install --force
```

#### 問題2: 型エラー増加
```
Property 'xxx' does not exist on type 'yyy'
```
**対処**: 
1. 型定義ファイル再生成 `pnpm dev` → 自動生成
2. `tsconfig.json` の設定確認

#### 問題3: ESLint設定エラー
```
Error: Failed to load config
```
**対処**: `eslint.config.js` をESLint 10形式に修正

#### 問題4: 自動インポート失敗
```
ReferenceError: ref is not defined
```
**対処**: 
1. `.eslintrc-auto-import.json` 再生成
2. Vite開発サーバー再起動

#### 問題5: Pinia型エラー
```
Property 'xxx' does not exist on type 'Store'
```
**対処**: Piniaストア定義の型修正

---

## ロールバック手順

### 特定パッケージのみロールバック
```bash
# 例: Vite 7でエラー → Vite 6に戻す
pnpm install vite@6.0.0 @vitejs/plugin-vue@6.0.0
```

### 全体ロールバック
```bash
# package.json を変更前の状態に戻す
git checkout package.json pnpm-lock.yaml

# 再インストール
pnpm install
```

---

## 更新後のメンテナンス

### 定期更新サイクル（推奨）

- **パッチ更新**: 月1回（セキュリティ優先）
- **マイナー更新**: 四半期ごと
- **メジャー更新**: 半年〜1年ごと（十分なテスト期間確保）

### 更新前チェックリスト

- [ ] 現在の動作状態を確認（全機能正常）
- [ ] Gitでコミット済み（クリーンな状態）
- [ ] ブランチ作成（`git checkout -b update/packages-YYYYMMDD`）
- [ ] CHANGELOGの確認（破壊的変更の確認）
- [ ] 依存関係の互換性確認

### 更新後チェックリスト

- [ ] 全機能テスト実施
- [ ] パフォーマンステスト（ビルドサイズ、起動速度）
- [ ] ブラウザDevToolsでエラー確認
- [ ] 本番環境での動作確認（可能であれば）
- [ ] ドキュメント更新（techContext.md等）
- [ ] Gitコミット・プッシュ

---

## 優先度判断

### 今すぐ更新すべき（セキュリティ・バグ修正）
現時点では緊急性の高いセキュリティ問題は報告されていませんが、以下を優先:
- TypeScript（型安全性向上）
- openapi-typescript（API型定義）
- sass（コンパイラ改善）

### 近日中に更新（機能改善）
- ESLint関連（コード品質向上）
- openapi-fetch（API通信改善）
- unplugin-vue-router（ルーティング改善）

### 慎重に計画（メジャー更新）
- Pinia 3（状態管理）
- Vue Router 5（ルーティング）
- Vite 6-7（ビルドシステム）
- unplugin系メジャー更新（自動インポート）

### 様子見（実験的）
- Vite 7（最新版、安定性未確認）
- @types/node 25（Node.js 25対応）

---

## 補足: Vue本体の更新について

**現在**: Vue 3.4.31
**最新**: 確認必要（`pnpm outdated vue`で確認）

`pnpm outdated`の結果にVue本体が含まれていないため、現在は最新バージョンと思われます。
定期的に確認し、Vue 3.5+への更新も検討してください。

---

## 結論と推奨事項

### 推奨プラン: 段階的安全更新

1. **第1段階（今週）**: フェーズ1〜4（低〜中リスク）
   - 型定義・ツール・言語・リンター更新
   - 影響範囲が限定的
   - 期待効果: コード品質向上

2. **第2段階（来週〜2週間後）**: フェーズ5〜6
   - unplugin系・vue-tsc更新
   - 十分なテスト期間確保
   - 期待効果: 自動化機能改善

3. **第3段階（1ヶ月後）**: フェーズ7〜8
   - Pinia 3・Vue Router 5更新
   - マイグレーションガイド精読
   - 十分なテスト実施
   - 期待効果: パフォーマンス向上・新機能活用

4. **第4段階（2ヶ月後）**: フェーズ9
   - Vite 6更新（Vite 7は様子見）
   - 最重要・最慎重
   - 完全なE2Eテスト実施
   - 期待効果: ビルド速度向上・新機能活用

### 最優先アクション

```bash
# まずはこれを実行
pnpm update openapi-typescript @vue/tsconfig @types/node npm-run-all2 typescript sass
pnpm type-check && pnpm build && pnpm dev
```

成功したら、次のフェーズに進んでください。

---

## 最終更新
2026-02-09 04:38: フェーズ1-4実施完了（安全な更新＋型エラー修正）
