<template>
  <v-dialog v-model="dialogState">
    <v-card>
      <v-card-title>一括編集</v-card-title>
      <v-card-text>
        {{ booksCount }}
      </v-card-text>
      <v-card-actions>
          <v-btn color="error" text @click="dialogState = false">閉じる</v-btn>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="getAll()">検索</v-btn>
          <!-- <v-btn color="primary" text @click="submitDialog()">検索</v-btn> -->
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from '@/axios'

export default {
  data: function () {
    return {
      dialogState: false,
      searchQuery: {},
      topBerQuery: null,
      allBooks: []
    }
  },
  methods: {
    openDialog () {
      this.dialogState = true
      this.booksCount = this.$store.getters.booksCount
    },
    async getAll () {
      const query = this.$store.getters.searchQuery

      await axios.get('/api/books', {
        params: query
      }).then((response) => {
        this.allBooks = response.data
      })
    },
    async submitDialog () {
    }
  }
}
</script>
