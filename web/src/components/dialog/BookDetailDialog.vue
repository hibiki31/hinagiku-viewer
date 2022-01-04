<template>
  <v-dialog v-model="dialogState">
    <v-card>
      <v-card-title>Select Editor</v-card-title>
      <v-divider></v-divider>
      <v-card-text style="height: 300px">
        <v-rating v-model="openItem.userData.rate" small class="pa-1"></v-rating>
        <v-row>
          <v-text-field label="Title" v-model="openItem.title"></v-text-field>
          <v-btn small icon><v-icon>mdi-magnify</v-icon></v-btn>
        </v-row>
        <v-row>
          <div>Author</div>
        </v-row>
        <v-row v-for="author in openItem.authors" :key="author.name">
          <v-text-field
            v-model="author.name"
          ></v-text-field>
          <v-btn @click="searchQuery.fullText=author.name; search()" small icon><v-icon>mdi-magnify</v-icon></v-btn>
        </v-row>
        <v-btn small class="pa-1" @click="showJson = !showJson">Json</v-btn>
        <div v-if="showJson" class="selectable">{{ this.openItem }}</div>
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

export default {
  data: function () {
    return {
      dialogState: false,
      searchQuery: {},
      topBerQuery: null,
      // ダイアログで使用
      showJson: false,
      openItem: {
        userData: {
          rate: null
        }
      }
    }
  },
  methods: {
    openDialog (book) {
      this.openItem = book
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
            uuids: [this.openItem.uuid],
            rate: this.openItem.userData.rate
          }
        })
        .then((response) =>
          this.$_pushNotice('評価を更新しました', 'success')
        )
    }
  }
}
</script>
