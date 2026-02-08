<template>
  <div class="books" style="height: 100vh">
    <!-- メニューダイアログ -->
    <v-dialog v-model="menuDialog" scrollable max-width="500px">
      <v-card>
        <v-card-text class="pt-6">
          <v-btn @click="nowPage += 1">
            ページ調整
          </v-btn>
          <v-btn class="ml-3" @click="goLibrary()">
            ライブラリへ戻る
          </v-btn>
          <v-row class="mt-3 pa-0">
            <v-col cols="12" sm="4">
              <v-select
                v-model="settings.cachePage"
                :items="cachePageItems"
                label="先読みページ数"
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="4">
              <v-select
                v-model="settings.customHeight"
                :items="[600, 1080, 1920]"
                label="ページ縦サイズ"
                density="compact"
              />
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="loadSizeMB"
                label="ロードサイズ MB"
                clearable
                readonly
                density="compact"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" sm="6">
              <v-switch
                v-model="settings.showTowPage"
                label="見開き表示"
                density="compact"
                hide-details
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-switch
                v-model="settings.showWindwSize"
                label="画面サイズで表示"
                density="compact"
                hide-details
              />
            </v-col>
          </v-row>
          <v-slider
            v-model="nowPage"
            label="ページ"
            :min="0"
            :max="bookInfo.page"
            thumb-label
          />
          <v-rating
            :model-value="bookInfo.userData.rate ?? undefined"
            size="small"
            class="pa-1"
            @update:model-value="(value) => { bookInfo.userData.rate = value as number; bookInfoSubmit(); }"
          />
        </v-card-text>
        <v-divider />
        <v-card-actions>
          <v-btn color="blue-darken-1" variant="text" @click="menuDialog = false">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- 画像表示 -->
    <div
      :class="{
        'image-base-width': settings.showBaseWidth,
        'image-base-height': !settings.showBaseWidth
      }"
      class="image-area"
      @click="actionPageNext"
      @contextmenu.prevent="menuDialog = true"
    >
      <template v-if="pageBlob[nowPage - 1]">
        <img v-if="settings.showTowPage" :src="pageBlob[nowPage + 0] || ''">
        <img :src="pageBlob[nowPage - 1] || ''">
      </template>
      <template v-else>
        <v-progress-circular indeterminate size="50" color="primary" />
      </template>
    </div>
    <!-- 下部メニュー -->
    <div
      v-if="subMenu"
      class="text-center"
      style="position: fixed; bottom: 5px; z-index: 10; width: 100%"
    >
      <v-container>
        <v-switch v-model="settings.showTowPage" label="見開き表示" hide-details />
        <v-switch v-model="settings.showBaseWidth" label="横幅に合わせる" hide-details />
        <v-slider v-model="nowPage" :min="1" :max="bookInfo.page" thumb-label />
      </v-container>
    </div>
    <!-- 上部メニュー -->
    <div
      v-if="subMenu"
      class="text-center"
      style="position: fixed; top: 10px; z-index: 10; width: 100%"
    >
      <v-container>
        <v-btn icon @click="actionFirstPage">
          <v-icon>mdi-page-first</v-icon>
        </v-btn>
        <v-btn icon @click="nowPage += 1">
          <v-icon>mdi-book-open-page-variant</v-icon>
        </v-btn>
        <v-btn icon class="ml-3" @click="goLibrary">
          <v-icon>mdi-close-circle</v-icon>
        </v-btn>
        <v-btn icon class="ml-3" @click="menuDialog = true">
          <v-icon>mdi-dots-horizontal-circle</v-icon>
        </v-btn>
      </v-container>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiClient } from '@/func/client'
import { usePushNotice } from '@/composables/utility'

const router = useRouter()
const route = useRoute()
const { pushNotice } = usePushNotice()

const menuDialog = ref(false)
const subMenu = ref(false)
const uuid = ref('')
const nowPage = ref(1)
const nowLoading = ref(0)
const pageMove = ref(false)
const pageBlob = ref<(string | null)[]>([])
const isCompletedRead = ref(false)
const cachePageItems = [2, 4, 8, 16, 32, 64]
const loadSizeB = ref(0)
const loadSizeMB = ref(0)

const bookInfo = reactive<{
  page: number
  uuid?: string
  userData: {
    rate: number | null
    openPage?: number | null
  }
}>({
  page: 0,
  userData: {
    rate: null
  }
})

const settings = reactive({
  cachePage: 32,
  mulchLoad: 4,
  showTowPage: false,
  showBaseWidth: true,
  showWindwSize: false,
  customHeight: 1024,
  windowHeight: Math.round(window.innerHeight * window.devicePixelRatio)
})

// ライブラリに戻る
const goLibrary = () => {
  if (!isCompletedRead.value) {
    apiClient.PATCH('/api/books/user-data', {
      body: {
        uuids: [uuid.value],
        status: 'pause',
        page: nowPage.value
      }
    })
  }
  localStorage.removeItem('openBookUUID')
  localStorage.removeItem('openBookPage')
  router.push('/')
}

const bookInfoSubmit = () => {
  apiClient.PUT('/api/books/user-data', {
    body: {
      uuids: [bookInfo.uuid!],
      rate: bookInfo.userData.rate ?? undefined
    }
  }).then(({ error }) => {
    if (!error) {
      pushNotice('評価を更新しました', 'success')
    }
  })
}

// ページを進めるときに
const getDLoadingPage = async () => {
  const cachePage = settings.cachePage
  const mulchLoad = settings.mulchLoad
  let pageOffset: number | null = null

  // ロードされてないpageを取得
  for (let i = 0; i < cachePage; i++) {
    if (pageBlob.value[nowPage.value - 1 + i] == null) {
      pageOffset = i
      break
    }
  }
  const page = nowPage.value + (pageOffset || 0)

  // 先読み限界
  if (pageOffset === null) {
    return
  }
  // ページ移動
  if (pageMove.value) {
    return
  }
  // 指定ページが0以下 or ページ数より大きかったら終了
  if (page <= 0 || page > bookInfo.page) {
    return
  }
  // ロード中
  if (nowLoading.value >= mulchLoad) {
    return
  }

  nowLoading.value += 1

  let heightParam = settings.customHeight
  if (settings.showWindwSize) {
    heightParam = settings.windowHeight
  }

  try {
    // Blob取得: openapi-fetchのparseAsオプションでblob取得
    const response = await fetch(
      `${import.meta.env.VITE_APP_API_HOST || ''}/media/books/${uuid.value}/${page}?height=${heightParam}`,
      {
        headers: {
          'Authorization': `Bearer ${(await import('js-cookie')).default.get('accessToken') || ''}`
        }
      }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const contentLength = response.headers.get('content-length')
    loadSizeB.value += Number(contentLength)
    loadSizeMB.value = Math.round(loadSizeB.value / 10000) / 100
    const blob = await response.blob()
    pageBlob.value[page - 1] = window.URL.createObjectURL(blob)
    nowLoading.value -= 1
    getDLoadingPage()
  } catch (error) {
    console.log(error)
    pushNotice('エラーが発生したので再試行します', 'error')
    pageBlob.value[page - 1] = null
    nowLoading.value -= 1
    setTimeout(getDLoadingPage, 1000)
  }
}

const actionPageNext = () => {
  if (settings.showTowPage) {
    nowPage.value += 2
  } else {
    nowPage.value += 1
  }
  if (bookInfo.page <= nowPage.value) {
    nowPage.value = bookInfo.page
    if (!isCompletedRead.value) {
      apiClient.PATCH('/api/books/user-data', {
        body: {
          uuids: [uuid.value],
          status: 'close'
        }
      })
    }
    isCompletedRead.value = true
    menuDialog.value = true
  }
}

const actionFirstPage = () => {
  nowPage.value = 1
}

const loadSettings = () => {
  try {
    const getParam = JSON.parse(localStorage.getItem('readerSettings') || '{}')
    for (const key in getParam) {
      if (key in settings) {
        ;(settings as Record<string, unknown>)[key] = getParam[key]
      }
    }
  } catch (e) {
    console.log(e)
    localStorage.removeItem('readerSettings')
  }
}

watch(nowPage, () => {
  getDLoadingPage()
  localStorage.openBookPage = nowPage.value
})

watch(
  settings,
  () => {
    localStorage.setItem('readerSettings', JSON.stringify(settings))
  },
  { deep: true }
)

onMounted(async () => {
  // パスからUUIDを取得して，ローカルストレージに保存
  const paramUuid = (route.params as { uuid?: string | string[] }).uuid
  uuid.value = Array.isArray(paramUuid) ? paramUuid[0] : (paramUuid || '')
  localStorage.openBookUUID = uuid.value

  // ページの指定はあるか？
  if (route.query.startPage) {
    nowPage.value = Number(route.query.startPage)
  }

  // 先読み用アレイ初期化
  pageBlob.value = Array(4).fill(null)
  getDLoadingPage()

  // 書籍情報取得
  try {
    const { data, error } = await apiClient.GET('/api/books', {
      params: {
        query: { uuid: uuid.value }
      }
    })
    if (error) throw error
    if (data && data.rows.length > 0) {
      Object.assign(bookInfo, data.rows[0])
      if (bookInfo.userData.openPage !== null && bookInfo.userData.openPage !== undefined) {
        nowPage.value = bookInfo.userData.openPage
      }
      pageBlob.value = [...pageBlob.value, ...Array(bookInfo.page - 4).fill(null)]
    }
  } catch (error) {
    console.error('書籍情報取得エラー:', error)
  }

  apiClient.PATCH('/api/books/user-data', {
    body: {
      uuids: [uuid.value],
      status: 'open'
    }
  })

  loadSettings()
})

onBeforeUnmount(() => {
  pageMove.value = true
})
</script>

<style scoped lang="scss">
.image-area {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  cursor: pointer;
}

.image-base-width > img {
  max-width: 100%;
  height: auto;
  width: auto;
}

.image-base-height > img {
  max-height: 100vh;
  height: 100vh;
}

.image-base-height {
  max-height: 100vh;
  height: 100vh;
}
</style>
