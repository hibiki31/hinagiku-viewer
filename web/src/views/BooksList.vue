<template>
  <div class="booksList">
    <SearchDialog ref="searchDialog" @search="search" />
    <BookDetailDialog ref="bookDetailDialog" @search="search" />
    <range-change-dialog ref="rangeChangeDialog" @search="search" />
    <!-- トップバー -->
    <v-app-bar
      color="primary"
      dark
      dense
      flat
      app
      clipped-left
    >
      <v-app-bar-nav-icon
        @click="showDrawer = !showDrawer"
      ></v-app-bar-nav-icon>
      <v-toolbar-title></v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="queryTitle"
        hide-details
        single-line
      ></v-text-field>
      <v-btn icon @click="$refs.searchDialog.openDialog()"><v-icon>mdi-magnify</v-icon></v-btn>
      <v-btn icon @click="reload()"><v-icon>mdi-reload</v-icon></v-btn>
    </v-app-bar>
    <!-- ドロワー -->
    <v-navigation-drawer v-model="showDrawer" app clipped>
      <v-list nav dense>
        <v-list-item-group>
          <v-select
            :items="libraryList"
            label="Library"
            v-model="queryLibrary"
            item-text="name"
            item-value="id"
            dense
            class="pr-2 pl-2 pt-3"
          ></v-select>
        </v-list-item-group>
      </v-list>

      <!-- 評価するところ -->
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group>
          <v-rating v-model="queryRate" small></v-rating>
        </v-list-item-group>
        <v-list-item-group>
          <v-btn small color="primary" dark @click="queryRate = null" class="ma-1" width="70">
            All Rate
          </v-btn>
          <v-btn small color="gray" dark @click="queryRate = 0" class="ma-1" width="70">
            No Rate
          </v-btn>
        </v-list-item-group>
      </v-list>
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group>
          <v-btn class="ma-1" small color="error" @click="exportDialog = true" disabled
            >Range Export<v-icon class="pl-1">mdi-export</v-icon></v-btn
          >
          <v-btn class="ma-1" small color="primary" @click="$refs.rangeChangeDialog.openDialog()"
            >Range Change<v-icon>mdi-pen</v-icon></v-btn
          >
          <v-btn class="ma-1" small @click="loadLibrary">
            Load Library<v-icon class="pl-2">mdi-book-refresh</v-icon>
          </v-btn>
          <v-btn class="ma-1" small @click="toDuplicateView">
            Duplicate List<v-icon class="pl-2">mdi-content-duplicate</v-icon>
          </v-btn>
        </v-list-item-group>
      </v-list>
      <v-divider></v-divider>
      <v-switch
        @change="$store.dispatch('setShowListMode', $event)"
        class="ma-3"
        label="リスト表示"
        dense
        hide-details
      ></v-switch>
      <!-- ライセンス -->
      <v-divider class="pb-2"></v-divider>
      <span class="subtitle-2 ml-3"
        >Develop by
        <a href="https://github.com/hibiki31" class="blue--text"
          >@hibiki31</a
        ></span
      >
      <span class="subtitle-2 ml-3">v{{ this.version }}</span>
      <div class="subtitle-2 ml-3">
        Icons made by
        <a
          href="https://www.flaticon.com/authors/icon-pond"
          title="Icon Pond"
          class="blue--text"
          >Icon Pond</a
        >
      </div>
    </v-navigation-drawer>
    <v-progress-linear
      indeterminate
      color="yellow darken-2"
      v-show="isLoading"
    ></v-progress-linear>
    <!-- メインの一覧 -->
    <v-container v-show="!isLoading">
      <BooksListTable
        v-if="showListMode"
        @toReaderPage="toReaderPage"
        @openMenu="openMenu"
        @search="search"
      />
      <BooksListThum v-else @toReaderPage="toReaderPage" @openMenu="openMenu"/>
    </v-container>
  <v-pagination
    v-model="page"
    :length="maxPage"
    :total-visible="17"
    class="ma-3"
  ></v-pagination>
  </div>
</template>

<script>
import axios from '@/axios/index'
import router from '../router'
import VueScrollTo from 'vue-scrollto'
import SearchDialog from '../components/dialog/SearchDialog'
import BookDetailDialog from '../components/dialog/BookDetailDialog'

import BooksListTable from '../components/BooksListTable'
import BooksListThum from '../components/BooksListThum'
import store from '@/store'

import RangeChangeDialog from '../components/dialog/RangeChangeDialog.vue'

export default {
  name: 'BooksList',
  components: {
    SearchDialog,
    BooksListTable,
    BooksListThum,
    BookDetailDialog,
    RangeChangeDialog
  },
  head: {
    title: function () {
      return {
        inner: 'HinaV',
        separator: '|',
        complement: 'ホーム'
      }
    }
  },
  data: function () {
    return {
      // 監視パラーメータで重複を避けるため検索を行うかのフラグ
      serachEnable: true,
      pageWatchEnable: true,
      // 表示ステータス
      menuDialog: false,
      exportDialog: false,
      mulchBooksDialog: false,
      showDrawer: true,
      isLoading: true,
      // ダイアログで開いているアイテム
      openItem: {
        userData: {
          rate: null
        }
      },
      // ライブラリ情報
      libraryList: [],
      totalItems: 0,
      // バージョン固定値
      version: require('../../package.json').version
    }
  },
  computed: {
    searchQuery: () => store.getters.searchQuery,
    booksList: () => store.getters.booksList,
    booksCount: () => store.getters.booksCount,
    maxPage: () => Math.ceil(store.getters.booksCount / store.getters.searchQuery.limit),
    showListMode: () => store.getters.showListMode,
    page: {
      get () {
        const query = this.searchQuery
        return Number((query.offset / query.limit) + 1)
      },
      set (value) {
        const query = this.searchQuery
        query.offset = query.limit * (value - 1)
        store.dispatch('setSearchQuery', query)
        this.search(false)
      }
    },
    queryTitle: {
      get () {
        return this.searchQuery.fullText
      },
      set (value) {
        const query = this.searchQuery
        query.fullText = value
        store.dispatch('setSearchQuery', query)
        this.search(true)
      }
    },
    queryLibrary: {
      get () {
        return this.searchQuery.libraryId
      },
      set (value) {
        const query = this.searchQuery
        query.libraryId = value
        store.dispatch('setSearchQuery', query)
        this.search(true)
      }
    },
    queryRate: {
      get () {
        return this.searchQuery.rate
      },
      set (value) {
        const query = this.searchQuery
        query.rate = value
        store.dispatch('setSearchQuery', query)
        this.search(true)
      }
    }
  },
  watch: {
  },
  methods: {
    async search (resetOffset = false) {
      this.isLoading = true
      await store.dispatch('serachBooks', resetOffset)
      this.$_pushNotice(store.getters.booksCount + '件', 'info')
      this.isLoading = false
      this.scrollToUUID()
    },
    reload () {
      const query = this.searchQuery
      query.fullText = ''
      store.dispatch('setSearchQuery', query)
      this.search(true)
    },
    scrollToUUID () {
      setTimeout(() => {
        const backBookUUID = localStorage.backBookUUID
        this.$forceNextTick(() => {
          if (backBookUUID) {
            const options = { offset: -300 }
            VueScrollTo.scrollTo(
              document.getElementById(backBookUUID),
              400,
              options
            )
          }
        })
        localStorage.removeItem('backBookUUID')
      }, 300)
    },
    loadLibrary () {
      axios
        .request({
          method: 'patch',
          url: '/media/library',
          data: { state: 'load' }
        })
        .then((response) => {
          this.$_pushNotice('ライブラリのリロードを開始' + response.data.status, 'success')
        })
    },
    openMenu (item) {
      this.$refs.bookDetailDialog.openDialog(item)
    },
    async toReaderPage (item) {
      // ローカルストレージにパラメータ格納
      this.createCache(item)
      const parsed = JSON.stringify(this.searchQuery)
      localStorage.setItem('searchQuery', parsed)
      localStorage.setItem('backBookUUID', item.uuid)

      // 移動
      router.push({ name: 'BookReader', params: { uuid: item.uuid } })
    },
    createCache (book) {
      this.$_pushNotice('キャッシュの作成をリクエスト', 'info')
      axios.request({
        method: 'patch',
        url: '/media/books',
        data: {
          uuid: book.uuid,
          height: window.innerHeight * window.devicePixelRatio
        }
      })
    },
    toDuplicateView () {
      router.push({ name: 'DuplicateList' })
    }
  },

  mounted: function () {
    // 前回開いていた本を取得
    const uuid = localStorage.openBookUUID
    const page = localStorage.openBookPage
    // 前回開いていた本が取得できたら本を開く
    if (uuid && page) {
      router.push({
        name: 'BookReader',
        params: { uuid: uuid },
        query: { startPage: page }
      })
      return
    } else {
      localStorage.removeItem('openBookUUID')
      localStorage.removeItem('openBookPage')
    }

    // ライブラリ情報取得
    axios
      .get('/api/librarys')
      .then((response) => (this.libraryList = response.data))

    // 初期ロード
    this.search()
  }
}
</script>
