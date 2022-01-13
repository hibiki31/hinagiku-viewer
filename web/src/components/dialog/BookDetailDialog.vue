<template>
  <v-dialog v-model="dialogState" max-width=700>
    <v-card>
      <v-card-text>
        <v-row class="pt-8">
          <v-text-field label="Title" v-model="openBook.title"></v-text-field>
        </v-row>
        <p>サイズ {{ $_fitByte(openBook.size) }}</p>
        <p>ページ {{ openBook.page }}</p>
        <v-rating v-model="openBook.userData.rate" @input="bookInfoSubmit" small class="pa-1"></v-rating>
        <v-row>
          <BaseAuthorChip :openBook="openBook" @search="$emit('search')" />
        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-btn color="blue darken-1" text @click="dialogState = false">
          閉じる
        </v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from '@/axios/index'
import store from '@/store'

import BaseAuthorChip from '../BaseAuthorChip'

export default {
  components: {
    BaseAuthorChip
  },
  computed: {
    openBook: () => store.getters.openBook
  },
  data: function () {
    return {
      dialogState: false,
      searchQuery: {},
      topBerQuery: null
    }
  },
  methods: {
    openDialog (book) {
      this.$store.dispatch('setOpenBook', book)
      this.dialogState = true
      this.searchQuery = this.$store.getters.searchQuery
    },
    async submitDialog () {
      await this.$store.dispatch('serachBooks', this.searchQuery)
    },
    bookInfoSubmit () {
      axios.request({
        method: 'put',
        url: '/api/books/user-data',
        data: {
          uuids: [this.openBook.uuid],
          rate: this.openBook.userData.rate
        }
      }).then((response) =>
        this.$_pushNotice('評価を更新しました', 'success')
      )
    }
  }
}
</script>
