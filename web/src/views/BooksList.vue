<template>
  <div class="booksList">
    <SearchDialog ref="searchDialog" @search="search" />
    <BookDetailDialog ref="bookDetailDialog" />
    <!-- エクスポート確認 -->
    <v-dialog v-model="exportDialog" persistent max-width="290">
      <v-card>
        <v-card-title class="headline"> 本をエクスポート </v-card-title>
        <v-card-text>検索結果の本を全てエクスポートします</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="success" text @click="exportDialog = false">
            キャンセル
          </v-btn>
          <v-btn color="error" text @click="searchBooksPut()"> OK </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- 複数選択ダイアログ -->
    <v-dialog v-model="mulchBooksDialog" scrollable max-width="500px">
      <v-card>
        <v-card-title> Range Editor </v-card-title>
        <v-divider></v-divider>
        <v-card-text style="height: 300px">
          <v-rating v-model="openItem.rate" small class="pa-3"></v-rating>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="blue darken-1" text @click="mulchBooksDialog = false"
            >閉じる</v-btn
          >
          <v-btn color="blue darken-1" text @click="searchBooksRate"
            >保存</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
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
          <v-btn
            small
            color="primary"
            dark
            @click="queryRate = null"
            class="ma-1"
          >
            All Rate
          </v-btn>
          <v-btn small color="gray" dark @click="queryRate = 0" class="ma-1">
            No Rate
          </v-btn>
        </v-list-item-group>
      </v-list>
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group>
          <v-btn class="ma-1" small @click="exportDialog = true"
            >Range Export<v-icon>mdi-export</v-icon></v-btn
          >
          <v-btn class="ma-1" small @click="mulchBooksDialog = true"
            >Range Change<v-icon>mdi-pen</v-icon></v-btn
          >
          <v-btn class="ma-1" small @click="loadLibrary">
            Load
          </v-btn>
          <v-switch
            @change="$store.dispatch('setShowListMode', $event)"
            class="ma-1"
            label="リスト表示"
            dense
            hide-details
          ></v-switch>
        </v-list-item-group>
      </v-list>
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
      <v-pagination
        v-model="page"
        :length="maxPage"
        :total-visible="9"
        class="pt-5"
      ></v-pagination>
    </v-container>
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

export default {
  name: 'BooksList',
  components: {
    SearchDialog,
    BooksListTable,
    BooksListThum,
    BookDetailDialog
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
  computed: {
    booksList: () => store.getters.booksList,
    booksCount: () => store.getters.booksCount,
    maxPage: () => Math.ceil(store.getters.booksCount / store.getters.searchQuery.limit),
    showListMode: () => store.getters.showListMode
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
      showDrawer: false,
      isLoading: true,
      // ローカルクエリ
      page: 1,
      queryTitle: '',
      queryRate: null,
      queryLibrary: 0,
      // 検索クエリ
      searchQuery: {
        limit: 60,
        offset: 0,
        title: null,
        rate: null,
        genre: null,
        libraryId: null,
        fullText: '',
        authorLike: null
      },
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

  watch: {
    page: {
      handler () {
        window.scrollTo({ top: 0 })
        this.searchQuery.offset = this.searchQuery.limit * (this.page - 1)
        if (this.pageWatchEnable) {
          this.search()
        }
      },
      deep: true
    },
    queryTitle: {
      handler () {
        window.scrollTo({ top: 0 })
        this.pageChange()
        this.searchQuery.fullText = this.queryTitle
        this.search(true)
      },
      deep: true
    },
    queryRate: {
      handler () {
        window.scrollTo({ top: 0 })
        this.pageChange()
        this.searchQuery.rate = this.queryRate
        this.search()
      },
      deep: true
    },
    queryLibrary: {
      handler () {
        window.scrollTo({ top: 0 })
        this.pageChange()
        this.searchQuery.libraryId = this.queryLibrary
        this.search()
      },
      deep: true
    }
  },

  methods: {
    async searchBooksPut () {
      // 全件取得
      this.mulchBooksDialog = false
      this.searchQuery.offset = 0
      this.searchQuery.limit = 99999
      // 同期をとる
      await this.search()
      // uuidを取得
      const uuids = this.booksList.map((x) => x.uuid)
      axios
        .request({
          method: 'put',
          url: '/api/books',
          data: { uuids: uuids, state: 'export' }
        })
        .then((response) =>
          this.$_pushNotice('検索範囲のエクスポートを依頼しました', 'success')
        )
    },
    async searchBooksRate () {
      // 全件取得
      this.mulchBooksDialog = false
      this.searchQuery.offset = 0
      this.searchQuery.limit = 99999
      // 同期をとる
      await this.search()
      // uuidを取得
      const uuids = this.booksList.map((x) => x.uuid)
      axios
        .request({
          method: 'put',
          url: '/api/books',
          data: { uuids: uuids, rate: this.openItem.rate }
        })
        .then((response) =>
          this.$_pushNotice('検索範囲の本の評価を変更', 'success')
        )
    },
    openItemSearchAuthor () {
      this.searchQuery.authorLike = this.openItem.author
      this.menuDialog = false
      this.pageChange()
      this.search()
    },
    bookInfoSubmitButton (item) {
      this.openItem = item
      this.bookInfoSubmit()
    },
    bookExport () {
      this.menuDialog = false
      axios
        .request({
          method: 'put',
          url: '/api/books',
          data: { uuids: [this.openItem.uuid], state: 'export' }
        })
        .then((response) => {
          this.$_pushNotice('書籍をエクスポートしました', 'success')
        })
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
    reload () {
      this.pageChange()
      const oldsearchQuery = Object.assign({}, this.searchQuery)
      this.searchQuery = {
        limit: 60,
        offset: 0,
        title: null,
        rate: null,
        genre: null,
        libraryId: oldsearchQuery.libraryId,
        fullText: ''
      }
      this.search()
    },
    async search () {
      this.isLoading = true
      await store.dispatch('serachBooks', this.searchQuery)
      this.$_pushNotice(store.getters.booksCount + '件', 'info')
      this.isLoading = false
      this.scrollToUUID()
    },
    pageChange () {
      this.pageWatchEnable = false
      this.page = 1
      this.pageWatchEnable = true
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
      .get('/api/library')
      .then((response) => (this.libraryList = response.data))

    // 検索パラメータを復元
    try {
      const getParam = JSON.parse(localStorage.getItem('searchQuery'))
      // 上書きじゃなくてあったKeyを追加
      for (const key in getParam) {
        this.searchQuery[key] = getParam[key]
      }
    } catch (e) {
      localStorage.removeItem('searchQuery')
    }

    // クエリから戻す
    this.serachEnable = false
    this.page = Math.ceil(this.searchQuery.offset / this.searchQuery.limit + 1)
    this.queryTitle = this.searchQuery.fullText
    this.serachEnable = true

    // 初期ロード
    this.search()
  }
}
</script>
