<template>
  <div class="booksList">
    <!-- 前回の続きを開くか確認するダイアログ -->
    <v-dialog v-model="resumeDialog" max-width="450" persistent>
      <v-card>
        <v-card-title class="text-h6">
          読書を再開しますか？
        </v-card-title>
        <v-card-text>
          前回読んでいた本があります。続きから開きますか？
          <div class="text-body-2 text-grey mt-2">
            ページ: {{ resumeBookPage }}
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dismissResume">
            開かない
          </v-btn>
          <v-btn color="primary" variant="flat" @click="acceptResume">
            続きから開く
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <SearchDialog ref="searchDialogRef" @search="search" />
    <BookDetailDialog ref="bookDetailDialogRef" @search="search" />
    <RangeChangeDialog ref="rangeChangeDialogRef" @search="search" />
    <!-- トップバー -->
    <v-app-bar color="primary" dark density="compact" flat app>
      <v-app-bar-nav-icon @click="showDrawer = !showDrawer" />
      <v-toolbar-title />
      <v-spacer />
      <v-text-field
        v-model="queryTitle"
        hide-details
        single-line
        density="compact"
      />
      <v-btn icon @click="searchDialogRef?.openDialog()">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>
      <v-btn icon @click="reload()">
        <v-icon>mdi-reload</v-icon>
      </v-btn>
    </v-app-bar>
    <!-- ドロワー -->
    <v-navigation-drawer v-model="showDrawer" app>
      <v-list nav density="compact">
        <v-list-item>
          <v-select
            v-model="queryLibrary"
            :items="libraryList"
            label="Library"
            item-title="name"
            item-value="id"
            density="compact"
          />
        </v-list-item>
      </v-list>

      <!-- 評価するところ -->
      <v-divider />
      <v-list nav density="compact">
        <v-list-item>
          <v-rating
            :model-value="queryRate ?? undefined"
            size="small"
            @update:model-value="(value) => queryRate = value as number"
          />
        </v-list-item>
        <v-list-item>
          <v-btn size="small" color="primary" class="ma-1" width="70" @click="queryRate = null">
            All Rate
          </v-btn>
          <v-btn size="small" color="grey" class="ma-1" width="70" @click="queryRate = 0">
            No Rate
          </v-btn>
        </v-list-item>
      </v-list>
      <v-divider />
      <v-list nav density="compact">
        <v-list-item>
          <v-btn class="ma-1" size="small" color="error" disabled @click="exportDialog = true">
            Range Export<v-icon class="pl-1">
              mdi-export
            </v-icon>
          </v-btn>
        </v-list-item>
        <v-list-item>
          <v-btn class="ma-1" size="small" color="primary" @click="rangeChangeDialogRef?.openDialog()">
            Range Change<v-icon>mdi-pen</v-icon>
          </v-btn>
        </v-list-item>
        <v-list-item>
          <v-btn class="ma-1" size="small" @click="loadLibrary">
            Load Library<v-icon class="pl-2">
              mdi-book-refresh
            </v-icon>
          </v-btn>
        </v-list-item>
        <v-list-item>
          <v-btn class="ma-1" size="small" @click="toDuplicateView">
            Duplicate List<v-icon class="pl-2">
              mdi-content-duplicate
            </v-icon>
          </v-btn>
        </v-list-item>
      </v-list>
      <v-divider />
      <v-list-item>
        <v-switch
          :model-value="showListMode"
          label="リスト表示"
          density="compact"
          hide-details
          @update:model-value="(value) => readerStateStore.setShowListMode(!!value)"
        />
      </v-list-item>
      <!-- ライセンス -->
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
    <v-progress-linear v-show="isLoading" indeterminate color="yellow-darken-2" />
    <!-- メインの一覧 -->
    <v-container v-show="!isLoading">
      <BooksListTable
        v-if="showListMode"
        @to-reader-page="toReaderPage"
        @open-menu="openMenu"
        @search="search"
      />
      <BooksListThum v-else @to-reader-page="toReaderPage" @open-menu="openMenu" />
    </v-container>
    <v-pagination v-model="page" :length="maxPage" :total-visible="17" class="ma-3" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useReaderStateStore } from '@/stores/readerState'
import axios from '@/func/axios'
import { usePushNotice } from '@/composables/utility'
import SearchDialog from '@/components/dialog/SearchDialog.vue'
import BookDetailDialog from '@/components/dialog/BookDetailDialog.vue'
import RangeChangeDialog from '@/components/dialog/RangeChangeDialog.vue'
import BooksListTable from '@/components/BooksListTable.vue'
import BooksListThum from '@/components/BooksListThum.vue'
import type { components } from '@/api'

type GetLibrary = components['schemas']['GetLibrary']
type BookBase = components['schemas']['BookBase']

const router = useRouter()
const readerStateStore = useReaderStateStore()
const { pushNotice } = usePushNotice()

const searchDialogRef = ref()
const bookDetailDialogRef = ref()
const rangeChangeDialogRef = ref()

const showDrawer = ref(true)
const isLoading = ref(true)
const exportDialog = ref(false)
const libraryList = ref<GetLibrary[]>([])
const version = '3.0.0'

// 前回の続きを開くか確認するダイアログ
const resumeDialog = ref(false)
const resumeBookUUID = ref('')
const resumeBookPage = ref(0)

const searchQuery = computed(() => readerStateStore.searchQuery)
const booksCount = computed(() => readerStateStore.booksCount)
const showListMode = computed(() => readerStateStore.showListMode)
const maxPage = computed(() => Math.ceil(booksCount.value / searchQuery.value.limit))

const page = computed({
  get() {
    return Number(searchQuery.value.offset / searchQuery.value.limit) + 1
  },
  set(value: number) {
    const query = { ...searchQuery.value }
    query.offset = query.limit * (value - 1)
    readerStateStore.setSearchQuery(query)
    search(false)
  }
})

const queryTitle = computed({
  get() {
    return searchQuery.value.fullText
  },
  set(value: string) {
    const query = { ...searchQuery.value }
    query.fullText = value
    readerStateStore.setSearchQuery(query)
    search(true)
  }
})

const queryLibrary = computed({
  get() {
    return searchQuery.value.libraryId
  },
  set(value: number | null) {
    const query = { ...searchQuery.value }
    query.libraryId = value
    readerStateStore.setSearchQuery(query)
    search(true)
  }
})

const queryRate = computed({
  get() {
    return searchQuery.value.rate
  },
  set(value: number | null) {
    const query = { ...searchQuery.value }
    query.rate = value
    readerStateStore.setSearchQuery(query)
    search(true)
  }
})

const search = async (resetOffset = false) => {
  isLoading.value = true
  await readerStateStore.serachBooks(resetOffset)
  pushNotice(booksCount.value + '件', 'info')
  isLoading.value = false
  scrollToUUID()
}

const reload = () => {
  const query = { ...searchQuery.value }
  query.fullText = ''
  readerStateStore.setSearchQuery(query)
  search(true)
}

const scrollToUUID = () => {
  setTimeout(() => {
    const backBookUUID = localStorage.backBookUUID
    if (backBookUUID) {
      const element = document.getElementById(backBookUUID)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
    localStorage.removeItem('backBookUUID')
  }, 300)
}

const loadLibrary = async () => {
  try {
    const response = await axios.request({
      method: 'patch',
      url: '/media/library',
      data: { state: 'load' }
    })
    pushNotice('ライブラリのリロードを開始' + response.data.status, 'success')
  } catch {
    pushNotice('ライブラリのリロードに失敗しました', 'error')
  }
}

const openMenu = (item: BookBase) => {
  bookDetailDialogRef.value?.openDialog(item)
}

const toReaderPage = async (item: BookBase) => {
  // ローカルストレージにパラメータ格納
  createCache(item)
  localStorage.setItem('searchQuery', JSON.stringify(searchQuery.value))
  localStorage.setItem('backBookUUID', item.uuid)

  // 移動
  router.push(`/books/${item.uuid}`)
}

const createCache = (book: BookBase) => {
  pushNotice('キャッシュの作成をリクエスト', 'info')
  axios.request({
    method: 'patch',
    url: '/media/books',
    data: {
      uuid: book.uuid,
      height: window.innerHeight * window.devicePixelRatio
    }
  })
}

const toDuplicateView = () => {
  router.push('/duplicate')
}

// 前回の続きを開くダイアログのハンドラー
const acceptResume = () => {
  resumeDialog.value = false
  router.push(`/books/${resumeBookUUID.value}?startPage=${resumeBookPage.value}`)
}

const dismissResume = () => {
  resumeDialog.value = false
  localStorage.removeItem('openBookUUID')
  localStorage.removeItem('openBookPage')
}

const initLibraryAndSearch = async () => {
  // ライブラリ情報取得
  try {
    const response = await axios.get('/api/librarys')
    libraryList.value = response.data
  } catch (error) {
    console.error('ライブラリ情報取得エラー:', error)
  }

  // 初期ロード
  search()
}

onMounted(async () => {
  // 前回開いていた本を取得
  const uuid = localStorage.openBookUUID
  const openPage = localStorage.openBookPage
  // 前回開いていた本が取得できたらダイアログで確認
  if (uuid && openPage) {
    resumeBookUUID.value = uuid
    resumeBookPage.value = Number(openPage)
    resumeDialog.value = true
  } else {
    localStorage.removeItem('openBookUUID')
    localStorage.removeItem('openBookPage')
  }

  await initLibraryAndSearch()
})
</script>
