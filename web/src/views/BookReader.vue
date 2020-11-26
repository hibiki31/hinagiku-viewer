<template>
  <div class="books">
    <v-row>
      <v-col lg="1">
        <v-btn @click="index-=2">
          {{index-1}}
          前
        </v-btn>
      </v-col>
      <v-col lg="5">
        <v-img
        :height="this.height-100"
        :src="getPageUrl(this.index+1)"
        contain
        ></v-img>
      </v-col>
      <v-col lg="5"> 
          <v-img
          :height="this.height-100"
          :src="getPageUrl(this.index+0)"
          contain
          ></v-img>
      </v-col>
      <v-col lg="1">
        <v-btn @click="index+=2">
          次
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>

export default {
  name: 'Books',
  data: function () {
    return {
      uuid: '',
      index: 1,
      booksList: [],
      width: window.innerWidth,
      height: window.innerHeight
    }
  },
  methods: {
    getPageUrl (index) {
      return process.env.VUE_APP_API_HOST + '/media/books/' + this.uuid + '/?page=' + index
    },
    handleResize: function () {
      // resizeのたびにこいつが発火するので、ここでやりたいことをやる
      this.width = window.innerWidth
      this.height = window.innerHeight
    }
  },
  mounted: function () {
    window.addEventListener('resize', this.handleResize)
    this.uuid = this.$route.params.uuid
  },
  beforeDestroy: function () {
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>
