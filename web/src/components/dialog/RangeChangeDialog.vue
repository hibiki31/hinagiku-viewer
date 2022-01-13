<template>
  <v-dialog v-model="dialogState" max-width="400">
    <v-card>
      <v-card-title>一括編集</v-card-title>
      <v-card-text>
        {{ uuids.length }}件の本を一括で編集
      </v-card-text>
      <v-card-text>
        <v-row>
          <v-checkbox v-model="changeLibrary"></v-checkbox>
          <v-select
            :items="libraryList"
            label="Library"
            v-model="queryLibrary"
            item-text="name"
            item-value="id"
            dense
            class="pr-2 pl-2 pt-3"
          ></v-select>
        </v-row>
        <v-row>
          <v-checkbox v-model="changeRate"></v-checkbox>
          <v-rating v-model="queryRate" small class="mt-4"></v-rating>
          <v-btn @click="queryRate = null" small class="mt-4">未評価</v-btn>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" text @click="dialogState = false">閉じる</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="error" text @click="submitDialog()">置き換え</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from '@/axios'
import store from '@/store'

export default {
  data: function () {
    return {
      dialogState: false,
      libraryList: [],
      queryLibrary: 0,
      queryRate: null,
      changeLibrary: false,
      changeRate: false
    }
  },
  computed: {
    uuids: () => store.getters.booksList.map((x) => x.uuid)
  },
  methods: {
    openDialog () {
      this.dialogState = true
      axios.get('/api/librarys').then((response) => (this.libraryList = response.data))
    },
    async submitDialog () {
      if (this.changeLibrary) {
        await axios.request({
          method: 'put',
          url: '/api/books',
          data: { uuids: this.uuids, libraryId: this.queryLibrary }
        })
          .then((response) =>
            this.$_pushNotice('ライブラリを一括変更しました', 'success')
          )
      }
      if (this.changeRate) {
        await axios.request({
          method: 'put',
          url: '/api/books/user-data',
          data: { uuids: this.uuids, rate: this.queryRate }
        }).then((response) => {
          this.$_pushNotice('評価を一括更新しました', 'success')
        })
      }
      this.$emit('search')
    }
  }
}
</script>
