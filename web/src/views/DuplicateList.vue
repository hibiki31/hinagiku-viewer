<template>
  <div class="duplicateList">
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
      <v-btn icon @click="reload()"><v-icon>mdi-reload</v-icon></v-btn>
    </v-app-bar>
    <v-navigation-drawer v-model="showDrawer" app clipped>
      <v-list nav dense>
      </v-list>
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group>
          <v-btn class="ma-1" small @click="serachDuplicate">
            search<v-icon class="pl-2">mdi-content-duplicate</v-icon>
          </v-btn>
          <v-btn class="ma-1" small @click="toBookList">
            BookList<v-icon class="pl-2">mdi-content</v-icon>
          </v-btn>
        </v-list-item-group>
      </v-list>
      <v-divider></v-divider>
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
    <v-container v-show="!isLoading">
      <div
        class="pb-5"
        v-for="item in booksList"
        :key="item.duplicate_uuid"
        :id="item.duplicate_uuid">
        {{ item.duplicate_uuid }}
        <v-row>
          <v-col
            :xs="4"
            :sm="3"
            :md="3"
            :lg="3"
            v-for="item_book in item.books"
            :key="item_book.duplicate_uuid"
            :id="item_book.duplicate_uuid"
            class="pt-5"
          >
          <v-card>
            <v-row>
              <v-col cols="4">
                <v-img
              aspect-ratio="0.7"
              eager
              :src="getCoverURL(item_book.uuid)"
            ></v-img>
              </v-col>
              <v-col cols="8">
                {{ parseInt(item_book.size / 1024 /1024, 10)  }} MB
                評価：{{ item_book.rate === null ? "なし" : item_book.rate }}
                <div>{{ item_book.file }}</div>
                <v-btn icon @click="deleteBook(item_book.uuid)"><v-icon>mdi-delete-outline</v-icon></v-btn>
              </v-col>
            </v-row>
          </v-card>
        </v-col>
        </v-row>
      </div>
    </v-container>
  </div>
</template>

<script>
import axios from '@/axios/index'
import router from '@/router'
// import store from '@/store'
export default {
  name: 'DuplicateList',
  components: {
  },
  head: {
    title: function () {
      return {
        inner: 'HinaV',
        separator: '|',
        complement: '重複リスト'
      }
    }
  },
  data: function () {
    return {
      showDrawer: true,
      isLoading: true,
      version: require('../../package.json').version,
      booksList: [
      ]
    }
  },
  computed: {
  },
  watch: {
  },
  methods: {
    serachDuplicate () {
      axios
        .request({
          method: 'patch',
          url: '/media/library',
          data: { state: 'sim_all' }
        })
        .then((response) => {
          this.$_pushNotice('重複の検索を開始' + response.data.status, 'success')
        })
    },
    reload () {
      axios.get('/media/books/duplicate').then((response) => {
        this.booksList = response.data
        this.isLoading = false
      })
    },
    getCoverURL (uuid) {
      const api = process.env.VUE_APP_API_HOST
      if (api) {
        return process.env.VUE_APP_API_HOST + '/media/books/' + uuid
      } else {
        return '/media/books/' + uuid
      }
    },
    deleteBook (uuid) {
      axios.request({
        method: 'delete',
        url: '/api/books/' + uuid
      })
        .then((response) => {
          this.$_pushNotice('削除しました' + response.data.status, 'success')
          this.reload()
        })
    },
    toBookList () {
      router.push({ name: 'BooksList' })
    }
  },
  mounted: function () {
    this.reload()
  }
}
</script>
