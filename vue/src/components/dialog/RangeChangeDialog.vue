<template>
  <v-dialog v-model="dialogState" max-width="400">
    <v-card>
      <v-card-title>一括編集</v-card-title>
      <v-card-text> {{ uuids.length }}件の本を一括で編集 </v-card-text>
      <v-card-text>
        <v-row>
          <v-checkbox v-model="changeLibrary" />
          <v-select
            v-model="queryLibrary"
            :items="libraryList"
            label="Library"
            item-title="name"
            item-value="id"
            density="compact"
            class="pr-2 pl-2 pt-3"
          />
        </v-row>
        <v-row>
          <v-checkbox v-model="changeRate" />
          <v-rating
            :model-value="queryRate ?? undefined"
            size="small"
            class="mt-4"
            @update:model-value="(value) => queryRate = value as number"
          />
          <v-btn size="small" class="mt-4" @click="queryRate = null">
            未評価
          </v-btn>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" variant="text" @click="dialogState = false">
          閉じる
        </v-btn>
        <v-spacer />
        <v-btn color="error" variant="text" @click="submitDialog()">
          置き換え
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from '@/func/axios'
import { useReaderStateStore } from '@/stores/readerState'
import { usePushNotice } from '@/composables/utility'
import type { components } from '@/api'

type BookBase = components['schemas']['BookBase']
type GetLibrary = components['schemas']['GetLibrary']

const readerStateStore = useReaderStateStore()
const { pushNotice } = usePushNotice()

const emit = defineEmits<{
  search: []
}>()

const dialogState = ref(false)
const libraryList = ref<GetLibrary[]>([])
const queryLibrary = ref<number>(0)
const queryRate = ref<number | null>(null)
const changeLibrary = ref(false)
const changeRate = ref(false)

const uuids = computed(() => readerStateStore.booksList.map((x: BookBase) => x.uuid))

const openDialog = async () => {
  dialogState.value = true
  try {
    const response = await axios.get('/api/librarys')
    libraryList.value = response.data
  } catch {
    console.error('ライブラリ情報取得エラー')
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
    } catch {
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
    } catch {
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
