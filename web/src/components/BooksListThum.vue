<template>
  <v-row >
    <v-col
      :cols="4"
      :xs="4"
      :sm="3"
      :md="2"
      :lg="2"
      v-for="item in booksList"
      :key="item.uuid"
      :id="item.uuid"
      class="pt-5"
    >
      <v-card @click="$emit('toReaderPage', item)">
        <div fluid class="text-center" style="
          position: absolute;
          z-index: 1;
          top: -15px;
        ">
          <v-icon :color="getBadge(item)" small>mdi-circle</v-icon>
        </div>
        <v-img
          aspect-ratio="0.7"
          eager
          :src="getCoverURL(item.uuid)"
          v-hammer:press="(event) => $emit('openMenu',item)"
        ></v-img>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import store from '@/store'

export default {
  data: function () {
    return {
    }
  },
  computed: {
    booksList () {
      return store.getters.booksList
    },
    booksCount () {
      return store.getters.booksCount
    }
  },
  methods: {
    getCoverURL (uuid) {
      const api = process.env.VUE_APP_API_HOST
      if (api) {
        return process.env.VUE_APP_API_HOST + '/media/books/' + uuid
      } else {
        return '/media/books/' + uuid
      }
    },
    getBadge (item) {
      if (item.userData.openPage !== null) {
        return 'rgba(245,175,44,0.7)'
      } else if (item.userData.readTimes === null) {
        return 'rgba(81, 221, 30, 0.45)'
      } else {
        return 'gray'
      }
    }
  }
}
</script>
