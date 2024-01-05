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

    <v-menu
      v-for="author in openBook.authors"
      :key="author.id"
    >
      <template v-slot:activator="{ on: menu, attrs }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on: tooltip }">
            <v-chip
              class="mt-2 mb-2 mr-2"
              small
              :color="getAuthorColo(author.isFavorite)"
              close
              v-bind="attrs"
              v-on="{ ...tooltip, ...menu }"
              @click:close="deleteAuthor(openBook, author.id)"
            >
              {{ author.name }}
            </v-chip>
          </template>
          <span>Open Menu</span>
        </v-tooltip>
      </template>
      <v-card>
        <v-card-text>
          <div class="ma-3" @click="searchAuthor(author.name)">
            <v-icon color="primary"
              >mdi-magnify</v-icon
            >この著者で検索する
          </div>
          <div class="ma-3" @click="favoriteAuthor(author, true)" v-if="author.isFavorite===false">
            <v-icon color="primary"
              >mdi-star</v-icon
            >この著者をお気に入りにする
          </div>
          <div class="ma-3" @click="favoriteAuthor(author, false)" v-if="author.isFavorite===true">
            <v-icon color=""
              >mdi-star</v-icon
            >この著者をお気に入りから外す
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
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
    getAuthorColo (isFavorite) {
      if (isFavorite) {
        return 'orange'
      } else {
        return ''
      }
    },
    favoriteAuthor (author, favorite) {
      axios
        .request({
          method: 'patch',
          url: '/api/authors',
          data: { authorId: author.id, isFavorite: favorite }
        })
        .then((response) => {
          this.$_pushNotice('著者のお気に入り変更', 'success')
          author.isFavorite = favorite
        }).catch(error => {
          this.$_apiErrorHandler(error)
        })
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
