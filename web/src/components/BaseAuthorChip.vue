<template>
  <div>
    <v-dialog width="400" v-model="postDialogState">
      <v-card>
        <v-card-title>著者追加</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="postAuthorName"
            :rules="[$_required, $_limitLength64]"
            counter="64"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" v-on:click="postAuthor">追加</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-chip
      v-for="author in openBook.authors"
      :key="author.id"
      class="mt-2 mb-2 mr-2"
      small
      close
      @click="searchAuthor(author.name)"
      @click:close="deleteAuthor(openBook, author.id)"
    >
      {{ author.name }}
    </v-chip>
    <v-icon
      small
      @click="openPostDialog(openBook)"
    >mdi-plus-circle</v-icon>
  </div>
</template>

<script>
import store from '@/store'
import axios from '@/axios/index'

export default {
  data: function () {
    return {
      postDialogState: false,
      postAuthorName: ''
    }
  },
  props: {
    openBook: {}
  },
  computed: {
  },
  methods: {
    openPostDialog () {
      this.postDialogState = true
    },
    searchAuthor (authorName) {
      const query = store.getters.searchQuery
      query.fullText = authorName
      store.dispatch('setSearchQuery', query)
      this.$emit('search')
    },
    postAuthor () {
      axios
        .request({
          method: 'post',
          url: `/api/books/${this.openBook.uuid}/authors`,
          data: { authorName: this.postAuthorName }
        })
        .then((response) => {
          this.$_pushNotice('著者追加成功', 'success')
          store.dispatch('setOpenBook', response.data)
          store.dispatch('serachBooks')
        }).catch(error => {
          this.$_apiErrorHandler(error)
        })
      this.postDialogState = false
    },
    deleteAuthor (book, id) {
      axios
        .request({
          method: 'delete',
          url: `/api/books/${book.uuid}/authors`,
          data: { authorId: id }
        })
        .then((response) => {
          this.$_pushNotice('著者削除', 'success')
          store.dispatch('setOpenBook', response.data)
          store.dispatch('serachBooks')
        }).catch(error => {
          this.$_apiErrorHandler(error)
        })
    }
  }
}
</script>
