<template>
    <v-data-table
          :headers="headers"
          :items="booksList"
          :items-per-page="searchQuery.limit"
          hide-default-footer
        >
        <template v-slot:[`item.title`]="props">
          <v-edit-dialog
            :return-value.sync="props.item.title"
            @save="save(props.item)"
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
            class="ma-2"
            small
            close
            @click:close="deleteAuthor(item, author.id)"
          >
            {{ author.name }}
          </v-chip>
        </template>
    </v-data-table>
</template>

<script>
import store from '@/store'
import axios from '@/axios/index'

export default {
  data: function () {
    return {
      dialogState: false,
      searchQuery: {},
      topBerQuery: null,
      headers: [
        { text: 'title', value: 'title' },
        { text: 'authors', value: 'authors' },
        { text: 'publisher', value: 'publisher.name' },
        { text: 'actions', value: 'actions' }
      ]
    }
  },
  computed: {
    booksList () {
      return store.getters.booksList
    },
    booksCount () {
      return store.getters.booksCount
    }
  },
  methods: {
    deleteAuthor (book, id) {
      axios
        .request({
          method: 'delete',
          url: '/api/books',
          data: { uuids: [book.uuid], author: id }
        })
        .then((response) =>
          this.$_pushNotice('著者削除', 'success')
        )
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
