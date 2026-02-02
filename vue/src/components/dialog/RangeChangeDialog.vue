<template>
  <v-dialog v-model="dialogState" max-width="400">
    <v-card>
      <v-card-title>一括編集</v-card-title>
      <v-card-text> {{ uuids.length }}件の本を一括で編集 </v-card-text>
      <v-card-text>
        <v-row>
          <v-checkbox v-model="changeLibrary"></v-checkbox>
          <v-select
            :items="libraryList"
            label="Library"
            v-model="queryLibrary"
            item-title="name"
            item-value="id"
            density="compact"
            class="pr-2 pl-2 pt-3"
          ></v-select>
        </v-row>
        <v-row>
          <v-checkbox v-model="changeRate"></v-checkbox>
          <v-rating v-model="queryRate" size="small" class="mt-4"></v-rating>
          <v-btn @click="queryRate = null" size="small" class="mt-4">未評価</v-btn>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" variant="text" @click="dialogState = false">閉じる</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="error" variant="text" @click="submitDialog()">置き換え</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from '@/func/axios'
import { useReaderStateStore } from '@/stores/readerState'
import { usePushNotice } from '@/composables/utility'

const readerStateStore = useReaderStateStore()
const { pushNotice } = usePushNotice()

const emit = defineEmits<{
  search: []
}>()

const dialogState = ref(false)
const libraryList = ref<any[]>([])
const queryLibrary = ref<number>(0)
const queryRate = ref<number | null>(null)
const changeLibrary = ref(false)
const changeRate = ref(false)

const uuids = computed(() => readerStateStore.booksList.map((x: any) => x.uuid))

const openDialog = async () => {
  dialogState.value = true
  try {
    const response = await axios.get('/api/librarys')
    libraryList.value = response.data
  } catch (error) {
    console.error('ライブラリ情報取得エラー:', error)
  }
}

const submitDialog = async () => {
  if (changeLibrary.value) {
    try {
      await axios.request({
        method: 'put',
        url: '/api/books',
        data: { uuids: uuids.value, libraryId: queryLibrary.value }
      })
      pushNotice('ライブラリを一括変更しました', 'success')
    } catch (error) {
      pushNotice('ライブラリの変更に失敗しました', 'error')
    }
  }
  if (changeRate.value) {
    try {
      await axios.request({
        method: 'put',
        url: '/api/books/user-data',
        data: { uuids: uuids.value, rate: queryRate.value }
      })
      pushNotice('評価を一括更新しました', 'success')
    } catch (error) {
      pushNotice('評価の更新に失敗しました', 'error')
    }
  }
  emit('search')
  dialogState.value = false
}

defineExpose({
  openDialog
})
</script>
