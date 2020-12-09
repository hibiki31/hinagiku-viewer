<template>
  <div class="books">
    <!-- ダイアログ -->
    <v-dialog v-model="menuDialog" scrollable max-width="500px">
      <v-card>
        <v-card-text class="pt-6">
          <v-btn @click="goLibrary()" class="ml-3">ライブラリへ戻る</v-btn>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text style="height: 300px">
          <v-rating
            v-model="openItem.rate"
            small
          ></v-rating>
          {{ this.openItem }}
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="blue darken-1" text @click="menuDialog = false">閉じる</v-btn>
          <v-btn color="blue darken-1" text @click="bookInfoSubmit">保存</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- トップバー -->
    <v-app-bar color="primary" dark dense flat app clipped-left v-if="this.$store.state.showMenuBer">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>HinaV</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="searchTitle"
        hide-details
        single-line
      ></v-text-field>
      <v-btn icon @click="search()"><v-icon>mdi-magnify</v-icon></v-btn>
      <v-btn icon @click="reload()"><v-icon>mdi-reload</v-icon></v-btn>
    </v-app-bar>
    <!-- ドロワー -->
    <v-navigation-drawer
      v-model="drawer"
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
          <v-rating
            v-model="searchRate"
            small
          ></v-rating>
          <v-btn icon small @click="searchRate = null"><v-icon>mdi-reload</v-icon></v-btn>
          <v-select
          :items="libraryList"
          v-model="searchLibrary"
          label="ライブラリー"
          dense
        ></v-select>
        </v-list-item-group>
      </v-list>
      <v-divider class="pb-2"></v-divider>
      <span class="subtitle-2 ml-3">Develop by <a href="https://github.com/hibiki31" class="blue--text">@hibiki31</a></span>
      <span class="subtitle-2 ml-1">v{{this.version}}</span>
    </v-navigation-drawer>
    <v-container>
      <v-row>
        <v-col :cols="4" :xs="4" :sm="3" :md="2" :lg="2" v-for="item in booksList" :key="item.uuid">
          <v-card @click="toReaderPage(item)">
            <v-img
              aspect-ratio="0.7"
              :src="getCoverURL(item.uuid)"
              v-hammer:press="(event)=> openMenu(item)"
            ></v-img>
            <!-- <v-card-title>
              {{ item.title }}
            </v-card-title>
            <v-card-text>
              <v-icon v-if="item.state=='cached'" color="primary">mdi-checkbox-marked-circle-outline</v-icon>
              <v-icon v-else >mdi-checkbox-marked-circle-outline</v-icon>
            </v-card-text> -->
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import axios from '@/axios/index'
import router from '../router'

export default {
  name: 'Books',
  data: function () {
    return {
      version: require('../../package.json').version,
      drawer: false,
      menuDialog: false,
      booksList: [],
      searchTitle: '',
      searchRate: null,
      searchGenre: null,
      searchLibrary: ['default', 0],
      openItem: {},
      libraryList: []
    }
  },
  watch: {
    searchRate: function (newValue, oldValue) {
      this.search()
    },
    searchLibrary: function (newValue, oldValue) {
      this.search()
    }
  },
  methods: {
    bookInfoSubmit () {
      this.menuDialog = false
      axios.request({
        method: 'put',
        url: '/api/books',
        data: { uuids: [this.openItem.uuid], rate: this.openItem.rate }
      })
        .then((response) => (this.$_pushNotice('書籍情報を更新しました', 'success')))
    },
    reload () {
      this.searchTitle = null
      this.searchRate = null
      this.searchGenre = null
      this.search()
    },
    search () {
      axios.get('/api/books', {
        params: {
          file_name_like: this.searchTitle,
          rate: this.searchRate,
          library: this.searchLibrary[0]
        }
      })
        .then((response) => (this.booksList = response.data))
    },
    openMenu (item) {
      this.openItem = item
      this.menuDialog = true
    },
    async toReaderPage (item) {
      if (item.state !== 'cached') {
        axios.request({
          method: 'put',
          url: '/api/books',
          data: { uuids: [item.uuid], state: 'request' }
        })
      }
      router.push({ name: 'BookReader', params: { uuid: item.uuid } })
    },
    getCoverURL (uuid) {
      const api = process.env.VUE_APP_API_HOST
      if (api) {
        return process.env.VUE_APP_API_HOST + '/media/books/' + uuid
      } else {
        return '/media/books/' + uuid
      }
    }
  },
  mounted: function () {
    const uuid = localStorage.uuid
    const page = localStorage.page
    // this.$_pushNotice('データ' + uuid + ' ' + page, 'success')

    if (uuid && page) {
      router.push({ name: 'BookReader', params: { uuid: uuid }, query: { page: page } })
    } else {
      localStorage.removeItem('uuid')
      localStorage.removeItem('page')
    }
    this.search()
    axios.get('/api/library').then((response) => (this.libraryList = response.data))
  }
}
</script>
