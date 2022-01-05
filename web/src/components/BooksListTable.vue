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
    <v-data-table
          :headers="headers"
          :items="booksList"
          :items-per-page="searchQuery.limit"
          hide-default-footer
          dense
        >
        <template v-slot:[`item.title`]="props">
          <v-edit-dialog
            :return-value.sync="props.item.title"
            @save="saveTitle(props.item)"
            @cancel="cancel"
            @open="open"
            @close="close"
          >
            {{ props.item.title }}
            <template v-slot:input>
              <v-text-field
                v-model="props.item.title"
                label="Edit"
                single-line
                counter
              ></v-text-field>
            </template>
          </v-edit-dialog>
        </template>
        <template v-slot:[`item.publisher`]="props">
          <v-edit-dialog
            :return-value.sync="props.item.publisher.name"
            @save="savePublisher(props.item)"
            @cancel="cancel"
            @open="open"
            @close="close"
          >
            {{ props.item.publisher.name }}
            <template v-slot:input>
              <v-text-field
                v-model="props.item.publisher.name"
                label="Edit"
                single-line
                counter
              ></v-text-field>
            </template>
          </v-edit-dialog>
        </template>
         <template v-slot:[`item.actions`]="{ item }">
          <v-icon
            small
            class="mr-2"
            @click="$emit('toReaderPage', item)"
          >
            mdi-book-open-blank-variant
          </v-icon>
          <v-icon
            small
            class="mr-2"
            @click="$emit('openMenu',item)"
          >
            mdi-tooltip-edit-outline
          </v-icon>
        </template>
         <template v-slot:[`item.authors`]="{ item }">
          <v-chip
            v-for="author in item.authors"
            :key="author.id"
            class="mt-2 mb-2 mr-2"
            small
            close
            @click="searchAuthor(author.name)"
            @click:close="deleteAuthor(item, author.id)"
          >
            {{ author.name }}
          </v-chip>
          <v-icon
            small
            @click="openPostDialog(item)"
          >mdi-plus-circle</v-icon>
        </template>
    </v-data-table>
  </div>
</template>

<script>
import store from '@/store'
import axios from '@/axios/index'

export default {
  data: function () {
    return {
      topBerQuery: null,
      postDialogState: false,
      postAuthorName: '',
      oepnBook: null,
      headers: [
        { text: 'title', value: 'title' },
        { text: 'authors', value: 'authors' },
        { text: 'publisher', value: 'publisher.name' },
        { text: 'actions', value: 'actions' }
      ]
    }
  },
  computed: {
    searchQuery: () => store.getters.searchQuery,
    booksList: () => store.getters.booksList,
    booksCount: () => store.getters.booksCount
  },
  methods: {
    openPostDialog (book) {
      this.oepnBook = book
      this.postDialogState = true
    },
    searchAuthor (authorName) {
      const query = store.getters.searchQuery
      query.fullText = authorName
      this.$store.dispatch('setSearchQuery', this.searchQuery)
      this.$emit('search')
    },
    postAuthor () {
      axios
        .request({
          method: 'post',
          url: `/api/books/${this.oepnBook.uuid}/authors`,
          data: { authorName: this.postAuthorName }
        })
        .then((response) => {
          this.$_pushNotice('著者追加成功', 'success')
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
          store.dispatch('serachBooks')
        }).catch(error => {
          this.$_apiErrorHandler(error)
        })
    },
    saveTitle (book) {
      axios
        .request({
          method: 'put',
          url: '/api/books',
          data: { uuids: [book.uuid], title: book.title }
        })
        .then((response) =>
          this.$_pushNotice('タイトル更新', 'success')
        )
    },
    savePublisher (book) {
      axios
        .request({
          method: 'put',
          url: '/api/books',
          data: { uuids: [book.uuid], publisher: book.publisher.name }
        })
        .then((response) =>
          this.$_pushNotice('発行者更新', 'success')
        )
    },
    cancel () {
    },
    open () {
    },
    close () {
    }
  }
}
</script>
