<template>
  <div>
    <v-data-table
      :headers="headers"
      :items="booksList"
      :items-per-page="searchQuery.limit"
      :custom-sort="updateSortQuery"
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
          <v-tooltip left nudge-right=100>
            <template v-slot:activator="{ on, attrs }">
              <div
                v-bind="attrs"
                v-on="on"
              >
                {{ props.item.title }}
              </div>
            </template>
            <v-img
              aspect-ratio="0.7"
              eager
              width="150"
              :src="$_getCoverURL(props.item.uuid)"
            ></v-img>
            <span></span>
          </v-tooltip>
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
        <BaseAuthorChip :openBook="item" @search="$emit('search')" />
      </template>
      <template v-slot:[`item.size`]="{ item }">
        {{ $_fitByte(item.size) }}
      </template>
      <template v-slot:[`item.addDate`]="{ item }">
        {{ $_convertDateFormat(item.addDate) }}
      </template>
    </v-data-table>
  </div>
</template>

<script>
import store from '@/store'
import axios from '@/axios/index'
import BaseAuthorChip from './BaseAuthorChip'

export default {
  data: function () {
    return {
      topBerQuery: null,
      oepnBook: null,
      sortedBy: null,
      sortedDesc: false,
      headers: [
        { text: 'title', value: 'title' },
        { text: 'authors', value: 'authors' },
        { text: 'publisher', value: 'publisher.name' },
        { text: 'rate', value: 'userData.rate' },
        { text: 'addDate', value: 'addDate', width: '110' },
        { text: 'last', value: 'userData.lastOpenDate', width: '110' },
        { text: 'size', value: 'size', width: '60' },
        { text: 'page', value: 'page', width: '20' },
        { text: 'actions', value: 'actions' }
      ]
    }
  },
  components: {
    BaseAuthorChip
  },
  computed: {
    searchQuery: () => store.getters.searchQuery,
    booksList: () => store.getters.booksList,
    booksCount: () => store.getters.booksCount
  },
  methods: {
    searchAuthor (authorName) {
      const query = store.getters.searchQuery
      query.fullText = authorName
      this.$store.dispatch('setSearchQuery', this.searchQuery)
      this.$emit('search')
    },
    updateSortQuery (items, sortBy, sortDesc) {
      if (sortBy.length === 0) {
        return items
      }
      if (sortBy[0] !== this.sortedBy || sortDesc[0] !== this.sortedDesc) {
        this.sortedBy = sortBy[0]
        this.sortedDesc = sortDesc[0]
        const query = store.getters.searchQuery
        query.sortKey = sortBy[0]
        query.sortDesc = sortDesc[0]
        console.log(query)
        this.$store.dispatch('setSearchQuery', this.searchQuery)
        this.$emit('search')
      }
      return items
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
