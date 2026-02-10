<template>
  <v-dialog v-model="dialogState" max-width="800" scrollable>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2" color="primary">mdi-magnify</v-icon>
        詳細検索
      </v-card-title>
      <v-divider />
      <v-card-text class="pa-0">
        <v-tabs v-model="activeTab" bg-color="grey-lighten-4">
          <v-tab value="basic">
            <v-icon start>mdi-text-search</v-icon>
            基本検索
          </v-tab>
          <v-tab value="author">
            <v-icon start>mdi-account</v-icon>
            著者
          </v-tab>
          <v-tab value="filters">
            <v-icon start>mdi-filter</v-icon>
            フィルター
          </v-tab>
          <v-tab value="advanced">
            <v-icon start>mdi-tune</v-icon>
            詳細
          </v-tab>
        </v-tabs>

        <v-window v-model="activeTab" class="pa-4">
          <!-- 基本検索タブ -->
          <v-window-item value="basic">
            <v-text-field
              v-model="searchQuery.titleLike"
              spellcheck="false"
              label="タイトル検索"
              placeholder="タイトルに含まれる文字列"
              prepend-inner-icon="mdi-book"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
            />
            <v-text-field
              v-model="searchQuery.fullText"
              spellcheck="false"
              label="あいまい検索"
              placeholder="タイトル・著者・ファイル名などから検索"
              prepend-inner-icon="mdi-text-search"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
            />
            <v-text-field
              v-model="searchQuery.fileNameLike"
              spellcheck="false"
              label="ファイル名検索"
              placeholder="元のファイル名で検索"
              prepend-inner-icon="mdi-file"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
            />

            <v-divider class="my-4" />

            <div class="text-subtitle-2 mb-2">評価フィルター</div>
            <div class="d-flex align-center mb-2">
              <v-rating
                :model-value="searchQuery.rate ?? undefined"
                size="large"
                color="amber"
                active-color="amber"
                hover
                @update:model-value="(value) => searchQuery.rate = value as number"
              />
              <v-spacer />
              <v-btn
                size="small"
                variant="outlined"
                @click="searchQuery.rate = null"
              >
                クリア
              </v-btn>
            </div>
            <v-btn-group divided density="compact" variant="outlined" class="w-100">
              <v-btn
                :variant="searchQuery.rate === null ? 'flat' : 'outlined'"
                :color="searchQuery.rate === null ? 'primary' : undefined"
                @click="searchQuery.rate = null"
              >
                <v-icon start size="small">mdi-format-list-bulleted</v-icon>
                全て表示
              </v-btn>
              <v-btn
                :variant="searchQuery.rate === 0 ? 'flat' : 'outlined'"
                :color="searchQuery.rate === 0 ? 'primary' : undefined"
                @click="searchQuery.rate = 0"
              >
                <v-icon start size="small">mdi-star-off-outline</v-icon>
                未評価のみ
              </v-btn>
            </v-btn-group>
          </v-window-item>

          <!-- 著者タブ -->
          <v-window-item value="author">
            <v-autocomplete
              v-model="searchQuery.authorLike"
              :items="authorSuggestions"
              :loading="authorLoading"
              :search="authorSearchInput"
              spellcheck="false"
              label="著者名検索"
              placeholder="著者名を入力してください"
              prepend-inner-icon="mdi-account-search"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
              item-title="name"
              item-value="name"
              no-filter
              @update:search="onAuthorSearchInput"
            >
              <template #item="{ props, item }">
                <v-list-item v-bind="props">
                  <template #prepend>
                    <v-icon v-if="item.raw.isFavorite" color="pink">mdi-heart</v-icon>
                    <v-icon v-else>mdi-account</v-icon>
                  </template>
                </v-list-item>
              </template>
              <template #no-data>
                <v-list-item>
                  <v-list-item-title class="text-grey">
                    {{ authorSearchInput ? '該当する著者が見つかりません' : '著者名を入力してください' }}
                  </v-list-item-title>
                </v-list-item>
              </template>
            </v-autocomplete>

            <v-divider class="my-4" />

            <v-switch
              v-model="searchQuery.authorIsFavorite"
              label="お気に入り著者のみ表示"
              color="pink"
              hide-details
              class="mb-4"
            >
              <template #prepend>
                <v-icon color="pink">mdi-heart</v-icon>
              </template>
            </v-switch>

            <v-alert type="info" variant="tonal" density="compact" class="mt-4">
              <template #prepend>
                <v-icon>mdi-information</v-icon>
              </template>
              著者のお気に入り設定は書籍詳細画面から行えます
            </v-alert>
          </v-window-item>

          <!-- フィルタータブ -->
          <v-window-item value="filters">
            <v-autocomplete
              v-model="searchQuery.tag"
              :items="availableTags"
              :loading="tagsLoading"
              spellcheck="false"
              label="タグで絞り込み"
              placeholder="タグを入力してください"
              prepend-inner-icon="mdi-tag"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
            >
              <template #item="{ props }">
                <v-list-item v-bind="props">
                  <template #prepend>
                    <v-icon>mdi-tag</v-icon>
                  </template>
                </v-list-item>
              </template>
              <template #no-data>
                <v-list-item>
                  <v-list-item-title class="text-grey">
                    該当するタグが見つかりません
                  </v-list-item-title>
                </v-list-item>
              </template>
            </v-autocomplete>

            <v-text-field
              v-model="searchQuery.seriesId"
              spellcheck="false"
              label="シリーズID"
              placeholder="シリーズで絞り込み"
              prepend-inner-icon="mdi-book-multiple"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
            />

            <v-text-field
              v-model="searchQuery.genreId"
              spellcheck="false"
              label="ジャンルID"
              placeholder="ジャンルで絞り込み"
              prepend-inner-icon="mdi-shape"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
            />

            <v-divider class="my-4" />

            <v-switch
              v-model="searchQuery.cached"
              label="キャッシュ済みのみ表示"
              color="primary"
              hide-details
              class="mb-2"
            >
              <template #prepend>
                <v-icon>mdi-cached</v-icon>
              </template>
            </v-switch>

            <v-alert type="info" variant="tonal" density="compact" class="mt-4">
              <template #prepend>
                <v-icon>mdi-information</v-icon>
              </template>
              キャッシュ済みの本は高速に表示できます
            </v-alert>
          </v-window-item>

          <!-- 詳細タブ -->
          <v-window-item value="advanced">
            <v-text-field
              v-model="searchQuery.uuid"
              spellcheck="false"
              label="UUID検索"
              placeholder="書籍の一意識別子"
              prepend-inner-icon="mdi-identifier"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
            />

            <v-text-field
              v-model="searchQuery.state"
              spellcheck="false"
              label="状態フィルター"
              placeholder="書籍の状態で絞り込み"
              prepend-inner-icon="mdi-state-machine"
              variant="outlined"
              clearable
              hide-details="auto"
              class="mb-4"
            />

            <v-divider class="my-4" />

            <div class="text-subtitle-2 mb-3">検索結果の件数</div>
            <v-slider
              v-model="searchQuery.limit"
              :min="10"
              :max="200"
              :step="10"
              thumb-label
              color="primary"
              hide-details
              class="mb-2"
            >
              <template #prepend>
                <v-icon>mdi-format-list-numbered</v-icon>
              </template>
              <template #append>
                <v-chip size="small" color="primary">
                  {{ searchQuery.limit }}件
                </v-chip>
              </template>
            </v-slider>

            <v-alert type="info" variant="tonal" density="compact" class="mt-4">
              <template #prepend>
                <v-icon>mdi-information</v-icon>
              </template>
              表示件数を増やすと読み込み時間が長くなる場合があります
            </v-alert>
          </v-window-item>
        </v-window>
      </v-card-text>

      <v-divider />

      <v-card-actions class="px-4 py-3">
        <v-btn
          color="warning"
          variant="text"
          prepend-icon="mdi-refresh"
          @click="resetSearch"
        >
          リセット
        </v-btn>
        <v-spacer />
        <v-btn
          color="grey"
          variant="text"
          @click="dialogState = false"
        >
          キャンセル
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          prepend-icon="mdi-magnify"
          @click="submitDialog"
        >
          検索
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useReaderStateStore } from '@/stores/readerState'
import { apiClient } from '@/func/client'
import type { components } from '@/api'

type AuthorGet = components['schemas']['AuthorGet']

const readerStateStore = useReaderStateStore()

const emit = defineEmits<{
  search: []
}>()

const dialogState = ref(false)
const activeTab = ref('basic')
const availableTags = ref<string[]>([])
const tagsLoading = ref(false)
const authorSuggestions = ref<AuthorGet[]>([])
const authorLoading = ref(false)
const authorSearchInput = ref<string | undefined>(undefined)
let authorSearchTimeout: ReturnType<typeof setTimeout> | null = null

interface ExtendedSearchQuery {
  // 既存のパラメータ
  titleLike: string | null
  fullText: string | null
  rate: number | null
  authorLike: string | null
  // 新規追加パラメータ
  fileNameLike: string | null
  cached: boolean | null
  authorIsFavorite: boolean | null
  seriesId: string | null
  genreId: string | null
  tag: string | null
  state: string | null
  uuid: string | null
  limit: number
}

const searchQuery = reactive<ExtendedSearchQuery>({
  titleLike: null,
  fullText: null,
  rate: null,
  authorLike: null,
  fileNameLike: null,
  cached: null,
  authorIsFavorite: null,
  seriesId: null,
  genreId: null,
  tag: null,
  state: null,
  uuid: null,
  limit: 60
})

const openDialog = () => {
  // 現在の検索クエリから値を復元
  const current = readerStateStore.searchQuery
  searchQuery.titleLike = current.titleLike
  searchQuery.fullText = current.fullText || null
  searchQuery.rate = current.rate
  searchQuery.authorLike = current.authorLike
  searchQuery.fileNameLike = current.fileNameLike || null
  searchQuery.cached = current.cached || null
  searchQuery.authorIsFavorite = current.authorIsFavorite || null
  searchQuery.seriesId = current.seriesId || null
  searchQuery.genreId = current.genre
  searchQuery.tag = current.tag || null
  searchQuery.state = current.state || null
  searchQuery.uuid = current.uuid || null
  searchQuery.limit = current.limit

  dialogState.value = true
}

const resetSearch = () => {
  searchQuery.titleLike = null
  searchQuery.fullText = null
  searchQuery.rate = null
  searchQuery.authorLike = null
  searchQuery.fileNameLike = null
  searchQuery.cached = null
  searchQuery.authorIsFavorite = null
  searchQuery.seriesId = null
  searchQuery.genreId = null
  searchQuery.tag = null
  searchQuery.state = null
  searchQuery.uuid = null
  searchQuery.limit = 60
  activeTab.value = 'basic'
}

const submitDialog = async () => {
  // readerStateStoreのsearchQueryを更新
  await readerStateStore.setSearchQuery({
    ...readerStateStore.searchQuery,
    titleLike: searchQuery.titleLike,
    fullText: searchQuery.fullText || '',
    rate: searchQuery.rate,
    authorLike: searchQuery.authorLike,
    fileNameLike: searchQuery.fileNameLike,
    cached: searchQuery.cached,
    authorIsFavorite: searchQuery.authorIsFavorite,
    seriesId: searchQuery.seriesId,
    genre: searchQuery.genreId,
    tag: searchQuery.tag,
    state: searchQuery.state,
    uuid: searchQuery.uuid,
    limit: searchQuery.limit
  })
  emit('search')
  dialogState.value = false
}

const loadTags = async () => {
  try {
    tagsLoading.value = true
    const { data, error } = await apiClient.GET('/api/tags', {})
    if (error) throw error
    if (data && Array.isArray(data)) {
      availableTags.value = data.map((tag) => (tag as { name: string }).name)
    }
  } catch (error) {
    console.error('タグ取得エラー:', error)
  } finally {
    tagsLoading.value = false
  }
}

const onAuthorSearchInput = (value: string | undefined) => {
  authorSearchInput.value = value

  // デバウンス処理
  if (authorSearchTimeout) {
    clearTimeout(authorSearchTimeout)
  }

  // 入力が空の場合はクリア
  if (!value || value.trim().length === 0) {
    authorSuggestions.value = []
    return
  }

  // 300ms後にAPI呼び出し
  authorSearchTimeout = setTimeout(async () => {
    await loadAuthorSuggestions(value)
  }, 300)
}

const loadAuthorSuggestions = async (searchTerm: string) => {
  if (!searchTerm || searchTerm.trim().length === 0) {
    authorSuggestions.value = []
    return
  }

  try {
    authorLoading.value = true
    const { data, error } = await apiClient.GET('/api/authors', {
      params: {
        query: {
          isFavorite: false,
          nameLike: searchTerm
        }
      }
    })

    if (error) throw error
    if (data) {
      authorSuggestions.value = data as AuthorGet[]
    }
  } catch (error) {
    console.error('著者検索エラー:', error)
    authorSuggestions.value = []
  } finally {
    authorLoading.value = false
  }
}

onMounted(() => {
  loadTags()
})

defineExpose({
  openDialog
})
</script>

<style scoped>
.v-window {
  min-height: 400px;
  max-height: 500px;
  overflow-y: auto;
}
</style>
