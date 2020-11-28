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
    <v-row justify="center" v-hammer:press="openMenu" v-hammer:swipe="onSwipe">
      <!-- 先読みキャッシュ -->
      <v-col lg="6" hidden>
        <v-img :src="getPageUrl(this.index+0)" v-on:error="onImgError"></v-img>
        <v-img :src="getPageUrl(this.index+1)" v-on:error="onImgError"></v-img>
        <v-img :src="getPageUrl(this.index+2)" v-on:error="onImgError"></v-img>
        <v-img :src="getPageUrl(this.index+3)" v-on:error="onImgError"></v-img>
        <v-img :src="getPageUrl(this.index+4)" v-on:error="onImgError"></v-img>
        <v-img :src="getPageUrl(this.index+5)" v-on:error="onImgError"></v-img>
        <v-img :src="getPageUrl(this.index+6)" v-on:error="onImgError"></v-img>
        <v-img :src="getPageUrl(this.index+7)" v-on:error="onImgError"></v-img>
      </v-col>
      <!-- メイン -->
      <v-col lg="6" @click="index+=2" v-if="$vuetify.breakpoint.lg">
        <v-img
        :height="this.height - this.heightOffcet"
        :src="getPageUrl(this.index+1)"
        contain
        ></v-img>
      </v-col>
      <!-- メイン -->
      <v-col lg="6" @click="index-=2" v-if="$vuetify.breakpoint.lg">
          <v-img
          :height="this.height - this.heightOffcet"
          :src="getPageUrl(this.index+0)"
          contain
          ></v-img>
      </v-col>
      <!-- スマホ用 -->
      <v-col lg="6" @click="index+=1" v-if="$vuetify.breakpoint.mobile">
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
      uuid: '',
      index: 1,
      booksList: [],
      width: window.innerWidth,
      height: window.innerHeight
    }
  },
  methods: {
    onSwipe (e) {
      const swipe = this.dict[e.direction]
      if (swipe === 'left') {
        this.index -= 1
      } else if (swipe === 'right') {
        this.index += 1
      }
    },
    openMenu () {
      this.menuDialog = true
    },
    getPageUrl (index) {
      return process.env.VUE_APP_API_HOST + '/media/books/' + this.uuid + '?page=' + index
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
    this.$store.dispatch('hideMenuBer')
    window.addEventListener('resize', this.handleResize)
    this.uuid = this.$route.params.uuid
  },
  beforeDestroy: function () {
    this.$store.dispatch('showMenuBer')
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>
