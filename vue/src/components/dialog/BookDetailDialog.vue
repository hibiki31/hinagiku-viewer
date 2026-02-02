<template>
  <v-dialog v-model="dialogState" max-width="700">
    <v-card>
      <v-card-text>
        <v-row class="pt-8">
          <p class="font-weight-bold">{{ openBook.title }}</p>
        </v-row>
        <v-row>
          <p class="font-weight-black">サイズ:</p>
          <p>{{ fitByte(openBook.size || 0) }}</p>
        </v-row>
        <v-row>
          <p class="font-weight-black">ページ:</p>
          <p>{{ openBook.page }}</p>
        </v-row>
        <v-row>
          <v-select
            :items="libraryList"
            label="Library"
            v-model="openBook.libraryId"
            item-title="name"
            item-value="id"
            @update:model-value="changeBookLibrary"
            density="compact"
          ></v-select>
          <v-rating
            v-model="openBook.userData.rate"
            @update:model-value="bookInfoSubmit"
            size="small"
            class="pa-1"
          ></v-rating>
        </v-row>
        <v-row>
          <BaseAuthorChip :openBook="openBook" @search="emit('search')" />
        </v-row>
      </v-card-text>
      <v-divider></v-divider>
      <v-card-actions>
        <v-btn color="blue-darken-1" variant="text" @click="dialogState = false"> 閉じる </v-btn>
        <v-spacer></v-spacer>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from '@/func/axios'
import { useReaderStateStore } from '@/stores/readerState'
import { usePushNotice, useFitByte } from '@/composables/utility'
import BaseAuthorChip from '@/components/BaseAuthorChip.vue'

const readerStateStore = useReaderStateStore()
const { pushNotice } = usePushNotice()
const { fitByte } = useFitByte()

const emit = defineEmits<{
  search: []
}>()

const dialogState = ref(false)
const libraryList = ref<any[]>([])

const openBook = computed(() => readerStateStore.openBook)

const openDialog = async (book: any) => {
  readerStateStore.setOpenBook(book)
  dialogState.value = true
  try {
    const response = await axios.get('/api/librarys')
    libraryList.value = response.data
  } catch (error) {
    console.error('ライブラリ情報取得エラー:', error)
  }
}

const bookInfoSubmit = async () => {
  try {
    await axios.request({
      method: 'put',
      url: '/api/books/user-data',
      data: {
        uuids: [openBook.value.uuid],
        rate: openBook.value.userData.rate
      }
    })
    pushNotice('評価を更新しました', 'success')
    emit('search')
  } catch (error) {
    pushNotice('評価の更新に失敗しました', 'error')
  }
}

const changeBookLibrary = async () => {
  try {
    await axios.request({
      method: 'put',
      url: '/api/books',
      data: { uuids: [openBook.value.uuid], libraryId: openBook.value.libraryId }
    })
    pushNotice('ライブラリを変更しました', 'success')
    emit('search')
  } catch (error) {
    pushNotice('ライブラリの変更に失敗しました', 'error')
  }
}

defineExpose({
  openDialog
})
</script>
