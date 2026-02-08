# System Patterns - Vue 3 フロントエンド

## 重要: プロジェクト全体のパターンを参照

このファイルは `vue/` ディレクトリのVue 3フロントエンド固有のシステムパターンです。
**プロジェクト全体の情報は `/workspaces/hinagiku-viewer/memory-bank/systemPatterns.md` を参照してください。**

プロジェクトルートのsystemPatternsには以下が含まれます：
- システム全体のアーキテクチャ（マイクロサービス構成）
- データベース設計パターン
- APIアーキテクチャパターン
- ファイル処理パターン
- タスクキューパターン
- セキュリティパターン
- デプロイパターン

## Vue 3フロントエンドアーキテクチャ

### ファイルベースルーティング

`unplugin-vue-router`により`src/pages/`配下の`.vue`ファイルからルートを自動生成：

```
src/pages/
├── index.vue           → /                （書籍一覧）
├── login.vue           → /login           （ログイン）
├── duplicate.vue       → /duplicate       （重複管理）
└── books/
    └── [uuid].vue      → /books/:uuid     （書籍リーダー）
```

**パターン**: 
- ブラケット記法 `[param]` で動的パラメータ
- ネストしたディレクトリ構造がURLパスに反映
- `typed-router.d.ts` で型安全なルーティング

### レイアウトシステム

`vite-plugin-vue-layouts`で`src/layouts/`のレイアウトを適用：

```
src/layouts/
└── default.vue         # デフォルトレイアウト
```

**パターン**: 
- 全ページでデフォルトレイアウトを使用
- レイアウト内で `<router-view />` でページを表示
- 必要に応じてページ単位でレイアウトをカスタマイズ可能

### コンポーネント設計パターン

#### 基本構造
```vue
<script setup lang="ts">
// 自動インポート: ref, computed, watch, useRoute, useRouter等
import { api } from '@/func/axios'  // 手動インポート必要
import type { BookBase } from '@/api'  // 型インポート

const props = defineProps<{ uuid: string }>()
const emit = defineEmits<{ submit: [value: string] }>()

// リアクティブ変数
const count = ref(0)
const doubled = computed(() => count.value * 2)
</script>

<template>
  <!-- Vuetifyコンポーネントは自動インポート -->
  <v-card>
    <v-card-title>{{ count }}</v-card-title>
  </v-card>
</template>
```

#### ダイアログパターン
```vue
<!-- 親コンポーネント -->
<script setup lang="ts">
const dialogRef = ref()
const openDialog = () => dialogRef.value?.openDialog()
</script>

<template>
  <SearchDialog ref="dialogRef" @search="handleSearch" />
  <v-btn @click="openDialog">開く</v-btn>
</template>

<!-- ダイアログコンポーネント -->
<script setup lang="ts">
const dialog = ref(false)
const openDialog = () => { dialog.value = true }
defineExpose({ openDialog })
</script>

<template>
  <v-dialog v-model="dialog">
    <!-- コンテンツ -->
  </v-dialog>
</template>
```

### 状態管理パターン（Pinia）

#### ストア構造
```
stores/
├── index.ts            # ストアエクスポート
├── userData.ts         # 認証状態（Cookie永続化）
├── readerState.ts      # 書籍一覧・リーダー状態（localStorage永続化）
├── auth.ts             # 認証設定
└── app.ts              # アプリ全般
```

#### 認証ストア（userData.ts）パターン
```typescript
export const useUserDataStore = defineStore('userData', {
  state: () => ({
    isLoaded: false,
    isAuthed: false,
    accessToken: '',
    username: '',
    isAdmin: false,
  }),
  actions: {
    // Cookie + Axiosヘッダー設定
    authenticaitonSuccessful(token: string) {
      this.accessToken = token
      this.isAuthed = true
      Cookies.set('accessToken', token, { expires: 365 })
      api.defaults.headers.common.Authorization = `Bearer ${token}`
    },
    // Cookie + Axiosヘッダー削除
    authenticaitonFail() {
      this.accessToken = ''
      this.isAuthed = false
      Cookies.remove('accessToken')
      delete api.defaults.headers.common.Authorization
    },
  },
})
```

#### リーダーストア（readerState.ts）パターン
```typescript
export const useReaderStateStore = defineStore('readerState', {
  state: () => ({
    searchQuery: localStorage.getItem('searchQuery') || '',
    booksList: [] as BookBase[],
    booksCount: 0,
    // ...
  }),
  actions: {
    setSearchQuery(query: string) {
      this.searchQuery = query
      localStorage.setItem('searchQuery', query)  // 永続化
    },
  },
})
```

### API通信パターン（2クライアント共存）

#### Axiosクライアント（現在のメイン）
```typescript
// func/axios.ts
import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_APP_API_HOST || '',
})

// 使用例
import { api } from '@/func/axios'
const response = await api.get('/api/books')
```

**App.vueでインターセプター設定**:
```typescript
// 401応答 → 自動ログアウト
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      userDataStore.authenticaitonFail()
      window.location.reload()
    }
    return Promise.reject(error)
  }
)
```

#### openapi-fetchクライアント（型安全・移行先）
```typescript
// func/client.ts
import createClient from 'openapi-fetch'
import type { paths } from '@/api'

export const client = createClient<paths>({
  baseUrl: import.meta.env.VITE_API_ENDPOINT,
})

// Bearerトークンミドルウェア
client.use({
  onRequest({ request }) {
    const token = Cookies.get('accessToken')
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`)
    }
    return request
  },
})

// 使用例
const { data, error } = await client.GET('/api/books', {
  params: { query: { limit: 10, offset: 0 } }
})
```

**移行方針**: 新規コードはopenapi-fetchを優先、既存Axiosは段階的に移行

### 認証フローパターン

#### App.vueマウント時
```typescript
onMounted(async () => {
  // 1. Cookie確認
  const token = Cookies.get('accessToken')
  if (!token) {
    userDataStore.authenticaitonFail()
    return
  }

  // 2. トークン検証
  try {
    const { data } = await api.get('/api/auth/validate')
    userDataStore.authenticaitonSuccessful(token)
    userDataStore.username = data.username
    userDataStore.isAdmin = data.is_admin
    
    // 3. /loginにいる場合は/にリダイレクト
    if (route.path === '/login') {
      router.push('/')
    }
  } catch {
    userDataStore.authenticaitonFail()
  }
  
  userDataStore.isLoaded = true
})
```

#### ルーターガード
```typescript
router.beforeEach((to, from) => {
  const userDataStore = useUserDataStore()
  
  // 認証済み + /login → / にリダイレクト
  if (userDataStore.isAuthed && to.path === '/login') {
    return '/'
  }
  
  // 未認証 + /login以外 → /login にリダイレクト
  if (!userDataStore.isAuthed && to.path !== '/login') {
    return '/login'
  }
})
```

### 書籍リーダーの先読みパターン

```typescript
// pages/books/[uuid].vue
const getDLoadingPage = async () => {
  const start = currentPage.value
  const end = start + cachePage.value
  
  for (let i = start; i < end; i++) {
    if (books.value[i]?.isLoad) continue
    
    // 並列ロード数制限
    if (loadingCount.value >= mulchLoad.value) break
    
    loadingCount.value++
    
    try {
      const blob = await api.get(`/api/media/${uuid}/${i}`, {
        responseType: 'blob'
      })
      books.value[i] = {
        src: URL.createObjectURL(blob.data),
        isLoad: true
      }
    } catch {
      // 1秒後にリトライ
      await sleep(1000)
      loadingCount.value--
      getDLoadingPage()
      return
    }
    
    loadingCount.value--
  }
}
```

**パターン**:
- `cachePage`: 先読みページ数
- `mulchLoad`: 並列ロード数
- Blob取得 → `URL.createObjectURL()` でimgタグに設定
- 設定はlocalStorage "readerSettings" に永続化

### Composablesパターン

#### 通知（utility.ts）
```typescript
export const usePushNotice = () => {
  const { notify } = useNotification()
  
  const pushNotice = (message: string, type: string = 'success') => {
    notify({ 
      text: message, 
      type 
    })
  }
  
  return { pushNotice }
}

// 使用例
const { pushNotice } = usePushNotice()
pushNotice('保存しました', 'success')
```

#### カバー画像URL生成（utility.ts）
```typescript
export const useGetCoverURL = () => {
  const getCoverURL = (uuid: string, height: number = 300) => {
    return `${import.meta.env.VITE_APP_API_HOST}/api/media/cover/${uuid}?height=${height}`
  }
  
  return { getCoverURL }
}

// 使用例
const { getCoverURL } = useGetCoverURL()
const coverUrl = getCoverURL(book.uuid, 400)
```

### localStorage永続化パターン

#### 検索条件（stores/readerState.ts）
```typescript
state: () => ({
  searchQuery: localStorage.getItem('searchQuery') || '',
}),
actions: {
  setSearchQuery(query: string) {
    this.searchQuery = query
    localStorage.setItem('searchQuery', query)
  },
}
```

#### リーダー設定（pages/books/[uuid].vue）
```typescript
interface ReaderSettings {
  cachePage: number
  mulchLoad: number
  twoPage: boolean
  customHeight: boolean
  pageHeight: number
}

onMounted(() => {
  const saved = localStorage.getItem('readerSettings')
  if (saved) {
    const settings = JSON.parse(saved) as ReaderSettings
    cachePage.value = settings.cachePage
    // ...他の設定を復元
  }
})

watch([cachePage, mulchLoad, twoPage, customHeight, pageHeight], () => {
  localStorage.setItem('readerSettings', JSON.stringify({
    cachePage: cachePage.value,
    mulchLoad: mulchLoad.value,
    twoPage: twoPage.value,
    customHeight: customHeight.value,
    pageHeight: pageHeight.value,
  }))
})
```

## 設計上の重要な決定（Vue 3固有）

### 1. ファイルベースルーティング
**決定**: `unplugin-vue-router`でファイルベースルーティング
**理由**: 
- ルーター定義の手間削減
- 型安全なルーティング
- コロケーション向上

### 2. 自動インポート
**決定**: Vue API, Vuetifyコンポーネント、カスタムコンポーネントを自動インポート
**理由**: 
- importステートメント削減
- 開発効率向上
- 型定義自動生成

### 3. Pinia状態管理
**決定**: Vuexの代わりにPiniaを使用
**理由**: 
- Vue 3公式推奨
- TypeScript完全サポート
- シンプルなAPI

### 4. localStorage活用
**決定**: 検索条件とリーダー設定をlocalStorageに永続化
**理由**: 
- ユーザー体験向上（設定保存）
- バックエンド負荷軽減
- オフライン対応

### 5. 2クライアント共存
**決定**: AxiosとopenAPIクライアントを共存させる
**理由**: 
- 既存コードの段階的移行
- 型安全性を段階的に導入
- リスク分散

## パフォーマンス最適化パターン（Vue 3固有）

### 1. 画像先読み
- 現在ページから指定ページ数先まで先読み
- 並列ロード数を制限して負荷分散
- Blob + createObjectURLで高速表示

### 2. コンポーネント遅延ロード
```typescript
const HeavyComponent = defineAsyncComponent(() => 
  import('@/components/HeavyComponent.vue')
)
```

### 3. v-showとv-ifの使い分け
- 頻繁に切り替わる要素: `v-show`
- 条件によって描画される要素: `v-if`

## 最終更新日
2026-02-08: Vue 3メモリーバンク構造化
