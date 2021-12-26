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
          <v-btn @click="reCache()" class="ml-3">
            キャッシュ再生成
          </v-btn>
          <v-switch
              v-model="showTowPage"
              label="見開き表示"
              hide-details
          ></v-switch>
          <v-slider
            v-model="index"
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
      <!-- 先読みキャッシュ -->
      <v-col :cols="6" hidden>
        <v-img v-if="this.index > 2" :src="getPageUrl(this.index-2)" v-on:error="onImgError"></v-img>
        <v-img v-if="this.index > 1" :src="getPageUrl(this.index-1)" v-on:error="onImgError"></v-img>
        <v-img v-if="this.index + 0 <= this.bookInfo.page" :src="getPageUrl(this.index+0)" v-on:error="onImgError"></v-img>
        <v-img v-if="this.index + 1 <= this.bookInfo.page" :src="getPageUrl(this.index+1)" v-on:error="onImgError"></v-img>
        <v-img v-if="this.index + 2 <= this.bookInfo.page" :src="getPageUrl(this.index+2)" v-on:error="onImgError"></v-img>
        <v-img v-if="this.index + 3 <= this.bookInfo.page" :src="getPageUrl(this.index+3)" v-on:error="onImgError"></v-img>
        <v-img v-if="this.index + 4 <= this.bookInfo.page" :src="getPageUrl(this.index+4)" v-on:error="onImgError"></v-img>
        <v-img v-if="this.index + 5 <= this.bookInfo.page" :src="getPageUrl(this.index+5)" v-on:error="onImgError"></v-img>
      </v-col>
      <!-- メイン -->
      <div class="text-center">
        <template v-if="this.showTowPage" >
          <img
            v-hammer:swipe="onSwipe"
            v-hammer:press="openSubMenu"
            v-hammer:tap="pageNext"
            :height="this.height - this.heightOffcet"
            :src="getPageUrl(this.index+1)"
          />
          <!-- メイン -->
          <img
            v-hammer:tap="pageBack"
            v-hammer:swipe="onSwipe"
            v-hammer:press="openSubMenu"
            :height="this.height - this.heightOffcet"
            :src="getPageUrl(this.index+0)"
          />
        </template>
        <template v-else>
          <img
            :height="this.height - this.heightOffcet"
            :src="getPageUrl(this.index+0)"
            v-hammer:swipe="onSwipe"
            v-hammer:press="openSubMenu"
            v-hammer:tap="pageNext"
          />
        </template>
      </div>
      <div fluid class="text-center" style="position: fixed; bottom: 10px; z-index: 10; width: 100%" v-show="subMenu">
        <v-container>
          <v-btn
            class="white--text"
            color="teal"
            @click="subMenu=false"
          >
            閉じる
          </v-btn>
          <v-slider
            v-model="index"
            :min="1"
            :max="this.bookInfo.page"
            thumb-label
          ></v-slider>
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
      subMenu: false,
      heightOffcet: 0,
      showTowPage: true,
      uuid: '',
      index: 1,
      booksList: [],
      width: window.innerWidth,
      height: window.innerHeight,
      bookInfo: {},
      pageBlob: []
    }
  },
  methods: {
    getImageBlob () {
      axios.get(this.getPageUrl(this.index + 0)).then((response) => (
        this.bookInfo = response.data[0]
      ))
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
        this.index += 2
      } else {
        this.index += 1
      }
      if (this.bookInfo.page <= this.index) {
        this.index = this.bookInfo.page
        this.menuDialog = true
      }
    },
    pageBack () {
      if (this.showTowPage) {
        this.index -= 2
      } else {
        this.index -= 1
      }
      if (this.index <= 0) {
        this.index = 1
      }
    },
    onSwipe (e) {
      const swipe = this.dict[e.direction]
      if (swipe === 'left') {
        this.pageBack()
      } else if (swipe === 'right') {
        this.pageNext()
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
    this.showTowPage = !this.$vuetify.breakpoint.mobile
    axios.get('/api/books', { params: { uuid: this.uuid } }).then((response) => (this.bookInfo = response.data[0]))
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy: function () {
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped lang="scss">
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
