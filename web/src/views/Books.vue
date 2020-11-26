<template>
  <div class="books">
    <v-row>
      <v-col lg=1 sm=2 v-for="item in booksList" :key="item.uuid">
        <v-card :to="{ name: 'BookReader', params: { uuid: item.uuid } }">
          <v-img
            aspect-ratio="0.7"
            :src="getCoverURL(item.uuid)"
          ></v-img>
          <v-card-title>
            {{ item.title }}
          </v-card-title>
          <v-card-text>
            <v-icon v-if="item.state=='cached'" color="primary">mdi-checkbox-marked-circle-outline</v-icon>
            <v-icon v-else >mdi-checkbox-marked-circle-outline</v-icon>
          </v-card-text>
        </v-card>
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
      booksList: []
    }
  },
  methods: {
    getCoverURL (uuid) {
      return process.env.VUE_APP_API_HOST + '/media/books/' + uuid
    }
  },
  mounted: async function () {
    axios.get('/api/books').then((response) => (this.booksList = response.data))
  }
}
</script>
