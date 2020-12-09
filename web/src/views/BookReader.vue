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
      showTowPage: true,
      uuid: '',
      nowPage: 1,
      booksList: [],
      width: window.innerWidth,
      height: window.innerHeight,
      bookInfo: {},
      pageBlob: []
    }
  },
  watch: {
    nowPage: function (newPage, oldIndex) {
      this.getDLoadingPage(newPage + 0)
      this.getDLoadingPage(newPage + 1)
      this.getDLoadingPage(newPage + 2)
      this.getDLoadingPage(newPage + 3)
      this.getDLoadingPage(newPage + 4)
      this.getDLoadingPage(newPage + 5)
      this.getDLoadingPage(newPage - 2)
      this.getDLoadingPage(newPage - 1)
      localStorage.page = newPage
    }
  },
  methods: {
    goLibrary () {
      localStorage.removeItem('uuid')
      localStorage.removeItem('page')
      router.push({ name: 'Books' })
    },
    getDLoadingPage (page) {
      // 指定ページが0以下 or ページ数より大きかったら終了
      if ((page <= 0) || (page > this.bookInfo.page)) {
        return
      }
      if (typeof this.pageBlob[page - 1] === 'undefined') {
        this.pageBlob[page - 1] = LoadingImage
        this.getImageBlob(this.uuid, page)
      }
    },
    getImageBlob (uuid, page) {
      axios
        .get('/media/books/' + uuid + '/' + page, {
          responseType: 'blob'
        })
        .then(response => {
          this.pageBlob.splice(page - 1, 1, window.URL.createObjectURL(response.data))
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
    }
  },
  mounted: function () {
    this.uuid = this.$route.params.uuid
    localStorage.uuid = this.uuid

    if (this.$route.query.page) {
      this.nowPage = Number(this.$route.query.page)
    }

    this.pageBlob = Array(4)
    this.getImageBlob(this.uuid, 1, 0)

    axios.get('/api/books', {
      params: { uuid: this.uuid }
    })
      .then((response) => {
        this.bookInfo = response.data[0]
        Array.prototype.push.apply(this.pageBlob, Array(this.bookInfo.page - 4))
      })

    this.showTowPage = !this.$vuetify.breakpoint.md && !this.$vuetify.breakpoint.sm && !this.$vuetify.breakpoint.mobile
    this.baseWidth = !this.showTowPage

    this.$store.dispatch('hideMenuBer')
    window.addEventListener('resize', this.handleResize)

    this.getDLoadingPage(this.nowPage + 0)
    this.getDLoadingPage(this.nowPage + 1)
    this.getDLoadingPage(this.nowPage + 2)
    this.getDLoadingPage(this.nowPage + 3)
  },
  beforeDestroy: function () {
    this.$store.dispatch('showMenuBer')
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
