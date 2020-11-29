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
    <v-row justify="center" v-hammer:press="openMenu" v-hammer:swipe="onSwipe">
      <!-- 先読みキャッシュ -->
      <v-col lg="6" hidden>
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
      <v-col lg="6" @click="pageNext()" v-if="this.showTowPage">
        <v-img
        :height="this.height - this.heightOffcet"
        :src="getPageUrl(this.index+1)"
        contain
        ></v-img>
      </v-col>
      <!-- メイン -->
      <v-col lg="6" @click="pageBack()" v-if="this.showTowPage">
          <v-img
          :height="this.height - this.heightOffcet"
          :src="getPageUrl(this.index+0)"
          contain
          ></v-img>
      </v-col>
      <!-- スマホ用 -->
      <v-col lg="6" @click="pageNext()" v-if="!this.showTowPage">
          <v-img
          :height="this.height - this.heightOffcet"
          :src="getPageUrl(this.index+0)"
          contain
          ></v-img>
      </v-col>
    </v-row>
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
      heightOffcet: 50,
      showTowPage: true,
      uuid: '',
      index: 1,
      booksList: [],
      width: window.innerWidth,
      height: window.innerHeight,
      bookInfo: {}
    }
  },
  methods: {
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
    }
  },
  mounted: function () {
    this.uuid = this.$route.params.uuid
    this.showTowPage = !this.$vuetify.breakpoint.mobile
    this.$store.dispatch('hideMenuBer')
    axios.get('/api/books', { params: { uuid: this.uuid } }).then((response) => (this.bookInfo = response.data[0]))
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy: function () {
    this.$store.dispatch('showMenuBer')
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>
