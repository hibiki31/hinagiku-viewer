<template>
  <v-dialog v-model="dialogState">
    <v-card>
      <v-card-title>詳細</v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <!-- <v-rating v-model="openBook.userData.rate" small class="pa-1"></v-rating> -->
        <v-row>
          <v-text-field label="Title" v-model="openBook.title"></v-text-field>
          <v-btn small icon><v-icon>mdi-magnify</v-icon></v-btn>
        </v-row>
        <v-row>
          <BaseAuthorChip :openBook="openBook" @search="$emit('search')" />
        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-btn color="blue darken-1" text @click="menuDialog = false">
          閉じる
        </v-btn>
        <v-btn color="blue darken-1" text @click="bookInfoSubmit">保存</v-btn>
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
      this.dialogState = false
      axios
        .request({
          method: 'put',
          url: '/api/books/user-data',
          data: {
            uuids: [this.openBook.uuid],
            rate: this.openBook.userData.rate
          }
        })
        .then((response) =>
          this.$_pushNotice('評価を更新しました', 'success')
        )
    }
  }
}
</script>
