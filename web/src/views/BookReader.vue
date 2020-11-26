<template>
  <div class="books">
    <v-row>
      <v-col>
        <v-btn @click="index-=1">
          {{index-1}}
          前
        </v-btn>
      </v-col>
      <v-col>
        <v-img
        :height="this.height-100"
        :src="getPageUrl()"
        contain
      ></v-img>
      </v-col>
       <v-col>
        <v-btn @click="index+=1">
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
    getPageUrl () {
      return process.env.VUE_APP_API_HOST + '/media/books/' + this.uuid + '/?page=' + this.index
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
