<template>
  <div class="books">
    <v-dialog
      v-model="menuDialog"
      scrollable
      max-width="500px"
    >
      <v-card>
        <v-card-text class="pt-6">
          <v-btn @click="nowPage+=1">
            ページ調整
          </v-btn>
          <v-btn :to="{ name: 'Books'}" class="ml-3">
            戻る
          </v-btn>
          <v-btn @click="reCache()" class="ml-3">
            キャッシュ再生成
          </v-btn>
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
        <v-card-text style="height: 300px;">
          {{bookInfo}}
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
    <!-- 画像表示ぶ-->
    <div class="text-center" v-if="reShowFlag">
      <!-- 見開き表示 -->
      <template v-if="this.showTowPage" >
        <img
          v-hammer:swipe="onSwipe"
          v-hammer:press="openSubMenu"
          v-hammer:tap="pageNext"
          :height="this.height - this.heightOffcet"
          :src="this.pageBlob[this.nowPage+0]"
        />
        <img
          v-hammer:swipe="onSwipe"
          v-hammer:press="openSubMenu"
          v-hammer:tap="pageNext"
          :height="this.height - this.heightOffcet"
          :src="this.pageBlob[this.nowPage-1]"
        />
      </template>
      <!-- スマホ用片面 -->
      <template v-else>
        <img
          v-hammer:swipe="onSwipe"
          v-hammer:press="openSubMenu"
          v-hammer:tap="pageNext"
          :height="this.height - this.heightOffcet"
          :src="this.pageBlob[this.nowPage-1]"
        />
      </template>
    </div>
    <!-- 下部メニュ -->
    <div fluid class="text-center" style="position: fixed; bottom: 10px; z-index: 10; width: 100%" v-show="subMenu">
      <v-container>
        <v-switch
          v-model="showTowPage"
          label="見開き表示"
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
        <v-btn @click="nowPage+=1">
          ページ調整
        </v-btn>
        <v-btn :to="{ name: 'Books'}" class="ml-3">
          閉じる
        </v-btn>
        <v-btn @click="reCache()" class="ml-3">
          キャッシュ再生成
        </v-btn>
      </v-container>
    </div>

  </div>
</template>

<script>
import axios from '@/axios/index'

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
      reShowFlag: true,
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
    }
  },
  methods: {
    getDLoadingPage (page) {
      if (typeof this.pageBlob[page - 1] === 'undefined') {
        this.pageBlob[page - 1] = 'https://i.imgur.com/WAsKmUy.gif'
        this.getImageBlob(this.uuid, page)
      }
    },
    getImageBlob (uuid, page) {
      axios
        .get('/media/books/' + uuid + '/' + page, {
          responseType: 'blob'
        })
        .then(response => {
          console.log(page + 'ページの取得完了')
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

    this.pageBlob = Array(4)
    this.getImageBlob(this.uuid, 1, 0)

    axios.get('/api/books', {
      params: { uuid: this.uuid }
    })
      .then((response) => {
        this.bookInfo = response.data[0]
        Array.prototype.push.apply(this.pageBlob, Array(this.bookInfo.page - 4))
      })

    this.showTowPage = !this.$vuetify.breakpoint.mobile
    this.$store.dispatch('hideMenuBer')
    window.addEventListener('resize', this.handleResize)

    this.getImageBlob(this.uuid, 1, 0)
    this.getImageBlob(this.uuid, 2, 1)
    this.getImageBlob(this.uuid, 3, 2)
    this.getImageBlob(this.uuid, 4, 3)
  },
  beforeDestroy: function () {
    this.$store.dispatch('showMenuBer')
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped lang="scss">
.body {
  buser-select: none;
}
#contextmenu{
  display:none;
  position:fixed;
  left:0px;
  top:0px;
  width:100px;
  height:100px;
}
#contextmenu li{
  cursor:pointer;
}
</style>
