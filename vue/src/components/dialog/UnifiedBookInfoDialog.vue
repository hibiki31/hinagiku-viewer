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
          <v-icon color="white">
            mdi-close
          </v-icon>
        </v-btn>
      </v-card-title>

      <!-- タブナビゲーション -->
      <v-tabs v-model="currentTab" color="primary" align-tabs="center">
        <v-tab value="info">
          <v-icon start>
            mdi-information
          </v-icon>
          基本情報
        </v-tab>
        <v-tab v-if="showReaderSettings" value="reader">
          <v-icon start>
            mdi-book-open-page-variant
          </v-icon>
          リーダー設定
        </v-tab>
        <v-tab value="details">
          <v-icon start>
            mdi-file-document-outline
          </v-icon>
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
                    <v-icon color="white" size="small">
                      mdi-book
                    </v-icon>
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
                <v-list-item-subtitle class="text-caption">
                  タイトル
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- 著者 -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="blue-grey" size="32">
                    <v-icon color="white" size="small">
                      mdi-account
                    </v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title>
                  <div class="d-flex flex-wrap align-center ga-1 mb-2">
                    <v-menu
                      v-for="(author, index) in bookData.authors"
                      :key="author.id || index"
                      location="bottom"
                    >
                      <template #activator="{ props: menuProps }">
                        <v-tooltip location="bottom">
                          <template #activator="{ props: tooltipProps }">
                            <v-chip
                              v-bind="{ ...menuProps, ...tooltipProps }"
                              :color="author.isFavorite ? 'orange' : undefined"
                              size="small"
                              closable
                              @click:close="handleDeleteAuthor(author)"
                            >
                              {{ author.name }}
                            </v-chip>
                          </template>
                          <span>クリックでメニューを開く</span>
                        </v-tooltip>
                      </template>
                      <v-card min-width="200">
                        <v-list density="compact">
                          <v-list-item @click="handleSearchAuthor(author)">
                            <template #prepend>
                              <v-icon color="primary">
                                mdi-magnify
                              </v-icon>
                            </template>
                            <v-list-item-title>この著者で検索する</v-list-item-title>
                          </v-list-item>
                          <v-list-item
                            v-if="!author.isFavorite"
                            @click="handleFavoriteAuthor(author, true)"
                          >
                            <template #prepend>
                              <v-icon color="orange">
                                mdi-star
                              </v-icon>
                            </template>
                            <v-list-item-title>お気に入りに追加</v-list-item-title>
                          </v-list-item>
                          <v-list-item
                            v-if="author.isFavorite"
                            @click="handleFavoriteAuthor(author, false)"
                          >
                            <template #prepend>
                              <v-icon>mdi-star-outline</v-icon>
                            </template>
                            <v-list-item-title>お気に入りから外す</v-list-item-title>
                          </v-list-item>
                        </v-list>
                      </v-card>
                    </v-menu>
                    <v-tooltip location="bottom">
                      <template #activator="{ props }">
                        <v-btn
                          v-bind="props"
                          icon="mdi-plus-circle"
                          size="x-small"
                          variant="text"
                          @click="handleAddAuthorDialog"
                        />
                      </template>
                      <span>著者を追加</span>
                    </v-tooltip>
                  </div>
                  <div v-if="(!bookData.authors || bookData.authors.length === 0)" class="text-caption text-medium-emphasis">
                    著者が登録されていません
                  </div>
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">
                  著者
                </v-list-item-subtitle>
              </v-list-item>

              <!-- 著者追加ダイアログ -->
              <v-dialog v-model="addAuthorDialogState" max-width="400">
                <v-card>
                  <v-card-title>著者を追加</v-card-title>
                  <v-card-text>
                    <v-text-field
                      v-model="newAuthorName"
                      label="著者名"
                      counter="64"
                      variant="outlined"
                      density="comfortable"
                      autofocus
                      @keyup.enter="handleAddAuthorSubmit"
                    />
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer />
                    <v-btn variant="text" @click="addAuthorDialogState = false">
                      キャンセル
                    </v-btn>
                    <v-btn
                      color="primary"
                      variant="flat"
                      :disabled="!newAuthorName || newAuthorName.length > 64"
                      @click="handleAddAuthorSubmit"
                    >
                      追加
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>

              <v-divider class="my-1" />

              <!-- 出版社 -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="teal" size="32">
                    <v-icon color="white" size="small">
                      mdi-domain
                    </v-icon>
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
                <v-list-item-subtitle class="text-caption">
                  出版社
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- ページ数・サイズ -->
              <v-list-item class="px-2 py-1">
                <v-row dense class="align-center">
                  <v-col cols="6" class="d-flex align-center">
                    <v-avatar color="orange" size="32" class="mr-2">
                      <v-icon color="white" size="small">
                        mdi-file-document
                      </v-icon>
                    </v-avatar>
                    <div>
                      <div class="text-subtitle-2">
                        {{ bookData.page }}
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        ページ数
                      </div>
                    </div>
                  </v-col>
                  <v-col cols="6" class="d-flex align-center">
                    <v-avatar color="deep-purple" size="32" class="mr-2">
                      <v-icon color="white" size="small">
                        mdi-harddisk
                      </v-icon>
                    </v-avatar>
                    <div>
                      <div class="text-subtitle-2">
                        {{ formatFileSize(bookData.size || 0) }}
                      </div>
                      <div class="text-caption text-medium-emphasis">
                        ファイルサイズ
                      </div>
                    </div>
                  </v-col>
                </v-row>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- タグ -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="pink" size="32">
                    <v-icon color="white" size="small">
                      mdi-tag-multiple
                    </v-icon>
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
                <v-list-item-subtitle class="text-caption">
                  タグ
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- 評価 -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="amber" size="32">
                    <v-icon color="white" size="small">
                      mdi-star
                    </v-icon>
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
                <v-list-item-subtitle class="text-caption">
                  評価
                </v-list-item-subtitle>
              </v-list-item>

              <v-divider class="my-1" />

              <!-- ライブラリ -->
              <v-list-item class="px-2 py-1">
                <template #prepend>
                  <v-avatar color="primary" size="32">
                    <v-icon color="white" size="small">
                      mdi-bookshelf
                    </v-icon>
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
                <v-list-item-subtitle class="text-caption">
                  ライブラリ
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-window-item>


          <!-- リーダー設定タブ -->
          <v-window-item v-if="showReaderSettings" value="reader" class="pa-3">
            <v-card variant="outlined" class="mb-3">
              <v-card-subtitle class="d-flex align-center py-2 px-3">
                <v-icon size="small" class="mr-2" color="primary">
                  mdi-book-open-page-variant
                </v-icon>
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
                <v-icon size="small" class="mr-2" color="deep-purple">
                  mdi-image-size-select-large
                </v-icon>
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
                <v-icon size="small" class="mr-2">
                  mdi-calendar
                </v-icon>
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
                <v-icon size="small" class="mr-2">
                  mdi-book-clock
                </v-icon>
                読書状況
              </v-list-subheader>
              <v-list-item>
                <template #prepend>
                  <v-icon color="green">
                    mdi-counter
                  </v-icon>
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
                  <v-icon color="blue">
                    mdi-bookmark
                  </v-icon>
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
                  <v-icon color="orange">
                    mdi-clock-outline
                  </v-icon>
                </template>
                <v-list-item-title>最終閲覧日</v-list-item-title>
                <template #append>
                  <span class="text-caption">{{ formatDate(bookData.userData.lastOpenDate) }}</span>
                </template>
              </v-list-item>

              <v-divider class="my-4" />

              <v-list-subheader>
                <v-icon size="small" class="mr-2">
                  mdi-download
                </v-icon>
                ダウンロード
              </v-list-subheader>
              <v-list-item>
                <v-list-item-title>
                  <v-btn
                    block
                    color="primary"
                    variant="tonal"
                    prepend-icon="mdi-download"
                    :loading="downloadLoading"
                    @click="handleDownload"
                  >
                    本をダウンロード (ZIP)
                  </v-btn>
                </v-list-item-title>
              </v-list-item>

              <v-divider class="my-4" />

              <v-list-subheader>
                <v-icon size="small" class="mr-2">
                  mdi-file-code
                </v-icon>
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
        <v-btn
          v-if="showReaderSettings"
          prepend-icon="mdi-home"
          variant="tonal"
          color="secondary"
          @click="handleGoToLibrary"
        >
          ライブラリに戻る
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
  goToLibrary: []
  authorClick: [author: { id: number | null; name: string | null }]
}>()

const dialogState = ref(false)
const currentTab = ref('info')
const libraryList = ref<GetLibrary[]>([])
const showReaderSettings = ref(false)
const readerSettings = ref<ReaderSettings | null>(null)
const publisherName = ref<string>('')
const tagNames = ref<string[]>([])
const addAuthorDialogState = ref(false)
const newAuthorName = ref('')
const downloadLoading = ref(false)

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

  // リーダー設定があれば表示
  showReaderSettings.value = !!settings
  readerSettings.value = settings || null

  // ライブラリ一覧取得
  try {
    const { data, error } = await apiClient.GET('/api/libraries', {})
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

// 著者で検索
const handleSearchAuthor = (author: BookBase['authors'][0]) => {
  if (!author.name) return

  // 著者クリックイベントを発火
  emit('authorClick', { id: author.id, name: author.name })

  // ダイアログを閉じる
  dialogState.value = false
}

// 著者をお気に入りに追加/削除
const handleFavoriteAuthor = async (author: BookBase['authors'][0], isFavorite: boolean) => {
  if (!author.id) return

  try {
    const { error } = await apiClient.PATCH('/api/authors', {
      body: {
        authorId: author.id,
        isFavorite: isFavorite
      }
    })
    if (error) throw error

    // ローカルデータを更新
    author.isFavorite = isFavorite

    pushNotice(
      isFavorite ? '著者をお気に入りに追加しました' : '著者をお気に入りから外しました',
      'success'
    )
    emit('search')
  } catch {
    pushNotice('著者のお気に入り変更に失敗しました', 'error')
  }
}

// 著者を削除
const handleDeleteAuthor = async (author: BookBase['authors'][0]) => {
  if (!author.id) return

  try {
    const { error } = await apiClient.DELETE('/api/books/{book_uuid}/authors', {
      params: {
        path: { book_uuid: bookData.uuid! }
      },
      body: {
        authorId: author.id
      }
    })
    if (error) throw error

    // ローカルデータから削除
    if (bookData.authors) {
      const index = bookData.authors.findIndex((a) => a.id === author.id)
      if (index !== -1) {
        bookData.authors.splice(index, 1)
      }
    }

    pushNotice('著者を削除しました', 'success')
    emit('search')
  } catch {
    pushNotice('著者の削除に失敗しました', 'error')
  }
}

// 著者追加ダイアログを開く
const handleAddAuthorDialog = () => {
  newAuthorName.value = ''
  addAuthorDialogState.value = true
}

// 著者を追加
const handleAddAuthorSubmit = async () => {
  if (!newAuthorName.value || newAuthorName.value.length > 64) return

  try {
    const { data, error } = await apiClient.POST('/api/books/{book_uuid}/authors', {
      params: {
        path: { book_uuid: bookData.uuid! }
      },
      body: {
        authorName: newAuthorName.value
      }
    })
    if (error) throw error

    // レスポンスから更新された本のデータを取得
    if (data) {
      Object.assign(bookData, data)
    }

    pushNotice('著者を追加しました', 'success')
    addAuthorDialogState.value = false
    newAuthorName.value = ''
    emit('search')
  } catch {
    pushNotice('著者の追加に失敗しました', 'error')
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
    // 元のタグリストを取得（BookTag[]形式）
    const originalTags = bookData.tags || []

    // 新しいタグ名リスト
    const newTagNames = tagNames.value.filter(Boolean)

    // 削除されたタグ（元のタグから新しいタグ名リストに含まれないもの）
    const removedTags = originalTags.filter(tag => !newTagNames.includes(tag.name))

    // 追加されたタグ（新しいタグ名リストから元のタグ名に含まれないもの）
    const originalTagNames = originalTags.map(t => t.name)
    const addedTagNames = newTagNames.filter(tagName => !originalTagNames.includes(tagName))

    // 削除処理 - 新API: DELETE /api/books/{uuid}/tags/{tag_id}
    for (const tag of removedTags) {
      const { error } = await apiClient.DELETE('/api/books/{uuid}/tags/{tag_id}', {
        params: {
          path: {
            uuid: bookData.uuid!,
            tag_id: tag.id
          }
        }
      })
      if (error) throw error
    }

    // 追加処理 - 新API: POST /api/books/{uuid}/tags
    for (const tagName of addedTagNames) {
      const { error } = await apiClient.POST('/api/books/{uuid}/tags', {
        params: {
          path: { uuid: bookData.uuid! }
        },
        body: {
          name: tagName
        }
      })
      if (error) throw error
    }

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

const handleGoToLibrary = () => {
  emit('goToLibrary')
  dialogState.value = false
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

const handleDownload = async () => {
  if (!bookData.uuid) {
    pushNotice('本のUUIDが取得できません', 'error')
    return
  }

  downloadLoading.value = true

  try {
    // ファイル名を生成（タイトルまたはファイル名を使用）
    const filename = bookData.title || bookData.importFileName || `book_${bookData.uuid}.zip`
    const safeFilename = filename.replace(/[<>:"/\\|?*]/g, '_') + '.zip'

    // ダウンロードURLを生成
    const downloadUrl = `${import.meta.env.VITE_APP_API_HOST || ''}/api/books/${bookData.uuid}/download`

    // fetchでBlobを取得
    const response = await fetch(downloadUrl, {
      headers: {
        'Authorization': `Bearer ${(await import('js-cookie')).default.get('accessToken') || ''}`
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const blob = await response.blob()

    // ダウンロードリンクを生成
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = safeFilename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    pushNotice('ダウンロードを開始しました', 'success')
  } catch (error) {
    console.error('ダウンロードエラー:', error)
    pushNotice('ダウンロードに失敗しました', 'error')
  } finally {
    downloadLoading.value = false
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
