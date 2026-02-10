<template>
  <v-dialog v-model="dialogState" max-width="700">
    <v-card>
      <v-card-text>
        <v-row class="pt-8">
          <p class="font-weight-bold">
            {{ openBook.title }}
          </p>
        </v-row>
        <v-row>
          <p class="font-weight-black">
            サイズ:
          </p>
          <p>{{ fitByte(openBook.size || 0) }}</p>
        </v-row>
        <v-row>
          <p class="font-weight-black">
            ページ:
          </p>
          <p>{{ openBook.page }}</p>
        </v-row>
        <v-row>
          <v-select
            v-model="openBook.libraryId"
            :items="libraryList"
            label="Library"
            item-title="name"
            item-value="id"
            density="compact"
            @update:model-value="changeBookLibrary"
          />
          <v-rating
            :model-value="openBook.userData.rate ?? undefined"
            size="small"
            class="pa-1"
            @update:model-value="(value) => { openBook.userData.rate = value as number; bookInfoSubmit(); }"
          />
        </v-row>
        <v-row>
          <BaseAuthorChip v-if="openBook.uuid && openBook.authors" :open-book="openBook as any" @search="emit('search')" />
        </v-row>
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <v-btn color="blue-darken-1" variant="text" @click="dialogState = false">
          閉じる
        </v-btn>
        <v-spacer />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { apiClient } from '@/func/client'
import { useReaderStateStore } from '@/stores/readerState'
import { usePushNotice, useFitByte } from '@/composables/utility'
import BaseAuthorChip from '@/components/BaseAuthorChip.vue'
import type { components } from '@/api'

type BookBase = components['schemas']['BookBase']
type GetLibrary = components['schemas']['GetLibrary']

const readerStateStore = useReaderStateStore()
const { pushNotice } = usePushNotice()
const { fitByte } = useFitByte()

const emit = defineEmits<{
  search: []
}>()

const dialogState = ref(false)
const libraryList = ref<GetLibrary[]>([])

const openBook = computed(() => readerStateStore.openBook)

const openDialog = async (book: BookBase) => {
  readerStateStore.setOpenBook(book)
  dialogState.value = true
  try {
    const { data, error } = await apiClient.GET('/api/libraries', {})
    if (error) throw error
    if (data) {
      libraryList.value = data
    }
  } catch {
    console.error('ライブラリ情報取得エラー')
  }
}

const bookInfoSubmit = async () => {
  try {
    const { error } = await apiClient.PUT('/api/books/user-data', {
      body: {
        uuids: [openBook.value.uuid!],
        rate: openBook.value.userData.rate ?? undefined
      }
    })
    if (error) throw error
    pushNotice('評価を更新しました', 'success')
    emit('search')
  } catch {
    pushNotice('評価の更新に失敗しました', 'error')
  }
}

const changeBookLibrary = async () => {
  try {
    const { error } = await apiClient.PUT('/api/books', {
      body: { uuids: [openBook.value.uuid!], libraryId: openBook.value.libraryId }
    })
    if (error) throw error
    pushNotice('ライブラリを変更しました', 'success')
    emit('search')
  } catch {
    pushNotice('ライブラリの変更に失敗しました', 'error')
  }
}

defineExpose({
  openDialog
})
</script>
