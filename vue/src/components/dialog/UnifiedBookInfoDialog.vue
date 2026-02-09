<template>
  <v-dialog v-model="dialogState" max-width="900" scrollable>
    <v-card>
      <!-- ヘッダー -->
      <v-card-title class="d-flex align-center pa-4 bg-primary">
        <v-icon class="mr-2" color="white">
          mdi-book-open-variant
        </v-icon>
        <span class="text-white text-h6">本の情報</span>
        <v-spacer />
        <v-btn icon variant="text" @click="dialogState = false">
          <v-icon color="white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- タブナビゲーション -->
      <v-tabs v-model="currentTab" color="primary" align-tabs="center">
        <v-tab value="info">
          <v-icon start>mdi-information</v-icon>
          基本情報
        </v-tab>
        <v-tab v-if="showReaderSettings" value="reader">
          <v-icon start>mdi-book-open-page-variant</v-icon>
          リーダー設定
        </v-tab>
        <v-tab value="details">
          <v-icon start>mdi-file-document-outline</v-icon>
          詳細情報
        </v-tab>
      </v-tabs>

      <v-divider />

      <!-- タブコンテンツ -->
      <v-card-text style="max-height: 600px; overflow-y: auto;" class="pa-0">
        <v-window v-model="currentTab">
          <!-- 基本情報タブ -->
          <v-window-item value="info" class="pa-3">
            <v-list lines="one" density="compact">
              <!-- タイトル -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="primary" size="32">
                    <v-icon color="white" size="small">mdi-book</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>
                  <v-text-field
                    v-model="bookData.title"
                    density="compact"
                    variant="outlined"
                    hide-details
                    placeholder="タイトルを入力"
                    @blur="handleTitleChange"
                  />
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">タイトル</v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- 著者 -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="blue-grey" size="32">
                    <v-icon color="white" size="small">mdi-account</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>
                  <v-combobox
                    v-model="authorNames"
                    chips
                    multiple
                    density="compact"
                    variant="outlined"
                    hide-details
                    :placeholder="authorNames.length === 0 ? '著者を追加してください' : '著者を追加'"
                    closable-chips
                    @update:model-value="handleAuthorsChange"
                  >
                    <template #chip="{ props, item }">
                      <v-chip
                        v-bind="props"
                        :text="String(item.value || item.raw || item)"
                        size="x-small"
                        closable
                      />
                    </template>
                  </v-combobox>
                  <div v-if="authorNames.length === 0 && bookData.authors && bookData.authors.length > 0" class="text-caption text-warning mt-1">
                    ⚠️ 著者データはありますが名前が未設定です
                  </div>
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">著者</v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- 出版社 -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="teal" size="32">
                    <v-icon color="white" size="small">mdi-domain</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>
                  <v-combobox
                    v-model="publisherName"
                    density="compact"
                    variant="outlined"
                    hide-details
                    placeholder="出版社を入力"
                    @blur="handlePublisherChange"
                  />
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">出版社</v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- ページ数・サイズ -->
              <v-list-item class="px-2 py-1">
                <v-row dense class="align-center">
                  <v-col cols="6" class="d-flex align-center">
                    <v-avatar color="orange" size="32" class="mr-2">
                      <v-icon color="white" size="small">mdi-file-document</v-icon>
                    </v-avatar>
                    <div>
                      <div class="text-subtitle-2">{{ bookData.page }}</div>
                      <div class="text-caption text-medium-emphasis">ページ数</div>
                    </div>
                  </v-col>
                  <v-col cols="6" class="d-flex align-center">
                    <v-avatar color="deep-purple" size="32" class="mr-2">
                      <v-icon color="white" size="small">mdi-harddisk</v-icon>
                    </v-avatar>
                    <div>
                      <div class="text-subtitle-2">{{ formatFileSize(bookData.size || 0) }}</div>
                      <div class="text-caption text-medium-emphasis">ファイルサイズ</div>
                    </div>
                  </v-col>
                </v-row>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- タグ -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="pink" size="32">
                    <v-icon color="white" size="small">mdi-tag-multiple</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>
                  <v-combobox
                    v-model="tagNames"
                    chips
                    multiple
                    density="compact"
                    variant="outlined"
                    hide-details
                    placeholder="タグを追加"
                    closable-chips
                    @update:model-value="handleTagsChange"
                  >
                    <template #chip="{ props, item }">
                      <v-chip
                        v-bind="props"
                        :text="String(item.value || item.raw || item)"
                        size="x-small"
                        color="pink"
                        variant="tonal"
                        closable
                      />
                    </template>
                  </v-combobox>
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">タグ</v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- 評価 -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="amber" size="32">
                    <v-icon color="white" size="small">mdi-star</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>
                  <div class="d-flex align-center py-1">
                    <v-rating
                      :model-value="bookData.userData?.rate ?? undefined"
                      size="small"
                      color="amber"
                      active-color="amber"
                      hover
                      density="compact"
                      @update:model-value="handleRateChange"
                    />
                    <span class="text-caption text-medium-emphasis ml-2">
                      {{ bookData.userData?.rate ? `${bookData.userData.rate} / 5` : '未評価' }}
                    </span>
                  </div>
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">評価</v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- ライブラリ -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="primary" size="32">
                    <v-icon color="white" size="small">mdi-bookshelf</v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>
                  <v-select
                    v-model="bookData.libraryId"
                    :items="libraryList"
                    item-title="name"
                    item-value="id"
                    density="compact"
                    variant="outlined"
                    hide-details
                    @update:model-value="handleLibraryChange"
                  />
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">ライブラリ</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-window-item>


          <!-- リーダー設定タブ -->
          <v-window-item v-if="showReaderSettings" value="reader" class="pa-3">
            <v-card variant="outlined" class="mb-3">
              <v-card-subtitle class="d-flex align-center py-2 px-3">
                <v-icon size="small" class="mr-2" color="primary">mdi-book-open-page-variant</v-icon>
                ページ設定
              </v-card-subtitle>
              <v-card-text class="pt-0">
                <v-slider
                  :model-value="readerSettings?.currentPage"
                  label="ページ"
                  :min="1"
                  :max="bookData.page"
                  thumb-label
                  :step="1"
                  color="primary"
                  @update:model-value="handlePageChange"
                />
                <v-row dense class="mt-2">
                  <v-col cols="12" sm="6">
                    <v-switch
                      :model-value="readerSettings?.showTwoPage"
                      label="見開き表示"
                      density="compact"
                      hide-details
                      color="primary"
                      @update:model-value="handleShowTwoPageChange"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-switch
                      :model-value="readerSettings?.showWindowSize"
                      label="画面サイズで表示"
                      density="compact"
                      hide-details
                      color="primary"
                      @update:model-value="handleShowWindowSizeChange"
                    />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>

            <v-card variant="outlined">
              <v-card-subtitle class="d-flex align-center py-2 px-3">
                <v-icon size="small" class="mr-2" color="deep-purple">mdi-image-size-select-large</v-icon>
                画質設定
              </v-card-subtitle>
              <v-card-text class="pt-0">
                <v-row dense>
                  <v-col cols="12" sm="6">
                    <v-select
                      :model-value="readerSettings?.cachePage"
                      :items="[2, 4, 8, 16, 32, 64]"
                      label="先読みページ数"
                      density="compact"
                      variant="outlined"
                      hide-details
                      @update:model-value="handleCachePageChange"
                    />
                  </v-col>
                  <v-col cols="12" sm="6">
                    <v-select
                      :model-value="readerSettings?.customHeight"
                      :items="[600, 1080, 1920]"
                      label="ページ縦サイズ"
                      density="compact"
                      variant="outlined"
                      hide-details
                      @update:model-value="handleCustomHeightChange"
                    />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-window-item>

          <!-- 詳細情報タブ -->
          <v-window-item value="details" class="pa-3">
            <v-list density="compact">
              <v-list-subheader>
                <v-icon size="small" class="mr-2">mdi-calendar</v-icon>
                日付情報
              </v-list-subheader>
              <v-list-item>
                <v-list-item-title>追加日</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(bookData.addDate) }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title>ファイル日付</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(bookData.fileDate) }}</v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-2" />

              <v-list-subheader>
                <v-icon size="small" class="mr-2">mdi-book-clock</v-icon>
                読書状況
              </v-list-subheader>
              <v-list-item>
                <template #prepend>
                  <v-icon color="green">mdi-counter</v-icon>
                </template>
                <v-list-item-title>読んだ回数</v-list-item-title>
                <template #append>
                  <v-chip size="small" color="green">
                    {{ bookData.userData?.readTimes || 0 }} 回
                  </v-chip>
                </template>
              </v-list-item>
              <v-list-item v-if="bookData.userData?.openPage">
                <template #prepend>
                  <v-icon color="blue">mdi-bookmark</v-icon>
                </template>
                <v-list-item-title>最後に開いたページ</v-list-item-title>
                <template #append>
                  <v-chip size="small" color="blue">
                    {{ bookData.userData.openPage }} / {{ bookData.page }}
                  </v-chip>
                </template>
              </v-list-item>
              <v-list-item v-if="bookData.userData?.lastOpenDate">
                <template #prepend>
                  <v-icon color="orange">mdi-clock-outline</v-icon>
                </template>
                <v-list-item-title>最終閲覧日</v-list-item-title>
                <template #append>
                  <span class="text-caption">{{ formatDate(bookData.userData.lastOpenDate) }}</span>
                </template>
              </v-list-item>

              <v-divider class="my-4" />

              <v-list-subheader>
                <v-icon size="small" class="mr-2">mdi-file-code</v-icon>
                技術情報
              </v-list-subheader>
              <v-list-item>
                <v-list-item-title class="text-caption text-medium-emphasis">
                  UUID
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption font-monospace text-break">
                  {{ bookData.uuid }}
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="text-caption text-medium-emphasis">
                  SHA1ハッシュ
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption font-monospace text-break">
                  {{ bookData.sha1 }}
                </v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="text-caption text-medium-emphasis">
                  ファイル名
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption text-break">
                  {{ bookData.importFileName }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-window-item>
        </v-window>
      </v-card-text>

      <v-divider />

      <!-- アクション -->
      <v-card-actions class="pa-4">
        <v-btn
          v-if="showReaderSettings"
          prepend-icon="mdi-page-first"
          variant="tonal"
          color="primary"
          @click="handleGoToFirstPage"
        >
          最初のページへ
        </v-btn>
        <v-spacer />
        <v-btn
          variant="text"
          @click="dialogState = false"
        >
          閉じる
        </v-btn>
        <v-btn
          v-if="!showReaderSettings"
          prepend-icon="mdi-book-open-variant"
          color="primary"
          variant="flat"
          @click="handleOpenBook"
        >
          本を開く
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { apiClient } from '@/func/client'
import { usePushNotice } from '@/composables/utility'
import type { components } from '@/api'

type BookBase = components['schemas']['BookBase']
type GetLibrary = components['schemas']['GetLibrary']

interface ReaderSettings {
  currentPage: number
  showTwoPage: boolean
  showWindowSize: boolean
  cachePage: number
  customHeight: number
}

const { pushNotice } = usePushNotice()

const emit = defineEmits<{
  search: []
  openBook: [book: BookBase]
  rateChanged: [rate: number]
  libraryChanged: [libraryId: number]
  pageChanged: [page: number]
  showTwoPageChanged: [value: boolean]
  showWindowSizeChanged: [value: boolean]
  cachePageChanged: [value: number]
  customHeightChanged: [value: number]
  goToFirstPage: []
  authorClick: [author: { id: number | null; name: string | null }]
}>()

const dialogState = ref(false)
const currentTab = ref('info')
const libraryList = ref<GetLibrary[]>([])
const showReaderSettings = ref(false)
const readerSettings = ref<ReaderSettings | null>(null)
const publisherName = ref<string>('')
const authorNames = ref<string[]>([])
const tagNames = ref<string[]>([])

const bookData = reactive<Partial<BookBase>>({
  uuid: undefined,
  title: undefined,
  authors: [],
  publisher: { name: null, id: null },
  tags: [],
  page: 0,
  size: 0,
  sha1: '',
  importFileName: '',
  addDate: '',
  fileDate: '',
  libraryId: undefined,
  userData: {
    rate: null,
    openPage: null,
    readTimes: null,
    lastOpenDate: null
  }
})

const openDialog = async (book: BookBase, settings?: ReaderSettings) => {
  // 本のデータをコピー
  Object.assign(bookData, book)

  // 出版社名を設定
  publisherName.value = book.publisher?.name || ''

  // 著者名を文字列配列として設定
  console.log('openDialog - book.authors:', book.authors)

  // 著者名を抽出（nameプロパティが文字列の場合のみ取得）
  authorNames.value = (book.authors || [])
    .map(a => {
      if (typeof a === 'string') {
        return a
      }
      if (a && typeof a === 'object' && 'name' in a && typeof a.name === 'string') {
        return a.name
      }
      return ''
    })
    .filter(name => name && name.trim() !== '') // 空文字列や空白のみを除外
  console.log('openDialog - authorNames (filtered):', authorNames.value)

  // タグ名を文字列配列として設定
  tagNames.value = (book.tags || [])
    .map(t => {
      if (typeof t === 'string') {
        return t
      }
      if (t && typeof t === 'object' && 'name' in t && typeof t.name === 'string') {
        return t.name
      }
      return ''
    })
    .filter(name => name && name.trim() !== '')
  console.log('openDialog - tagNames (filtered):', tagNames.value)

  // リーダー設定があれば表示
  showReaderSettings.value = !!settings
  readerSettings.value = settings || null

  // ライブラリ一覧取得
  try {
    const { data, error } = await apiClient.GET('/api/librarys')
    if (error) throw error
    if (data) {
      libraryList.value = data
    }
  } catch (error) {
    console.error('ライブラリ情報取得エラー:', error)
  }

  // ダイアログを開く
  currentTab.value = 'info'
  dialogState.value = true
}

const handleRateChange = async (value: number | string) => {
  const rate = Number(value)
  if (!bookData.userData) {
    bookData.userData = { rate: null, openPage: null, readTimes: null, lastOpenDate: null }
  }
  bookData.userData.rate = rate

  try {
    const { error } = await apiClient.PUT('/api/books/user-data', {
      body: {
        uuids: [bookData.uuid!],
        rate: rate
      }
    })
    if (error) throw error
    pushNotice('評価を更新しました', 'success')
    emit('rateChanged', rate)
    emit('search')
  } catch {
    pushNotice('評価の更新に失敗しました', 'error')
  }
}

const handleTitleChange = async () => {
  try {
    const { error } = await apiClient.PUT('/api/books', {
      body: {
        uuids: [bookData.uuid!],
        title: bookData.title || undefined
      }
    })
    if (error) throw error
    pushNotice('タイトルを更新しました', 'success')
    emit('search')
  } catch {
    pushNotice('タイトルの更新に失敗しました', 'error')
  }
}

const handleAuthorsChange = async () => {
  try {
    const { error } = await apiClient.PUT('/api/books', {
      body: {
        uuids: [bookData.uuid!],
        authors: authorNames.value.filter(Boolean)
      }
    })
    if (error) throw error
    pushNotice('著者を更新しました', 'success')
    emit('search')
  } catch {
    pushNotice('著者の更新に失敗しました', 'error')
  }
}

const handlePublisherChange = async () => {
  try {
    const publisherValue = typeof publisherName.value === 'string'
      ? publisherName.value
      : (publisherName.value as { name: string })?.name || ''

    const { error } = await apiClient.PUT('/api/books', {
      body: {
        uuids: [bookData.uuid!],
        publisher: publisherValue || undefined
      }
    })
    if (error) throw error
    pushNotice('出版社を更新しました', 'success')

    // 更新後のデータを反映
    if (bookData.publisher) {
      bookData.publisher.name = publisherValue
    }
    emit('search')
  } catch {
    pushNotice('出版社の更新に失敗しました', 'error')
  }
}

const handleTagsChange = async () => {
  try {
    const { error } = await apiClient.PUT('/api/books', {
      body: {
        uuids: [bookData.uuid!],
        tags: tagNames.value.filter(Boolean)
      }
    })
    if (error) throw error
    pushNotice('タグを更新しました', 'success')
    emit('search')
  } catch {
    pushNotice('タグの更新に失敗しました', 'error')
  }
}

const handleLibraryChange = async () => {
  try {
    const { error } = await apiClient.PUT('/api/books', {
      body: {
        uuids: [bookData.uuid!],
        libraryId: bookData.libraryId
      }
    })
    if (error) throw error
    pushNotice('ライブラリを変更しました', 'success')
    emit('libraryChanged', bookData.libraryId!)
    emit('search')
  } catch {
    pushNotice('ライブラリの変更に失敗しました', 'error')
  }
}

const handlePageChange = (value: number | string) => {
  const page = Number(value)
  if (readerSettings.value) {
    readerSettings.value.currentPage = page
  }
  emit('pageChanged', page)
}

const handleShowTwoPageChange = (value: boolean | null) => {
  const boolValue = !!value
  if (readerSettings.value) {
    readerSettings.value.showTwoPage = boolValue
  }
  emit('showTwoPageChanged', boolValue)
}

const handleShowWindowSizeChange = (value: boolean | null) => {
  const boolValue = !!value
  if (readerSettings.value) {
    readerSettings.value.showWindowSize = boolValue
  }
  emit('showWindowSizeChanged', boolValue)
}

const handleCachePageChange = (value: number | string) => {
  const cachePage = Number(value)
  if (readerSettings.value) {
    readerSettings.value.cachePage = cachePage
  }
  emit('cachePageChanged', cachePage)
}

const handleCustomHeightChange = (value: number | string) => {
  const height = Number(value)
  if (readerSettings.value) {
    readerSettings.value.customHeight = height
  }
  emit('customHeightChanged', height)
}

const handleGoToFirstPage = () => {
  emit('goToFirstPage')
}

const handleOpenBook = () => {
  emit('openBook', bookData as BookBase)
  dialogState.value = false
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatDate = (dateString?: string): string => {
  if (!dateString) return '(不明)'
  try {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  } catch {
    return '(不明)'
  }
}

defineExpose({
  openDialog
})
</script>

<style scoped>
.text-break {
  word-break: break-all;
}

.font-monospace {
  font-family: 'Courier New', Courier, monospace;
}
</style>
