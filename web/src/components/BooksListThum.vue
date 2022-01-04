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
      >
        <v-card @click="$emit('toReaderPage', item)">
          <v-img
            aspect-ratio="0.7"
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
    }
  }
}
</script>
