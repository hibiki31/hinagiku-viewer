<template>
  <div>
    <v-dialog width="400" v-model="postDialogState">
      <v-card>
        <v-card-title>著者追加</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="postAuthorName"
            :rules="[required, limitLength64]"
            counter="64"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="postAuthor">追加</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-menu v-for="author in openBook.authors" :key="author.id">
      <template v-slot:activator="{ props: menuProps }">
        <v-tooltip location="bottom">
          <template v-slot:activator="{ props: tooltipProps }">
            <v-chip
              class="mt-2 mb-2 mr-2"
              size="small"
              :color="getAuthorColor(author.isFavorite)"
              closable
              v-bind="{ ...tooltipProps, ...menuProps }"
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
          <div class="ma-3" @click="searchAuthor(author.name)" style="cursor: pointer">
            <v-icon color="primary">mdi-magnify</v-icon>
            この著者で検索する
          </div>
          <div
            class="ma-3"
            @click="favoriteAuthor(author, true)"
            v-if="author.isFavorite === false"
            style="cursor: pointer"
          >
            <v-icon color="primary">mdi-star</v-icon>
            この著者をお気に入りにする
          </div>
          <div
            class="ma-3"
            @click="favoriteAuthor(author, false)"
            v-if="author.isFavorite === true"
            style="cursor: pointer"
          >
            <v-icon>mdi-star</v-icon>
            この著者をお気に入りから外す
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
    <v-icon size="small" @click="openPostDialog(openBook)">mdi-plus-circle</v-icon>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useReaderStateStore } from '@/stores/readerState'
import axios from '@/func/axios'
import { usePushNotice, useApiErrorHandler } from '@/composables/utility'
import { required, limitLength64 } from '@/composables/rules'

const readerStateStore = useReaderStateStore()
const { pushNotice } = usePushNotice()
const { apiErrorHandler } = useApiErrorHandler()

const props = defineProps<{
  openBook: any
}>()

const emit = defineEmits<{
  search: []
}>()

const postDialogState = ref(false)
const postAuthorName = ref('')

const openPostDialog = (book: any) => {
  postDialogState.value = true
}

const getAuthorColor = (isFavorite: boolean): string => {
  if (isFavorite) {
    return 'orange'
  } else {
    return ''
  }
}

const favoriteAuthor = async (author: any, favorite: boolean) => {
  try {
    await axios.request({
      method: 'patch',
      url: '/api/authors',
      data: { authorId: author.id, isFavorite: favorite }
    })
    pushNotice('著者のお気に入り変更', 'success')
    author.isFavorite = favorite
  } catch (error) {
    apiErrorHandler(error)
  }
}

const searchAuthor = (authorName: string) => {
  const query = { ...readerStateStore.searchQuery }
  query.fullText = authorName
  readerStateStore.setSearchQuery(query)
  emit('search')
}

const postAuthor = async () => {
  try {
    const response = await axios.request({
      method: 'post',
      url: `/api/books/${props.openBook.uuid}/authors`,
      data: { authorName: postAuthorName.value }
    })
    pushNotice('著者追加成功', 'success')
    readerStateStore.setOpenBook(response.data)
    await readerStateStore.serachBooks()
  } catch (error) {
    apiErrorHandler(error)
  }
  postDialogState.value = false
}

const deleteAuthor = async (book: any, id: number) => {
  try {
    const response = await axios.request({
      method: 'delete',
      url: `/api/books/${book.uuid}/authors`,
      data: { authorId: id }
    })
    pushNotice('著者削除', 'success')
    readerStateStore.setOpenBook(response.data)
    await readerStateStore.serachBooks()
  } catch (error) {
    apiErrorHandler(error)
  }
}
</script>
