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
        <v-btn color="error" variant="text" prepend-icon="mdi-delete" @click="deleteConfirmDialog = true">
          削除
        </v-btn>
        <v-spacer />
        <v-btn color="blue-darken-1" variant="text" @click="dialogState = false">
          閉じる
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- 削除確認ダイアログ -->
    <v-dialog v-model="deleteConfirmDialog" max-width="500">
      <v-card>
        <v-card-title class="d-flex align-center pa-4 bg-error">
          <v-icon class="mr-2" color="white">
            mdi-alert-circle
          </v-icon>
          <span class="text-white">本の削除</span>
        </v-card-title>
        <v-card-text class="pt-4">
          <v-alert type="error" variant="tonal" class="mb-4">
            <div class="text-subtitle-2 mb-2">
              ⚠️ この操作は取り消せません
            </div>
            <div class="text-body-2">
              以下の本のファイルとすべてのデータが完全に削除されます：
            </div>
          </v-alert>
          <div class="pa-3 bg-grey-lighten-4 rounded">
            <div class="text-subtitle-1 font-weight-bold mb-1">
              {{ openBook.title || '(タイトルなし)' }}
            </div>
            <div class="text-caption text-medium-emphasis">
              UUID: {{ openBook.uuid }}
            </div>
          </div>
          <div class="mt-4 text-body-2">
            本当に削除してもよろしいですか？
          </div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn variant="text" @click="deleteConfirmDialog = false">
            キャンセル
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            prepend-icon="mdi-delete"
            :loading="deleteLoading"
            @click="handleDeleteBook"
          >
            削除する
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
  bookDeleted: [uuid: string]
}>()

const dialogState = ref(false)
const libraryList = ref<GetLibrary[]>([])
const deleteConfirmDialog = ref(false)
const deleteLoading = ref(false)

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

const handleDeleteBook = async () => {
  if (!openBook.value.uuid) {
    pushNotice('本のUUIDが取得できません', 'error')
    return
  }

  deleteLoading.value = true

  try {
    const { error } = await apiClient.DELETE('/api/books/{book_uuid}', {
      params: {
        path: {
          book_uuid: openBook.value.uuid
        }
      }
    })
    if (error) throw error

    pushNotice('本を削除しました', 'success')

    // 削除イベントを発火
    emit('bookDeleted', openBook.value.uuid)
    emit('search')

    // ダイアログを閉じる
    deleteConfirmDialog.value = false
    dialogState.value = false
  } catch (error) {
    console.error('削除エラー:', error)
    pushNotice('本の削除に失敗しました', 'error')
  } finally {
    deleteLoading.value = false
  }
}

defineExpose({
  openDialog
})
</script>
