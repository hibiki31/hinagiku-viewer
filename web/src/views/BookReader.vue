<template>
  <div class="books">
    <!-- ダイアログ -->
    <v-dialog v-model="menuDialog" scrollable max-width="500px">
      <v-card>
        <v-card-text class="pt-6">
          <v-btn @click="nowPage += 1"> ページ調整 </v-btn>
          <v-btn @click="goLibrary()" class="ml-3">ライブラリへ戻る</v-btn>
          <v-row class="mt-3 pa-0">
            <v-col cols="12" sm="4">
              <v-select
                :items="cachePageItems"
                v-model="settings.cachePage"
                label="先読みページ数"
                dense
              ></v-select>
            </v-col>
            <v-col cols="12" sm="4">
              <v-select
                :items="[600, 1080, 1920]"
                v-model="settings.customHeight"
                label="ページ縦サイズ"
                dense
              ></v-select>
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="this.loadSizeMB"
                label="ロードサイズ MB"
                clearable
                readonly
                dense
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" sm="6">
              <v-switch
                v-model="settings.showTowPage"
                label="見開き表示"
                dense
                hide-details
              ></v-switch>
            </v-col>
            <v-col cols="12" sm="6">
              <v-switch
                v-model="settings.showWindwSize"
                label="画面サイズで表示"
                dense
                hide-details
              ></v-switch>
            </v-col>
          </v-row>
          <v-slider
            v-model="nowPage"
            label="ページ"
            :min="0"
            :max="this.bookInfo.page"
            thumb-label
          ></v-slider>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text style="height: 300px" class="selectable">
          {{ bookInfo }}
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="blue darken-1" text @click="menuDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- 画像表示ぶ-->
    <div
      v-bind:class="{ 'image-base-width': settings.showBaseWidth, 'image-base-height': !settings.showBaseWidth }"
      class="text-center"
    >
      <!-- 見開き表示 -->
      <template v-if="settings.showTowPage">
        <img
          v-hammer:swipe="onSwipe"
          v-hammer:press="openSubMenu"
          v-hammer:tap="pageNext"
          :src="this.pageBlob[this.nowPage+0]"
        />
        <img
          v-hammer:swipe="onSwipe"
          v-hammer:press="openSubMenu"
          v-hammer:tap="pageNext"
          :src="this.pageBlob[this.nowPage-1]"
        />
      </template>
      <!-- スマホ用片面 -->
      <template v-else>
        <img
          v-hammer:swipe="onSwipe"
          v-hammer:press="openSubMenu"
          v-hammer:tap="pageNext"
          :src="this.pageBlob[this.nowPage-1]"
        />
      </template>
      <!-- 確認用 -->
      <div style="display: none;">
        <img
          id="viewer-page-1"
          v-on:load="imageLoad('viewer-page-1')"
          :src="this.pageBlob[this.nowPage+0]"
        />
        <img
          id="viewer-page-2"
          v-on:load="imageLoad('viewer-page-2')"
          :src="this.pageBlob[this.nowPage-1]"
        />
      </div>
    </div>
    <!-- 下部メニュ -->
    <div fluid class="text-center" style="position: fixed; bottom: 5px; z-index: 10; width: 100%" v-show="subMenu">
      <v-container>
        <v-switch
          v-model="settings.showTowPage"
          label="見開き表示"
          hide-details
        ></v-switch>
        <v-switch
          v-model="settings.showBaseWidth"
          label="横幅に合わせる"
          hide-details
        ></v-switch>
        <v-slider
          v-model="nowPage"
          :min="1"
          :max="this.bookInfo.page"
          thumb-label
        ></v-slider>
      </v-container>
    </div>

    <div fluid class="text-center" style="position: fixed; top: 10px; z-index: 10; width: 100%" v-show="subMenu">
      <v-container>
        <v-btn icon @click="nowPage+=1">
          <v-icon>mdi-book-open-page-variant</v-icon>
        </v-btn>
        <v-btn icon @click="goLibrary" class="ml-3">
          <v-icon>mdi-close-circle</v-icon>
        </v-btn>
        <v-btn icon @click="menuDialog=true" class="ml-3">
          <v-icon>mdi-dots-horizontal-circle</v-icon>
        </v-btn>
      </v-container>
    </div>
  </div>
</template>

<script>
import axios from '@/axios/index'
import LoadingImage from '@/assets/loading.gif'
import router from '../router'

export default {
  name: 'Books',
  head: {
    title: function () {
      return {
        inner: 'HinaV',
        separator: '|',
        complement: this.bookInfo.title
      }
    }
  },
  data: function () {
    return {
      dict: {
        2: 'left',
        4: 'right',
        8: 'top',
        16: 'bottom'
      },
      menuDialog: false,
      subMenu: false,
      heightOffcet: 0,
      uuid: '',
      page: 0,
      nowPage: 1,
      nowLoading: 0,
      pageMove: false,
      booksList: [],
      width: window.innerWidth,
      height: window.innerHeight,
      bookInfo: {},
      pageBlob: [],
      cachePageItems: [2, 4, 8, 16, 32, 64],
      loadSizeB: 0,
      loadSizeMB: 0,
      viewerPage1TowPage: false,
      viewerPage2TowPage: false,
      settings: {
        cachePage: 32,
        mulchLoad: 4,
        showTowPage: false,
        showBaseWidth: false,
        showWindwSize: false,
        customHeight: 1024,
        windowHeight: window.innerHeight * window.devicePixelRatio
      }
    }
  },
  watch: {
    nowPage: function (newPage, oldPage) {
      this.getDLoadingPage()
      localStorage.openBookPage = newPage
      // if (Number(this.$route.query.page) !== newPage) {
      //   this.$router.replace({ query: { page: newPage } })
      // }
    },
    settings: {
      handler: function (val, oldVal) {
        localStorage.setItem('readerSettings', JSON.stringify(this.settings))
      },
      deep: true
    }
  },
  methods: {
    // ライブラリに戻るときに
    goLibrary () {
      localStorage.removeItem('openBookUUID')
      localStorage.removeItem('openBookPage')
      router.push({ name: 'BooksList' })
    },
    // ページを進めるときに
    async getDLoadingPage () {
      const uuid = this.uuid
      const cachePage = this.settings.cachePage
      const mulchLoad = this.settings.mulchLoad
      let pageOffset = null

      for (let i = 0; i < cachePage; i++) {
        if (this.pageBlob[this.nowPage - 1 + i] == null) {
          pageOffset = i
          break
        }
      }

      const page = this.nowPage + pageOffset

      // 先読み限界
      if (pageOffset === null) {
        // console.log('先読み限界で終了')
        return
      }
      // ページ移動
      if (this.pageMove) {
        // console.log('ページ移動したので終了')
        return
      }
      // 指定ページが0以下 or ページ数より大きかったら終了
      if ((page <= 0) || (page > this.bookInfo.page)) {
        // console.log('ページ限界なので終了')
        return
      }
      // ロード中
      if (this.nowLoading >= mulchLoad) {
        // console.log('ロード中なので終了')
        return
      }

      this.nowLoading += 1
      this.pageBlob[page - 1] = LoadingImage

      // console.log(`${page}ページを読みます`)

      let height = this.settings.customHeight
      if (this.settings.showWindwSize) { height = this.settings.windowHeight }

      await axios
        .get(`/media/books/${uuid}/${page}`, {
          responseType: 'blob',
          params: {
            direct: 'True',
            height: height
          }
        })
        .then(response => {
          this.loadSizeB += Number(response.headers['content-length'])
          this.loadSizeMB = Math.round(this.loadSizeB / 10000) / 100
          this.pageBlob.splice(page - 1, 1, window.URL.createObjectURL(response.data))
          this.nowLoading -= 1
          this.getDLoadingPage()
        })
        .catch(error => {
          console.log(error)
          this.$_pushNotice('エラーが発生したので再試行します', 'error')
          this.pageBlob[page - 1] = null
          this.nowLoading -= 1
          setTimeout(this.getDLoadingPage, 1000)
        })
    },
    openSubMenu (event, item, i) {
      if (this.subMenu) {
        this.subMenu = false
      } else {
        this.subMenu = true
      }
      document.body.style.zoom = 1.0
    },
    pageNext () {
      if (this.settings.showTowPage) {
        this.nowPage += 2
      } else {
        this.nowPage += 1
      }
      if (this.bookInfo.page <= this.nowPage) {
        this.nowPage = this.bookInfo.page
        this.menuDialog = true
      }
    },
    pageBack () {
      if (this.settings.showTowPage) {
        this.nowPage -= 2
      } else {
        this.nowPage -= 1
      }
      if (this.nowPage <= 0) {
        this.nowPage = 1
      }
    },
    onSwipe (e) {
      const swipe = this.dict[e.direction]
      if (swipe === 'left') {
        this.pageBack()
      } else if (swipe === 'right') {
        this.pageNext()
      } else if (swipe === 'bottom') {
        this.menuDialog = true
      } else if (swipe === 'top') {
        this.goLibrary()
      }
    },
    openMenu () {
      this.menuDialog = true
    },
    getPageUrl (index) {
      const api = process.env.VUE_APP_API_HOST
      if (api) {
        return api + '/media/books/' + this.uuid + '/' + index
      } else {
        return '/media/books/' + this.uuid + '/' + index
      }
    },
    handleResize: function () {
      // resizeのたびにこいつが発火するので、ここでやりたいことをやる
      this.width = window.innerWidth
      this.height = window.innerHeight
    },
    onImgError: function (event) {
      console.log(event)
    },
    reCache () {
      axios.request({
        method: 'put',
        url: '/api/books',
        data: { uuids: [this.uuid], state: 'request' }
      })
    },
    parseBoolean (str) {
      return (str === 'true')
    },
    loadSettings () {
      // 設定の復元
      try {
        // 置き換えじゃなくてキーごとに上書き
        const getParam = JSON.parse(localStorage.getItem('readerSettings'))
        for (const key in getParam) { this.settings[key] = getParam[key] }
      } catch (e) {
        console.log(e)
        localStorage.removeItem('readerSettings')
        this.settings.showTowPage = !(this.$vuetify.breakpoint.md || this.$vuetify.breakpoint.sm)
        this.settings.showBaseWidth = !this.settings.showTowPage
      }
    },
    imageLoad (id) {
      const element = document.getElementById(id)
      const width = element.naturalWidth
      const height = element.naturalHeight
      const fitWidth = width * this.height / height * 2
      // console.log([width, height, this.width, this.height])
      if (id === 'viewer-page-1') {
        if (fitWidth > this.width) {
          this.viewerPage1TowPage = false
        } else {
          this.viewerPage1TowPage = true
        }
      } else {
        if (fitWidth > this.width) {
          this.viewerPage2TowPage = false
        } else {
          this.viewerPage2TowPage = true
        }
      }
      this.settings.showBaseWidth = (width < height)
      this.settings.showTowPage = this.viewerPage1TowPage & this.viewerPage2TowPage
    }
  },
  mounted: function () {
    // ウインドウ変更検出リスナー登録
    window.addEventListener('resize', this.handleResize)
    this.settings.showBaseWidth = (this.width < this.height)
    // 拡大率修正
    document.body.style.zoom = 1.0
    // パスからUUIDを取得して，ローカルストレージに保存
    this.uuid = this.$route.params.uuid
    localStorage.openBookUUID = this.uuid

    // ページの指定はあるか？
    if (this.$route.query.startPage) {
      this.nowPage = Number(this.$route.query.startPage)
    }

    // 4ページ決め打ちで先読み用アレイ
    this.pageBlob = Array(4)
    this.getDLoadingPage()

    // 書籍情報取得
    axios.get('/api/books', {
      params: { uuid: this.uuid }
    })
      .then((response) => {
        this.bookInfo = response.data.rows[0]
        // タイトル更新
        this.$emit('updateHead')
        Array.prototype.push.apply(this.pageBlob, Array(this.bookInfo.page - 4))
      })

    this.loadSettings()
  },
  beforeDestroy: function () {
    // 再帰処理を止めてる
    this.pageMove = true
    // ウインドウ変更検出リスナー解除
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped lang="scss">
.image-base-width > img {
  max-width: 100%;
  height: auto;
  width: auto;
}

.image-base-height > img {
  max-height: 100vh;
  height: 100vh;
}

.image-base-height{
  max-height: 100vh;
  height: 100vh;
}
</style>
