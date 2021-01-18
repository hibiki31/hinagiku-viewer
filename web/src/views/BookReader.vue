<template>
  <div class="books">
    <!-- ダイアログ -->
    <v-dialog v-model="menuDialog" scrollable max-width="500px">
      <v-card>
        <v-card-text class="pt-6">
          <v-btn @click="nowPage += 1"> ページ調整 </v-btn>
          <v-btn @click="goLibrary()" class="ml-3">ライブラリへ戻る</v-btn>
          <v-btn @click="reCache()" class="ml-3">キャッシュ再生成</v-btn>
          <v-switch
            v-model="showTowPage"
            label="見開き表示"
            hide-details
          ></v-switch>
          <v-slider
            v-model="nowPage"
            label="ページ"
            :min="0"
            :max="this.bookInfo.page"
            thumb-label
          ></v-slider>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text style="height: 300px">
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
      v-bind:class="{ 'image-base-width': baseWidth, 'image-base-height': !baseWidth }"
      class="text-center"
    >
      <!-- 見開き表示 -->
      <template v-if="this.showTowPage" >
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
    </div>
    <!-- 下部メニュ -->
    <div fluid class="text-center" style="position: fixed; bottom: 5px; z-index: 10; width: 100%" v-show="subMenu">
      <v-container>
        <v-switch
          v-model="showTowPage"
          label="見開き表示"
          hide-details
        ></v-switch>
        <v-switch
          v-model="baseWidth"
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
        <v-btn icon @click="goLibrary()" class="ml-3">
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
  data: function () {
    return {
      dict: {
        2: 'left',
        4: 'right',
        8: 'top',
        16: 'bottom'
      },
      menuDialog: false,
      baseWidth: false,
      subMenu: false,
      heightOffcet: 0,
      showTowPage: false,
      uuid: '',
      nowPage: 1,
      loadCounter: 0,
      nowLoading: false,
      booksList: [],
      width: window.innerWidth,
      height: window.innerHeight,
      bookInfo: {},
      pageBlob: []
    }
  },
  watch: {
    nowPage: function (newPage, oldPage) {
      this.getDLoadingPage()
      localStorage.page = newPage
    },
    showTowPage: function (newValue, oldValue) {
      localStorage.showTowPage = newValue
    }
  },
  methods: {
    // ライブラリに戻るときに
    goLibrary () {
      localStorage.removeItem('uuid')
      localStorage.removeItem('page')
      router.push({ name: 'BooksList' })
    },
    // ページを進めるときに
    async getDLoadingPage () {
      const uuid = this.uuid

      // ロード中
      if (this.nowLoading) {
        this.loadCounter = 0
        console.log('ロード中なので終了')
        return
      }

      // まず現在のファイルを確認
      if (typeof this.pageBlob[this.nowPage - 1] === 'undefined') {
        this.pageBlob[this.nowPage - 1] = LoadingImage
        console.log(`現在のページ${this.nowPage}が読み込まれて無いのでカウンタを0に`)
        this.loadCounter = 0
      }

      // 移動時に99999とかにして再帰処理を止めてる
      if (this.loadCounter > 5) {
        this.loadCounter = 0
        console.log('先読み上限にきたので終了')
        return
      }

      const page = this.nowPage + this.loadCounter

      // 指定ページが0以下 or ページ数より大きかったら終了
      if ((page <= 0) || (page > this.bookInfo.page)) {
        console.log('ページ限界なので終了')
        return
      }

      this.nowLoading = true

      if (typeof this.pageBlob[page - 1] !== 'undefined') {
        this.loadCounter += 1
        this.nowLoading = false
        this.getDLoadingPage()
        return
      }

      console.log(`${page}を読みます ${this.nowPage}+${this.loadCounter}`)

      await axios
        .get(`/media/books/${uuid}/${page}`, {
          responseType: 'blob',
          params: { direct: 'True' }
        })
        .then(response => {
          this.pageBlob.splice(page - 1, 1, window.URL.createObjectURL(response.data))
          this.loadCounter += 1
          this.nowLoading = false
          this.getDLoadingPage()
        })
        .catch(error => {
          console.log(error)
          this.$_pushNotice('ページが見つかりませんでした', 'error')
          this.menuDialog = true
        })
    },
    // ページ取得
    getImageBlob (uuid, page) {
      axios
        .get(`/media/books/${uuid}/${page}`, {
          responseType: 'blob',
          params: { direct: 'True' }
        })
        .then(response => {
          this.pageBlob.splice(page - 1, 1, window.URL.createObjectURL(response.data))
        })
        .catch(error => {
          console.log(error)
          this.$_pushNotice('ページが見つかりませんでした', 'error')
          this.menuDialog = true
        })
    },
    openSubMenu () {
      if (this.subMenu) {
        this.subMenu = false
      } else {
        this.subMenu = true
      }
    },
    pageNext () {
      if (this.showTowPage) {
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
      if (this.showTowPage) {
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
      } else if (swipe === 'up') {
        alert('aaa')
        this.menuDialog = true
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
    }
  },
  mounted: function () {
    // パスからUUIDを取得
    this.uuid = this.$route.params.uuid
    // ローカルストレージに保存
    localStorage.uuid = this.openBookUUID

    // ページの指定はあるか？
    if (this.$route.query.page) {
      this.nowPage = Number(this.$route.query.page)
    }

    // 4ページ決め打ちで先読み用アレイ
    this.pageBlob = Array(4)
    this.getDLoadingPage(this.nowPage + 0)
    this.getDLoadingPage(this.nowPage + 1)
    this.getDLoadingPage(this.nowPage + 2)
    this.getDLoadingPage(this.nowPage + 3)

    // 書籍情報取得
    axios.get('/api/books', {
      params: { uuid: this.uuid }
    })
      .then((response) => {
        this.bookInfo = response.data.rows[0]
        Array.prototype.push.apply(this.pageBlob, Array(this.bookInfo.page - 4))
      })

    // 表示設定を取得
    const showTowPage = localStorage.showTowPage

    // なかったら縦横比で設定
    if (showTowPage !== null) {
      this.showTowPage = this.parseBoolean(showTowPage)
    } else {
      this.showTowPage = !(this.$vuetify.breakpoint.md || this.$vuetify.breakpoint.sm)
      localStorage.setItem('showTowPage', this.showTowPage)
    }
    // 見開き表示設定から縦横のベースを決定
    this.baseWidth = !this.showTowPage

    // メニューを非表示
    this.$store.dispatch('hideMenuBer')
    // ウインドウ変更検出リスナー登録
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy: function () {
    // 再帰処理を止めてる
    this.loadCounter = 99999
    // メニューを表示
    this.$store.dispatch('showMenuBer')
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
  height: auto;
  width: auto;
}
</style>
