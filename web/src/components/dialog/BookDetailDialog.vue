<template>
  <v-dialog v-model="dialogState" max-width=700>
    <v-card>
      <v-card-text>
        <v-row class="pt-8">
          <p class="font-weight-bold">{{ openBook.title }}</p>
        </v-row>
        <v-row>
          <p class="font-weight-black">サイズ:</p><p>{{ $_fitByte(openBook.size) }}</p>
        </v-row>
        <v-row>
          <p class="font-weight-black">ページ:</p><p>{{ openBook.page }}</p>
        </v-row>
        <v-row>
          <v-select
            :items="libraryList"
            label="Library"
            v-model="openBook.libraryId"
            item-text="name"
            item-value="id"
            @change="changeBookLibrary"
            dense
            class=""
          ></v-select>
          <v-rating v-model="openBook.userData.rate" @input="bookInfoSubmit" small class="pa-1"></v-rating>
        </v-row>
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
      libraryList: []
    }
  },
  methods: {
    openDialog (book) {
      this.$store.dispatch('setOpenBook', book)
      this.dialogState = true
      this.searchQuery = this.$store.getters.searchQuery
      axios.get('/api/librarys').then((response) => (this.libraryList = response.data))
    },
    bookInfoSubmit () {
      axios.request({
        method: 'put',
        url: '/api/books/user-data',
        data: {
          uuids: [this.openBook.uuid],
          rate: this.openBook.userData.rate
        }
      }).then((response) => {
        this.$_pushNotice('評価を更新しました', 'success')
        this.$emit('search')
      })
    },
    changeBookLibrary () {
      axios.request({
        method: 'put',
        url: '/api/books',
        data: { uuids: [this.openBook.uuid], libraryId: this.openBook.libraryId }
      })
        .then((response) => {
          this.$_pushNotice('ライブラリを変更しました', 'success')
          this.$emit('search')
        })
    }
  }
}
</script>
