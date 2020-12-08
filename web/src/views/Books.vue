<template>
  <div class="books">
      <v-dialog
      v-model="menuDialog"
      scrollable
      max-width="500px"
    >
      <v-card>
        <v-card-text class="pt-6">
          <v-btn @click="index+=1">
            ページ調整
          </v-btn>
          <v-btn :to="{ name: 'Books'}" class="ml-3">
            戻る
          </v-btn>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text style="height: 300px;">
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn
            color="blue darken-1"
            text
            @click="dialog = false"
          >
            Close
          </v-btn>
          <v-btn
            color="blue darken-1"
            text
            @click="dialog = false"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
     <v-app-bar color="primary" dark dense flat app clipped-left v-if="this.$store.state.showMenuBer">
      <v-toolbar-title>Hinagiku Viewer</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        v-model="searchTitle"
        hide-details
        single-line
      ></v-text-field>
      <v-btn icon @click="search()"><v-icon>mdi-magnify</v-icon></v-btn>
      <v-btn icon @click="reload()"><v-icon>mdi-reload</v-icon></v-btn>
    </v-app-bar>
    <v-container>
      <v-row v-hammer:press="openMenu" >
        <v-col :cols="4" :xs="4" :sm="3" :md="2" :lg="2" v-for="item in booksList" :key="item.uuid">
          <v-card @click="toReaderPage(item)">
            <v-img
              aspect-ratio="0.7"
              :src="getCoverURL(item.uuid)"
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
import Cookies from 'js-cookie'

export default {
  name: 'Books',
  data: function () {
    return {
      menuDialog: false,
      booksList: [],
      searchTitle: ''
    }
  },
  methods: {
    reload () {
      axios.get('/api/books').then((response) => (this.booksList = response.data))
    },
    search () {
      axios.get('/api/books', { params: { file_name_like: this.searchTitle } }).then((response) => (this.booksList = response.data))
    },
    openMenu () {
      this.menuDialog = true
    },
    async toReaderPage (item) {
      if (item.state !== 'cached') {
        axios.request({
          method: 'put',
          url: '/api/books',
          data: { uuids: [item.uuid], state: 'request' }
        })
        await this.$_sleep(5000)
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
    const uuid = Cookies.get('uuid')
    const page = Cookies.get('page')
    this.$_pushNotice('データ' + uuid + ' ' + page, 'success')

    if (uuid && page) {
      router.push({ name: 'BookReader', params: { uuid: uuid }, query: { page: page } })
    } else {
      Cookies.remove('uuid')
      Cookies.remove('page')
    }

    axios.get('/api/books').then((response) => (this.booksList = response.data))
  }
}
</script>
