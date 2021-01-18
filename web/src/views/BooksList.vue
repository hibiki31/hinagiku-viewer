<template>
  <div class="books">
    <search-dialog ref='searchDialog' />
    <!-- エクスポート確認 -->
    <v-dialog
      v-model="exportDialog"
      persistent
      max-width="290"
    >
      <v-card>
        <v-card-title class="headline">
          本をエクスポート
        </v-card-title>
        <v-card-text>検索結果の本を全てエクスポートします</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="success"
            text
            @click="exportDialog = false"
          >
            キャンセル
          </v-btn>
          <v-btn
            color="error"
            text
            @click="searchBooksPut()"
          >
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- ダイアログ -->
    <v-dialog v-model="menuDialog" scrollable max-width="500px">
      <v-card>
        <v-card-title>Select Editor</v-card-title>
        <v-divider></v-divider>
        <v-card-text style="height: 300px">
          <v-rating
            v-model="openItem.rate"
            small
            class="pa-1"
          ></v-rating>
          <v-row class="mt-1">
            <v-text-field label="Title" v-model="openItem.title"></v-text-field>
            <v-btn small icon class="mt-3"><v-icon>mdi-magnify</v-icon></v-btn>
          </v-row>
          <v-row>
            <v-text-field class="mt-0" label="Author" v-model="openItem.author"></v-text-field>
            <v-btn small icon class="mt-3" @click="openItemSearchAuthor()"><v-icon>mdi-magnify</v-icon></v-btn>
          </v-row>
          <v-text-field label="Publisher" v-model="openItem.publisher"></v-text-field>
          <v-btn small class="pa-1" @click="showJson = !showJson">Json</v-btn>
        <div v-if="showJson">{{ this.openItem }}</div>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="blue darken-1" text @click="menuDialog = false">閉じる</v-btn>
          <v-btn color="blue darken-1" text @click="bookInfoSubmit">保存</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="red darken-1" text @click="bookExport" class="ml-3">エクスポート</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- 複数選択ダイアログ -->
    <v-dialog v-model="mulchBooksDialog" scrollable max-width="500px">
      <v-card>
        <v-card-title>
          Range Editor
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text style="height: 300px">
          <v-rating
            v-model="openItem.rate"
            small
            class="pa-3"
          ></v-rating>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="blue darken-1" text @click="mulchBooksDialog = false">閉じる</v-btn>
          <v-btn color="blue darken-1" text @click="searchBooksRate">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- トップバー -->
    <v-app-bar color="primary" dark dense flat app clipped-left v-if="this.$store.state.showMenuBer">
      <v-app-bar-nav-icon @click="showDrawer = !showDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title>HinaV</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="queryTitle"
        hide-details
        single-line
      ></v-text-field>
      <v-btn icon @click="search()"><v-icon>mdi-magnify</v-icon></v-btn>
      <v-btn icon @click="reload()"><v-icon>mdi-reload</v-icon></v-btn>
    </v-app-bar>
    <!-- ドロワー -->
    <v-navigation-drawer
      v-model="showDrawer"
      app
      clipped
    >
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title class="title"></v-list-item-title>
          <v-list-item-subtitle></v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>

      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group>
          <v-select
              :items="libraryList"
              label="Library"
              v-model="queryLibrary"
              dense
              class="pr-2 pl-2"
            ></v-select>
        </v-list-item-group>
      </v-list>

      <!-- 評価するところ -->
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group>
          <v-rating
            v-model="queryRate"
            small
          ></v-rating>
          <v-btn small color="primary" dark @click="queryRate = null" class="ma-1">
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
          <v-btn class="ma-1" small @click="exportDialog = true">Range Export<v-icon>mdi-export</v-icon></v-btn>
          <v-btn class="ma-1" small @click="mulchBooksDialog = true">Range Change<v-icon>mdi-pen</v-icon></v-btn>
        </v-list-item-group>
      </v-list>
      <v-divider class="pb-2"></v-divider>
      <span class="subtitle-2 ml-3">Develop by <a href="https://github.com/hibiki31" class="blue--text">@hibiki31</a></span>
      <span class="subtitle-2 ml-3">v{{this.version}}</span>
      <div class="subtitle-2 ml-3">
        Icons made by
        <a href="https://www.flaticon.com/authors/icon-pond" title="Icon Pond" class="blue--text">Icon Pond</a>
      </div>
    </v-navigation-drawer>
    <v-container>
      <v-row>
        <v-col :cols="4" :xs="4" :sm="3" :md="2" :lg="2" v-for="item in booksList" :key="item.uuid" :id="item.uuid">
          <v-card @click="toReaderPage(item)">
            <v-img
              aspect-ratio="0.7"
              :src="getCoverURL(item.uuid)"
              v-hammer:press="(event)=> openMenu(item)"
            ></v-img>
          </v-card>
        </v-col>
      </v-row>
      <v-pagination
        v-model="page"
        :length="Math.ceil(totalItems/searchQuery.limit)"
        :total-visible="7"
      ></v-pagination>
    </v-container>
  </div>
</template>

<script>
import axios from '@/axios/index'
import router from '../router'
import VueScrollTo from 'vue-scrollto'
import SearchDialog from '../components/SearchDialog'

export default {
  name: 'Books',
  components: {
    SearchDialog
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
      // ダイアログで使用
      showJson: false,
      // ローカルクエリ
      page: 1,
      queryTitle: '',
      queryRate: null,
      queryLibrary: '',
      // 検索クエリ
      searchQuery: {
        limit: 60,
        offset: 0,
        title: null,
        rate: null,
        genre: null,
        library: 'default',
        fileNameLike: '',
        authorLike: null
      },
      // ダイアログで開いているアイテム
      openItem: {},
      // ライブラリ情報
      libraryList: [],
      booksList: [],
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
        this.searchQuery.fileNameLike = this.queryTitle
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
        this.searchQuery.library = this.queryLibrary[0]
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
      const uuids = this.booksList.map(x => x.uuid)
      axios.request({
        method: 'put',
        url: '/api/books',
        data: { uuids: uuids, state: 'export' }
      })
        .then((response) => (this.$_pushNotice('検索範囲のエクスポートを依頼しました', 'success')))
    },
    async searchBooksRate () {
      // 全件取得
      this.mulchBooksDialog = false
      this.searchQuery.offset = 0
      this.searchQuery.limit = 99999
      // 同期をとる
      await this.search()
      // uuidを取得
      const uuids = this.booksList.map(x => x.uuid)
      axios.request({
        method: 'put',
        url: '/api/books',
        data: { uuids: uuids, rate: this.openItem.rate }
      })
        .then((response) => (this.$_pushNotice('検索範囲の本の評価を変更', 'success')))
    },
    openItemSearchAuthor () {
      this.searchQuery.authorLike = this.openItem.author
      this.menuDialog = false
      this.pageChange()
      this.search()
    },
    bookInfoSubmit () {
      this.menuDialog = false
      axios.request({
        method: 'put',
        url: '/api/books',
        data: {
          uuids: [this.openItem.uuid],
          rate: this.openItem.rate,
          publisher: this.openItem.publisher,
          title: this.openItem.title,
          author: this.openItem.author
        }
      })
        .then((response) => (this.$_pushNotice('書籍情報を更新しました', 'success')))
    },
    bookExport () {
      this.menuDialog = false
      axios.request({
        method: 'put',
        url: '/api/books',
        data: { uuids: [this.openItem.uuid], state: 'export' }
      })
        .then((response) => {
          this.$_pushNotice('書籍をエクスポートしました', 'success')
        })
    },
    reload () {
      this.pageChange()
      this.searchQuery = {
        limit: 60,
        offset: 0,
        title: null,
        rate: null,
        genre: null,
        library: 'default',
        fileNameLike: ''
      }
      this.search()
    },
    async search () {
      if (this.serachEnable) {
        await axios.get('/api/books', {
          params: this.searchQuery
        })
          .then((response) => {
            this.booksList = response.data.rows
            this.totalItems = response.data.count
            this.$_pushNotice(this.totalItems + '件', 'info')
          })
        // ローカルストレージにパラメータ格納
        const parsed = JSON.stringify(this.searchQuery)
        localStorage.setItem('searchQuery', parsed)
      }
    },
    pageChange () {
      this.pageWatchEnable = false
      this.page = 1
      this.pageWatchEnable = true
    },
    openMenu (item) {
      this.openItem = item
      this.menuDialog = true
    },
    async toReaderPage (item) {
      // ローカルストレージにパラメータ格納
      const parsed = JSON.stringify(this.searchQuery)
      localStorage.setItem('searchQuery', parsed)
      localStorage.setItem('openBookUUID', item.uuid)

      // 移動
      router.push({ name: 'BookReader', params: { uuid: item.uuid } })
    },
    createCache (book) {
      if (book.state !== 'cached') {
        this.$_pushNotice('キャッシュの作成をリクエスト', 'info')
        axios.request({
          method: 'put',
          url: '/api/books',
          data: { uuids: [book.uuid], state: 'request' }
        })
      }
    },
    getCoverURL (uuid) {
      const api = process.env.VUE_APP_API_HOST
      if (api) {
        return process.env.VUE_APP_API_HOST + '/media/books/' + uuid
      } else {
        return '/media/books/' + uuid
      }
    },
    scrollToUUID () {
      setTimeout(() => {
        const openBookUUID = localStorage.openBookUUID
        this.$forceNextTick(() => {
          if (openBookUUID) {
            const options = { offset: -300 }
            VueScrollTo.scrollTo(document.getElementById(openBookUUID), 400, options)
          }
        })
        localStorage.removeItem('openBookUUID')
      }, 300)
    }
  },

  mounted: async function () {
    // 前回開いていた本を取得
    const uuid = localStorage.backBookUUID
    const page = localStorage.backBookPage
    // 前回開いていた本が取得できたら本を開く
    if (uuid && page) {
      router.push({ name: 'BookReader', params: { uuid: uuid }, query: { page: page } })
      return
    } else {
      localStorage.removeItem('backBookUUID')
      localStorage.removeItem('backBookPage')
    }

    // ライブラリ情報取得
    axios.get('/api/library').then((response) => (this.libraryList = response.data))

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
    this.queryTitle = this.searchQuery.fileNameLike
    this.serachEnable = true

    // 初期ロード
    this.search()

    // 開いていた本へジャンプ
    this.scrollToUUID()
  }
}
</script>
