<template>
  <div class="duplicate-list">
    <v-app-bar color="primary" dark density="compact" flat app>
      <v-app-bar-nav-icon @click="showDrawer = !showDrawer" />
      <v-toolbar-title>重複リスト</v-toolbar-title>
      <v-spacer />
      <v-chip v-if="!isLoading && booksList.length > 0" class="mr-2" color="info">
        {{ booksList.length }} グループ
      </v-chip>
      <v-btn icon @click="reload()">
        <v-icon>mdi-reload</v-icon>
      </v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="showDrawer" app>
      <v-list nav density="compact">
        <v-list-item>
          <v-btn class="ma-1" size="small" color="primary" block @click="serachDuplicate">
            重複検索
            <v-icon class="pl-2">
              mdi-content-duplicate
            </v-icon>
          </v-btn>
        </v-list-item>
        <v-list-item>
          <v-btn class="ma-1" size="small" block @click="toBookList">
            書籍リスト
            <v-icon class="pl-2">
              mdi-book-multiple
            </v-icon>
          </v-btn>
        </v-list-item>
      </v-list>
      <v-divider />
      <v-list nav density="compact">
        <v-list-item>
          <v-btn class="ma-1" size="small" color="error" block @click="handleLogout">
            ログアウト
            <v-icon class="pl-2">
              mdi-logout
            </v-icon>
          </v-btn>
        </v-list-item>
      </v-list>
      <v-divider class="pb-2" />
      <div class="text-subtitle-2 ml-3">
        Develop by
        <a href="https://github.com/hibiki31" class="text-blue">@hibiki31</a>
      </div>
      <div class="text-subtitle-2 ml-3">
        v{{ version }}
      </div>
      <div class="text-subtitle-2 ml-3">
        Icons made by
        <a href="https://www.flaticon.com/authors/icon-pond" title="Icon Pond" class="text-blue">Icon Pond</a>
      </div>
    </v-navigation-drawer>

    <v-main>
      <v-progress-linear v-show="isLoading" indeterminate color="primary" />

      <!-- 重複がない場合 -->
      <v-container v-if="!isLoading && booksList.length === 0" class="text-center py-10">
        <v-icon size="64" color="success">
          mdi-check-circle-outline
        </v-icon>
        <div class="text-h6 mt-4">
          重複している本は見つかりませんでした
        </div>
        <v-btn class="mt-4" color="primary" @click="serachDuplicate">
          重複検索を実行
        </v-btn>
      </v-container>

      <!-- 重複リスト -->
      <v-container v-if="!isLoading && booksList.length > 0" fluid>
        <v-expansion-panels v-model="openPanels" multiple>
          <v-expansion-panel
            v-for="(group, groupIndex) in booksList"
            :key="group.duplicate_uuid"
            class="mb-2"
          >
            <v-expansion-panel-title>
              <div class="d-flex align-center ga-3">
                <v-icon color="warning">mdi-alert-circle</v-icon>
                <span class="text-subtitle-1 font-weight-bold">
                  重複グループ #{{ groupIndex + 1 }}
                </span>
                <v-chip size="small" color="error">
                  {{ group.books.length }} 冊
                </v-chip>
                <v-chip size="small" color="grey-lighten-1">
                  {{ group.duplicate_uuid.slice(0, 8) }}
                </v-chip>
              </div>
            </v-expansion-panel-title>

            <v-expansion-panel-text>
              <v-row>
                <v-col
                  v-for="book in group.books"
                  :key="book.uuid"
                  cols="12"
                  sm="6"
                  md="4"
                  lg="3"
                >
                  <v-card
                    :class="{ 'delete-recommended-card': !isRecommended(book, group.books) }"
                    class="book-card"
                    elevation="2"
                    :color="!isRecommended(book, group.books) ? 'error-lighten-5' : undefined"
                  >
                    <!-- 削除推奨バッジ -->
                    <v-chip
                      v-if="!isRecommended(book, group.books)"
                      class="recommend-badge"
                      color="error"
                      size="small"
                      prepend-icon="mdi-delete-alert"
                    >
                      削除推奨
                    </v-chip>

                    <v-row no-gutters>
                      <!-- カバー画像 -->
                      <v-col cols="5">
                        <v-img
                          :src="getCoverURL(book.uuid)"
                          aspect-ratio="0.7"
                          cover
                          class="book-cover"
                        >
                          <template #placeholder>
                            <v-row class="fill-height ma-0" align="center" justify="center">
                              <v-progress-circular indeterminate color="grey-lighten-1" />
                            </v-row>
                          </template>
                        </v-img>
                      </v-col>

                      <!-- 本の情報 -->
                      <v-col cols="7">
                        <v-card-text class="pa-2">
                          <!-- タイトル -->
                          <div class="text-subtitle-2 font-weight-bold mb-1 text-truncate-2">
                            {{ book.title || '（タイトルなし）' }}
                          </div>

                          <!-- 著者 -->
                          <div v-if="book.authors && book.authors.length > 0" class="mb-1">
                            <v-chip
                              v-for="author in book.authors.slice(0, 2)"
                              :key="author.id"
                              size="x-small"
                              class="mr-1 mb-1"
                              color="primary"
                              variant="tonal"
                            >
                              {{ author.name }}
                            </v-chip>
                            <span v-if="book.authors.length > 2" class="text-caption text-grey">
                              +{{ book.authors.length - 2 }}
                            </span>
                          </div>

                          <!-- 出版社 -->
                          <div v-if="book.publisher?.name" class="text-caption text-grey mb-1">
                            <v-icon size="x-small">mdi-domain</v-icon>
                            {{ book.publisher.name }}
                          </div>

                          <!-- ライブラリ -->
                          <div v-if="book.library?.name || book.libraryId" class="text-caption text-grey mb-1">
                            <v-icon size="x-small">mdi-bookshelf</v-icon>
                            {{ book.library?.name || `ライブラリ ${book.libraryId}` }}
                          </div>

                          <!-- 評価 -->
                          <div class="mb-1">
                            <v-rating
                              :model-value="book.userData?.rate || book.rate || 0"
                              density="compact"
                              size="small"
                              color="amber"
                              hover
                              @update:model-value="(value) => handleRateChange(book, value)"
                            />
                            <span v-if="!book.userData?.rate && !book.rate" class="text-caption text-grey ml-1">
                              未評価
                            </span>
                          </div>

                          <!-- メタデータ -->
                          <v-divider class="my-2" />

                          <div class="metadata-section">
                            <div class="metadata-item">
                              <v-icon size="small" color="grey">mdi-file-document</v-icon>
                              <span class="text-caption">{{ fitByte(book.size) }}</span>
                            </div>
                            <div class="metadata-item">
                              <v-icon size="small" color="grey">mdi-book-open-page-variant</v-icon>
                              <span class="text-caption">{{ book.page }}p</span>
                            </div>
                            <div v-if="book.addDate" class="metadata-item">
                              <v-icon size="small" color="grey">mdi-calendar-plus</v-icon>
                              <span class="text-caption">{{ convertDateFormat(book.addDate) }}</span>
                            </div>
                            <div v-if="book.lastOpenDate" class="metadata-item">
                              <v-icon size="small" color="grey">mdi-clock-outline</v-icon>
                              <span class="text-caption">{{ convertDateFormat(book.lastOpenDate) }}</span>
                            </div>
                            <div v-if="book.readTimes" class="metadata-item">
                              <v-icon size="small" color="grey">mdi-eye</v-icon>
                              <span class="text-caption">{{ book.readTimes }}回</span>
                            </div>
                          </div>

                          <!-- ファイル名 -->
                          <v-tooltip location="top">
                            <template #activator="{ props: tooltipProps }">
                              <div
                                v-bind="tooltipProps"
                                class="text-caption text-grey mt-2 text-truncate"
                              >
                                <v-icon size="x-small">mdi-file</v-icon>
                                {{ book.file }}
                              </div>
                            </template>
                            <span>{{ book.file }}</span>
                          </v-tooltip>
                        </v-card-text>
                      </v-col>
                    </v-row>

                    <!-- アクションボタン -->
                    <v-card-actions class="pa-2 pt-0">
                      <v-btn
                        size="small"
                        variant="tonal"
                        color="primary"
                        @click="openBook(book.uuid)"
                      >
                        <v-icon size="small">mdi-book-open</v-icon>
                        開く
                      </v-btn>
                      <v-spacer />
                      <v-btn
                        size="small"
                        variant="text"
                        color="error"
                        @click="confirmDelete(book)"
                      >
                        <v-icon size="small">mdi-delete</v-icon>
                        削除
                      </v-btn>
                    </v-card-actions>
                  </v-card>
                </v-col>
              </v-row>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-container>
    </v-main>

    <!-- 削除確認ダイアログ -->
    <v-dialog v-model="deleteDialog.show" max-width="500">
      <v-card>
        <v-card-title class="d-flex align-center bg-error text-white">
          <v-icon class="mr-2">mdi-alert</v-icon>
          削除確認
        </v-card-title>
        <v-card-text class="pt-4">
          <div class="mb-3">
            <strong>以下の本を削除してもよろしいですか？</strong>
          </div>
          <v-sheet color="grey-lighten-4" class="pa-3 rounded">
            <div class="text-subtitle-2 font-weight-bold mb-2">
              {{ deleteDialog.book?.title || '（タイトルなし）' }}
            </div>
            <div class="text-caption text-grey mb-1">
              <v-icon size="small">mdi-file</v-icon>
              {{ deleteDialog.book?.file }}
            </div>
            <div class="text-caption text-grey">
              <v-icon size="small">mdi-file-document</v-icon>
              {{ deleteDialog.book ? fitByte(deleteDialog.book.size) : '' }}
              <v-icon size="small" class="ml-2">mdi-book-open-page-variant</v-icon>
              {{ deleteDialog.book?.page }}ページ
            </div>
          </v-sheet>
          <v-alert type="warning" variant="tonal" class="mt-3" density="compact">
            この操作は取り消せません
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog.show = false">
            キャンセル
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="deleteDialog.loading"
            @click="executeDelete"
          >
            削除する
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserDataStore } from '@/stores/userData'
import { apiClient } from '@/func/client'
import {
  usePushNotice,
  useGetCoverURL,
  useFitByte,
  useConvertDateFormat
} from '@/composables/utility'
import { useTitle } from '@/composables/title'

// ページタイトル設定
useTitle('重複リスト')

// 型定義
interface DuplicateBook {
  duplicate_uuid: string
  uuid: string
  size: number
  rate: number | null
  file: string
  title?: string | null
  authors?: { id: number; name: string; isFavorite: boolean }[]
  publisher?: { name: string | null; id?: number | null }
  page: number
  addDate?: string
  lastOpenDate?: string | null
  readTimes?: number | null
  libraryId?: number
  library?: { id: number; name: string }
  userData?: {
    rate: number | null
    openPage?: number | null
    readTimes?: number | null
    lastOpenDate?: string | null
  }
}

interface DuplicateGroup {
  duplicate_uuid: string
  books: DuplicateBook[]
}

// Composables
const router = useRouter()
const userDataStore = useUserDataStore()
const { pushNotice } = usePushNotice()
const { getCoverURL } = useGetCoverURL()
const { fitByte } = useFitByte()
const { convertDateFormat } = useConvertDateFormat()

// State
const showDrawer = ref(true)
const isLoading = ref(true)
const version = __APP_VERSION__
const booksList = ref<DuplicateGroup[]>([])
const openPanels = ref<number[]>([])

const deleteDialog = reactive({
  show: false,
  loading: false,
  book: null as DuplicateBook | null
})

/**
 * 重複検索を実行
 */
const serachDuplicate = async () => {
  try {
    const { error } = await apiClient.PATCH('/media/library', {
      body: { state: 'sim_all' }
    })
    if (error) throw error
    pushNotice('重複の検索を開始しました', 'success')
  } catch {
    pushNotice('重複の検索に失敗しました', 'error')
  }
}

/**
 * データ再読み込み
 */
const reload = async () => {
  isLoading.value = true
  try {
    const { data, error } = await apiClient.GET('/media/books/duplicate')
    if (error) throw error
    booksList.value = (data as unknown as DuplicateGroup[]) || []
    // 全ての重複グループをデフォルトで開く
    openPanels.value = booksList.value.map((_, index) => index)
  } catch {
    pushNotice('データの読み込みに失敗しました', 'error')
  } finally {
    isLoading.value = false
  }
}

/**
 * 評価を変更
 */
const handleRateChange = async (book: DuplicateBook, value: number | string) => {
  const rate = Number(value)

  try {
    const { error } = await apiClient.PUT('/api/books/user-data', {
      body: {
        uuids: [book.uuid],
        rate: rate
      }
    })
    if (error) throw error

    // ローカルデータを更新
    if (!book.userData) {
      book.userData = { rate: null, openPage: null, readTimes: null, lastOpenDate: null }
    }
    book.userData.rate = rate
    book.rate = rate

    pushNotice('評価を更新しました', 'success')
  } catch {
    pushNotice('評価の更新に失敗しました', 'error')
  }
}

/**
 * おすすめを判定
 * 評価が最も高い、または評価が同じ場合はファイルサイズが大きいものを推奨
 */
const isRecommended = (book: DuplicateBook, books: DuplicateBook[]): boolean => {
  // 評価の最大値を取得（userDataの評価も考慮）
  const getRate = (b: DuplicateBook) => b.userData?.rate || b.rate || 0
  const maxRate = Math.max(...books.map(b => getRate(b)))

  // 評価が最大値でない場合は推奨しない
  if (getRate(book) < maxRate) {
    return false
  }

  // 評価が最大値の本を取得
  const maxRatedBooks = books.filter(b => getRate(b) === maxRate)

  // 評価が最大値の本が複数ある場合、ファイルサイズが最大のものを推奨
  if (maxRatedBooks.length > 1) {
    const maxSize = Math.max(...maxRatedBooks.map(b => b.size))
    return book.size === maxSize && getRate(book) === maxRate
  }

  // 評価が最大値の本が1つだけの場合、それを推奨
  return true
}

/**
 * 本を開く（別タブ）
 */
const openBook = (uuid: string) => {
  const url = router.resolve({ path: `/books/${uuid}` }).href
  window.open(url, '_blank')
}

/**
 * 削除確認ダイアログを表示
 */
const confirmDelete = (book: DuplicateBook) => {
  deleteDialog.book = book
  deleteDialog.show = true
}

/**
 * 削除を実行
 */
const executeDelete = async () => {
  if (!deleteDialog.book) return

  deleteDialog.loading = true
  try {
    const { error } = await apiClient.DELETE('/api/books/{book_uuid}', {
      params: { path: { book_uuid: deleteDialog.book.uuid } }
    })
    if (error) throw error

    pushNotice('削除しました', 'success')
    deleteDialog.show = false
    deleteDialog.book = null

    // データを再読み込み
    await reload()
  } catch {
    pushNotice('削除に失敗しました', 'error')
  } finally {
    deleteDialog.loading = false
  }
}

/**
 * 書籍リストへ移動
 */
const toBookList = () => {
  router.push('/')
}

/**
 * ログアウト処理
 */
const handleLogout = () => {
  userDataStore.logout()
  pushNotice('ログアウトしました', 'success')
  router.push('/login')
}

// 初期化
onMounted(() => {
  reload()
})
</script>

<style scoped>
.duplicate-list {
  height: 100vh;
}

.book-card {
  height: 100%;
  position: relative;
  transition: all 0.3s ease;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2) !important;
}

.delete-recommended-card {
  border: 2px solid #f44336;
}

.recommend-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 1;
}

.book-cover {
  border-radius: 4px 0 0 4px;
}

.text-truncate-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.3;
  max-height: 2.6em;
}

.metadata-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ダークモード対応 */
.v-theme--dark .book-card {
  background-color: #1e1e1e;
}

.v-theme--dark .delete-recommended-card {
  background-color: #3a1a1a;
}
</style>
