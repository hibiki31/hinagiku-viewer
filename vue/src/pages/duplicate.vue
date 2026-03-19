<route lang="json">
{ "meta": { "layout": "main" } }
</route>

<template>
  <!-- AppBarへのアクション注入 -->
  <Teleport to="#appbar-actions">
    <v-chip v-if="!isLoading && totalCount > 0" class="mr-2" color="info">
      {{ totalCount }} グループ
    </v-chip>
    <v-btn
      v-if="selectedBooks.length > 0"
      color="error"
      variant="flat"
      class="mr-2"
      @click="confirmBulkDelete"
    >
      <v-icon class="mr-1">mdi-delete</v-icon>
      選択を削除 ({{ selectedBooks.length }})
    </v-btn>
    <v-btn icon variant="plain" @click="reload()">
      <v-icon>mdi-reload</v-icon>
    </v-btn>
  </Teleport>

  <!-- サイドバーへのコンテンツ注入 -->
  <Teleport to="#sidebar-extra-content">
    <v-list nav density="comfortable">
      <v-list-subheader>操作</v-list-subheader>
      <v-list-item
        prepend-icon="mdi-magnify"
        title="重複検索を実行"
        @click="serachDuplicate"
      />
    </v-list>
    <v-divider />
  </Teleport>

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
      <!-- ページネーション（上部） -->
      <v-row class="mb-4" align="center" justify="space-between">
        <v-col cols="auto">
          <v-select
            :model-value="itemsPerPage"
            :items="[5, 10, 20, 50]"
            label="表示件数"
            density="compact"
            style="width: 120px"
            hide-details
            @update:model-value="onItemsPerPageChange"
          />
        </v-col>
        <v-col cols="auto">
          <div class="text-caption text-grey">
            全 {{ totalCount }} グループ中 {{ (page - 1) * itemsPerPage + 1 }}-{{ Math.min(page * itemsPerPage, totalCount) }} を表示
          </div>
        </v-col>
      </v-row>

      <v-expansion-panels v-model="openPanels" multiple>
        <v-expansion-panel
          v-for="(group, groupIndex) in booksList"
          :key="group.duplicate_uuid"
          class="mb-2"
        >
          <v-expansion-panel-title>
            <div class="d-flex align-center ga-3 flex-wrap flex-grow-1">
              <v-checkbox
                :model-value="isGroupAllSelected(group)"
                :indeterminate="isGroupPartiallySelected(group)"
                hide-details
                density="compact"
                @click.stop
                @update:model-value="(val) => toggleGroupSelection(group, !!val)"
              />
              <v-icon color="warning">
                mdi-alert-circle
              </v-icon>
              <span class="text-subtitle-1 font-weight-bold">
                重複グループ #{{ groupIndex + 1 }}
              </span>
              <v-chip size="small" color="error">
                {{ group.books.length }} 冊
              </v-chip>
              <v-chip size="small" color="grey-lighten-1">
                {{ group.duplicate_uuid.slice(0, 8) }}
              </v-chip>
              <v-spacer />
              <v-btn
                size="small"
                variant="tonal"
                color="secondary"
                prepend-icon="mdi-link-off"
                class="mr-2"
                @click.stop="confirmExcludeGroup(group)"
              >
                重複でないとマーク
              </v-btn>
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
                        <div class="d-flex align-center mb-2">
                          <v-checkbox
                            :model-value="isBookSelected(book.uuid)"
                            hide-details
                            density="compact"
                            color="primary"
                            @update:model-value="(val) => toggleBookSelection(book.uuid, !!val)"
                          />
                        </div>

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

                        <div v-if="book.publisher?.name" class="text-caption text-grey mb-1">
                          <v-icon size="x-small">mdi-domain</v-icon>
                          {{ book.publisher.name }}
                        </div>

                        <div v-if="book.library?.name || book.libraryId" class="text-caption text-grey mb-1">
                          <v-icon size="x-small">mdi-bookshelf</v-icon>
                          {{ book.library?.name || `ライブラリ ${book.libraryId}` }}
                        </div>

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

                        <div class="text-caption text-grey mt-2 filename-display">
                          <v-icon size="x-small">mdi-file</v-icon>
                          {{ book.file }}
                        </div>
                      </v-card-text>
                    </v-col>
                  </v-row>

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

      <!-- ページネーション（下部） -->
      <v-row v-if="totalCount > itemsPerPage" class="mt-6" justify="center">
        <v-col cols="auto">
          <v-pagination
            :model-value="page"
            :length="Math.ceil(totalCount / itemsPerPage)"
            :total-visible="7"
            @update:model-value="onPageChange"
          />
        </v-col>
      </v-row>
    </v-container>
  </v-main>

  <!-- 重複除外確認ダイアログ -->
  <v-dialog v-model="excludeGroupDialog.show" max-width="560">
    <v-card>
      <v-card-title class="d-flex align-center bg-secondary text-white">
        <v-icon class="mr-2">mdi-link-off</v-icon>
        重複でないとマーク
      </v-card-title>
      <v-card-text class="pt-4">
        <div class="mb-3">
          <strong>このグループの本を「重複でない」として除外しますか？</strong>
        </div>
        <v-alert type="info" variant="tonal" density="compact" class="mb-3">
          グループ内の全ペア（{{ excludeGroupDialog.pairCount }} ペア）を除外リストに登録します。<br>
          除外後は重複リストに表示されなくなります。
        </v-alert>
        <v-list density="compact" class="bg-grey-lighten-4 rounded">
          <v-list-item
            v-for="book in excludeGroupDialog.books"
            :key="book.uuid"
            :subtitle="book.file"
          >
            <template #prepend>
              <v-icon size="small" color="primary">mdi-book</v-icon>
            </template>
            <template #title>
              {{ book.title || '（タイトルなし）' }}
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="excludeGroupDialog.show = false">
          キャンセル
        </v-btn>
        <v-btn
          color="secondary"
          variant="flat"
          :loading="excludeGroupDialog.loading"
          @click="executeExcludeGroup"
        >
          除外する
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- 一括削除確認ダイアログ -->
  <v-dialog v-model="bulkDeleteDialog.show" max-width="600">
    <v-card>
      <v-card-title class="d-flex align-center bg-error text-white">
        <v-icon class="mr-2">mdi-alert</v-icon>
        一括削除確認
      </v-card-title>
      <v-card-text class="pt-4">
        <div class="mb-3">
          <strong>選択した {{ selectedBooks.length }} 冊の本を削除してもよろしいですか？</strong>
        </div>
        <v-alert type="warning" variant="tonal" density="compact">
          この操作は取り消せません
        </v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="bulkDeleteDialog.show = false">
          キャンセル
        </v-btn>
        <v-btn
          color="error"
          variant="flat"
          :loading="bulkDeleteDialog.loading"
          @click="executeBulkDelete"
        >
          {{ selectedBooks.length }}冊削除する
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

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
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
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

import type { components } from '@/api'

type ApiDuplicateBook = components['schemas']['DuplicateBook']
type ApiDuplicateListResponse = components['schemas']['DuplicateListResponse']

interface DuplicateBook extends ApiDuplicateBook {
  duplicate_uuid: string
  title?: string | null
  authors?: { id: number; name: string; isFavorite: boolean }[]
  publisher?: { name: string | null; id?: number | null }
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

const router = useRouter()
const { pushNotice } = usePushNotice()
const { getCoverURL } = useGetCoverURL()
const { fitByte } = useFitByte()
const { convertDateFormat } = useConvertDateFormat()

const isLoading = ref(true)
const booksList = ref<DuplicateGroup[]>([])
const openPanels = ref<number[]>([])

// ページネーション
const page = ref(1)
const itemsPerPage = ref(10)
const totalCount = ref(0)

const deleteDialog = reactive({
  show: false,
  loading: false,
  book: null as DuplicateBook | null
})

// 一括削除用の選択状態
const selectedBooks = ref<string[]>([])

// 一括削除ダイアログ
const bulkDeleteDialog = reactive({
  show: false,
  loading: false
})

// チェックボックス操作
const isBookSelected = (uuid: string) => {
  return selectedBooks.value.includes(uuid)
}

const toggleBookSelection = (uuid: string, selected: boolean) => {
  if (selected) {
    if (!selectedBooks.value.includes(uuid)) {
      selectedBooks.value.push(uuid)
    }
  } else {
    selectedBooks.value = selectedBooks.value.filter(id => id !== uuid)
  }
}

const isGroupAllSelected = (group: DuplicateGroup) => {
  return group.books.every(book => selectedBooks.value.includes(book.uuid))
}

const isGroupPartiallySelected = (group: DuplicateGroup) => {
  const selectedCount = group.books.filter(book => selectedBooks.value.includes(book.uuid)).length
  return selectedCount > 0 && selectedCount < group.books.length
}

const toggleGroupSelection = (group: DuplicateGroup, selected: boolean) => {
  if (selected) {
    // グループの全ての本を選択
    group.books.forEach(book => {
      if (!selectedBooks.value.includes(book.uuid)) {
        selectedBooks.value.push(book.uuid)
      }
    })
  } else {
    // グループの全ての本を選択解除
    const uuids = group.books.map(book => book.uuid)
    selectedBooks.value = selectedBooks.value.filter(id => !uuids.includes(id))
  }
}

const confirmBulkDelete = () => {
  bulkDeleteDialog.show = true
}

const executeBulkDelete = async () => {
  bulkDeleteDialog.loading = true
  try {
    // 各本を順次削除
    const deletePromises = selectedBooks.value.map(uuid =>
      apiClient.DELETE('/api/books/{book_uuid}', {
        params: { path: { book_uuid: uuid } }
      })
    )

    const results = await Promise.allSettled(deletePromises)
    const successCount = results.filter(r => r.status === 'fulfilled').length
    const failCount = results.filter(r => r.status === 'rejected').length

    if (failCount > 0) {
      pushNotice(`${successCount}件削除しました（${failCount}件失敗）`, 'warn')
    } else {
      pushNotice(`${successCount}件削除しました`, 'success')
    }

    selectedBooks.value = []
    bulkDeleteDialog.show = false
    await reload()
  } catch {
    pushNotice('削除に失敗しました', 'error')
  } finally {
    bulkDeleteDialog.loading = false
  }
}

const serachDuplicate = async () => {
  try {
    const { error } = await apiClient.POST('/api/tasks', {
      body: { taskType: 'sim_all' }
    })
    if (error) throw error
    pushNotice('重複の検索を開始しました', 'success')
  } catch {
    pushNotice('重複の検索に失敗しました', 'error')
  }
}

const reload = async () => {
  isLoading.value = true
  try {
    const offset = (page.value - 1) * itemsPerPage.value
    const { data, error } = await apiClient.GET('/media/books/duplicate', {
      params: {
        query: {
          limit: itemsPerPage.value,
          offset: offset
        }
      }
    })
    if (error) throw error

    // 新しいAPI形式に対応
    if (data && typeof data === 'object' && 'items' in data && 'count' in data) {
      // ページネーション対応のレスポンス形式
      const response = data as ApiDuplicateListResponse
      // APIのduplicateUuidをduplicate_uuidに変換
      booksList.value = (response.items || []).map(group => ({
        duplicate_uuid: group.duplicateUuid,
        books: group.books.map(book => ({
          ...book,
          duplicate_uuid: group.duplicateUuid
        }))
      }))
      totalCount.value = response.count || 0
    } else if (Array.isArray(data)) {
      // 旧API形式（後方互換性）
      booksList.value = data as unknown as DuplicateGroup[]
      totalCount.value = booksList.value.length
    } else {
      booksList.value = []
      totalCount.value = 0
    }

    openPanels.value = booksList.value.map((_, index) => index)
  } catch {
    pushNotice('データの読み込みに失敗しました', 'error')
  } finally {
    isLoading.value = false
  }
}

const onPageChange = (newPage: number) => {
  page.value = newPage
  reload()
}

const onItemsPerPageChange = (newItemsPerPage: number) => {
  itemsPerPage.value = newItemsPerPage
  page.value = 1
  reload()
}

const handleRateChange = async (book: DuplicateBook, value: number | string) => {
  const rate = Number(value)
  try {
    const { error } = await apiClient.PUT('/api/books/user-data', {
      body: { uuids: [book.uuid], rate: rate }
    })
    if (error) throw error
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

const isRecommended = (book: DuplicateBook, books: DuplicateBook[]): boolean => {
  const getRate = (b: DuplicateBook) => b.userData?.rate || b.rate || 0
  const maxRate = Math.max(...books.map(b => getRate(b)))
  if (getRate(book) < maxRate) return false
  const maxRatedBooks = books.filter(b => getRate(b) === maxRate)
  if (maxRatedBooks.length > 1) {
    const maxSize = Math.max(...maxRatedBooks.map(b => b.size))
    return book.size === maxSize && getRate(book) === maxRate
  }
  return true
}

const openBook = (uuid: string) => {
  const url = router.resolve({ path: `/books/${uuid}` }).href
  window.open(url, '_blank')
}

// 重複除外ダイアログ
const excludeGroupDialog = reactive({
  show: false,
  loading: false,
  group: null as DuplicateGroup | null,
  books: [] as DuplicateBook[],
  pairCount: 0
})

const confirmExcludeGroup = (group: DuplicateGroup) => {
  const n = group.books.length
  excludeGroupDialog.group = group
  excludeGroupDialog.books = group.books
  excludeGroupDialog.pairCount = (n * (n - 1)) / 2
  excludeGroupDialog.show = true
}

const executeExcludeGroup = async () => {
  if (!excludeGroupDialog.group) return
  excludeGroupDialog.loading = true
  try {
    const books = excludeGroupDialog.group.books
    // 全ペアの組み合わせを生成して除外登録
    const pairs: { bookUuid1: string; bookUuid2: string }[] = []
    for (let i = 0; i < books.length; i++) {
      for (let j = i + 1; j < books.length; j++) {
        pairs.push({ bookUuid1: books[i].uuid, bookUuid2: books[j].uuid })
      }
    }
    const results = await Promise.allSettled(
      pairs.map(pair =>
        apiClient.POST('/media/books/duplicate/exclude', { body: pair })
      )
    )
    const failCount = results.filter(r => r.status === 'rejected').length
    if (failCount > 0) {
      pushNotice(`一部の除外登録に失敗しました（${failCount}件失敗）`, 'warn')
    } else {
      pushNotice('重複でないとマークしました', 'success')
    }
    excludeGroupDialog.show = false
    excludeGroupDialog.group = null
    await reload()
  } catch {
    pushNotice('除外登録に失敗しました', 'error')
  } finally {
    excludeGroupDialog.loading = false
  }
}

const confirmDelete = (book: DuplicateBook) => {
  deleteDialog.book = book
  deleteDialog.show = true
}

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
    await reload()
  } catch {
    pushNotice('削除に失敗しました', 'error')
  } finally {
    deleteDialog.loading = false
  }
}

onMounted(() => {
  reload()
})
</script>

<style scoped>
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

.filename-display {
  word-break: break-all;
  white-space: normal;
  line-height: 1.4;
}

.v-theme--dark .book-card {
  background-color: #1e1e1e;
}

.v-theme--dark .delete-recommended-card {
  background-color: #3a1a1a;
}
</style>
