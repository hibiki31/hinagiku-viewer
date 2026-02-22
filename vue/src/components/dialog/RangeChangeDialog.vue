<template>
  <v-dialog v-model="dialogState" max-width="600" persistent>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-pencil-box-multiple</v-icon>
        一括編集
      </v-card-title>

      <v-divider />

      <v-card-text class="pt-4">
        <!-- 処理対象範囲の選択 -->
        <div class="mb-4">
          <v-chip
            :color="targetMode === 'current' ? 'primary' : 'default'"
            variant="flat"
            class="mr-2"
          >
            <v-icon start>mdi-book-multiple</v-icon>
            {{ targetMode === 'current' ? `現在のページ: ${currentPageCount}件` : `全ページ: ${totalCount}件` }}
          </v-chip>
        </div>

        <v-radio-group v-model="targetMode" :disabled="isProcessing" class="mb-4">
          <v-radio value="current" color="primary">
            <template #label>
              <div class="text-body-1">
                <strong>現在のページのみ</strong>
                <span class="text-grey ml-2">(最大60件)</span>
              </div>
            </template>
          </v-radio>
          <v-radio value="all" color="warning">
            <template #label>
              <div class="text-body-1">
                <strong>全ページを自動処理</strong>
                <span class="text-grey ml-2">(検索条件に該当する全ての本)</span>
              </div>
            </template>
          </v-radio>
        </v-radio-group>

        <v-alert
          v-if="targetMode === 'all'"
          type="warning"
          variant="tonal"
          density="compact"
          class="mb-4"
        >
          <div class="text-body-2">
            現在の検索条件に該当する全ての本（約{{ totalCount }}件）が対象になります。
            <br>
            この操作は取り消せません。
          </div>
        </v-alert>

        <v-divider class="mb-4" />

        <!-- ライブラリ変更 -->
        <div class="mb-4">
          <v-switch
            v-model="changeLibrary"
            :disabled="isProcessing"
            color="primary"
            hide-details
            class="mb-2"
          >
            <template #label>
              <div class="d-flex align-center">
                <v-icon class="mr-2">mdi-bookshelf</v-icon>
                <span class="text-body-1 font-weight-medium">ライブラリを変更</span>
              </div>
            </template>
          </v-switch>

          <v-expand-transition>
            <v-select
              v-if="changeLibrary"
              v-model="queryLibrary"
              :items="libraryList"
              :disabled="isProcessing"
              label="変更先のライブラリ"
              item-title="name"
              item-value="id"
              density="comfortable"
              variant="outlined"
              prepend-inner-icon="mdi-bookshelf"
              class="mt-2"
            />
          </v-expand-transition>
        </div>

        <!-- 評価変更 -->
        <div class="mb-2">
          <v-switch
            v-model="changeRate"
            :disabled="isProcessing"
            color="primary"
            hide-details
            class="mb-2"
          >
            <template #label>
              <div class="d-flex align-center">
                <v-icon class="mr-2">mdi-star</v-icon>
                <span class="text-body-1 font-weight-medium">評価を変更</span>
              </div>
            </template>
          </v-switch>

          <v-expand-transition>
            <div v-if="changeRate" class="mt-2">
              <div class="d-flex align-center justify-center mb-2">
                <v-rating
                  :model-value="queryRate ?? undefined"
                  :disabled="isProcessing"
                  size="large"
                  color="amber"
                  active-color="amber"
                  @update:model-value="(value) => queryRate = value as number"
                />
              </div>
              <div class="d-flex justify-center">
                <v-btn
                  :variant="queryRate === null ? 'flat' : 'outlined'"
                  :color="queryRate === null ? 'grey' : undefined"
                  :disabled="isProcessing"
                  size="small"
                  prepend-icon="mdi-star-off"
                  @click="queryRate = null"
                >
                  未評価に設定
                </v-btn>
              </div>
            </div>
          </v-expand-transition>
        </div>

        <!-- プログレス表示 -->
        <v-expand-transition>
          <div v-if="isProcessing" class="mt-4">
            <v-card variant="tonal" color="primary">
              <v-card-text>
                <div class="text-center mb-2">
                  <v-progress-circular
                    :model-value="progressPercentage"
                    :size="80"
                    :width="8"
                    color="primary"
                  >
                    {{ progressPercentage }}%
                  </v-progress-circular>
                </div>
                <div class="text-center">
                  <div class="text-body-1 font-weight-medium">
                    処理中: {{ processedCount }} / {{ totalProcessCount }}件
                  </div>
                  <div v-if="targetMode === 'all'" class="text-body-2 text-grey mt-1">
                    ページ {{ currentProcessPage }} / {{ totalPages }}
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </div>
        </v-expand-transition>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-btn
          variant="text"
          :disabled="isProcessing"
          @click="closeDialog"
        >
          {{ isProcessing ? '処理中...' : 'キャンセル' }}
        </v-btn>
        <v-spacer />
        <v-btn
          :color="targetMode === 'all' ? 'warning' : 'primary'"
          :disabled="!canSubmit || isProcessing"
          :loading="isProcessing"
          variant="flat"
          @click="submitDialog"
        >
          <v-icon start>mdi-check-circle</v-icon>
          {{ targetMode === 'all' ? '全ページを一括変更' : '変更を実行' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { apiClient } from '@/func/client'
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

// ダイアログの状態
const dialogState = ref(false)
const isProcessing = ref(false)

// 処理対象モード
const targetMode = ref<'current' | 'all'>('current')

// ライブラリ
const libraryList = ref<GetLibrary[]>([])
const queryLibrary = ref<number>(0)
const changeLibrary = ref(false)

// 評価
const queryRate = ref<number | null>(null)
const changeRate = ref(false)

// プログレス
const processedCount = ref(0)
const totalProcessCount = ref(0)
const currentProcessPage = ref(0)
const totalPages = ref(0)

// 現在のページのUUID一覧
const currentPageUuids = computed(() => readerStateStore.booksList.map((x: BookBase) => x.uuid))

// 現在のページの件数
const currentPageCount = computed(() => currentPageUuids.value.length)

// 全体の件数
const totalCount = computed(() => readerStateStore.booksCount)

// 進捗率
const progressPercentage = computed(() => {
  if (totalProcessCount.value === 0) return 0
  return Math.round((processedCount.value / totalProcessCount.value) * 100)
})

// 実行可能かどうか
const canSubmit = computed(() => {
  return changeLibrary.value || changeRate.value
})

/**
 * ダイアログを開く
 */
const openDialog = async () => {
  dialogState.value = true
  targetMode.value = 'current'
  changeLibrary.value = false
  changeRate.value = false
  queryRate.value = null
  isProcessing.value = false
  processedCount.value = 0
  totalProcessCount.value = 0
  currentProcessPage.value = 0
  totalPages.value = 0

  // ライブラリ情報取得
  try {
    const { data, error } = await apiClient.GET('/api/libraries', {})
    if (error) throw error
    if (data) {
      libraryList.value = data
      if (data.length > 0) {
        queryLibrary.value = data[0].id
      }
    }
  } catch {
    console.error('ライブラリ情報取得エラー')
  }
}

/**
 * ダイアログを閉じる
 */
const closeDialog = () => {
  if (isProcessing.value) return
  dialogState.value = false
}

/**
 * 単一ページの処理を実行
 */
const processSinglePage = async (uuids: string[]) => {
  const errors: string[] = []

  if (changeLibrary.value) {
    try {
      const { error } = await apiClient.PUT('/api/books', {
        body: { uuids, libraryId: queryLibrary.value }
      })
      if (error) throw new Error('ライブラリ変更エラー')
    } catch (e) {
      errors.push('ライブラリの変更に失敗')
      console.error(e)
    }
  }

  if (changeRate.value) {
    try {
      const { error } = await apiClient.PUT('/api/books/user-data', {
        body: { uuids, rate: queryRate.value ?? undefined }
      })
      if (error) throw new Error('評価変更エラー')
    } catch (e) {
      errors.push('評価の変更に失敗')
      console.error(e)
    }
  }

  return errors
}

/**
 * 現在のページのみ処理
 */
const processCurrentPage = async () => {
  isProcessing.value = true
  processedCount.value = 0
  totalProcessCount.value = currentPageCount.value

  const errors = await processSinglePage(currentPageUuids.value)

  processedCount.value = currentPageCount.value

  if (errors.length === 0) {
    pushNotice(`${currentPageCount.value}件の変更が完了しました`, 'success')
  } else {
    pushNotice(`一部の変更に失敗しました: ${errors.join(', ')}`, 'error')
  }

  isProcessing.value = false
}

/**
 * 全ページを処理
 */
const processAllPages = async () => {
  isProcessing.value = true
  processedCount.value = 0
  currentProcessPage.value = 0

  // 現在の検索クエリを取得
  const searchQuery = readerStateStore.searchQuery
  const limit = 60 // 1ページあたりの件数

  // 総ページ数を計算
  totalPages.value = Math.ceil(totalCount.value / limit)
  totalProcessCount.value = totalCount.value

  let allErrors: string[] = []

  // 各ページを順次処理
  for (let page = 0; page < totalPages.value; page++) {
    currentProcessPage.value = page + 1

    // 現在のページのデータを取得
    try {
      const { data, error } = await apiClient.GET('/api/books', {
        params: {
          query: {
            uuid: searchQuery.uuid ?? undefined,
            fileNameLike: searchQuery.fileNameLike ?? undefined,
            cached: searchQuery.cached ?? undefined,
            authorLike: searchQuery.authorLike ?? undefined,
            authorIsFavorite: searchQuery.authorIsFavorite ?? undefined,
            titleLike: searchQuery.titleLike ?? undefined,
            fullText: searchQuery.fullText || undefined,
            rate: searchQuery.rate ?? undefined,
            seriesId: searchQuery.seriesId ?? undefined,
            genreId: searchQuery.genre ?? undefined,
            libraryId: searchQuery.libraryId ?? undefined,
            tag: searchQuery.tag ?? undefined,
            state: searchQuery.state as components['schemas']['BookStateEnum'] | undefined,
            limit,
            offset: page * limit,
            sortKey: searchQuery.sortKey,
            sortDesc: searchQuery.sortDesc
          }
        }
      })

      if (error) throw error
      if (!data || !data.rows || data.rows.length === 0) {
        break
      }

      // UUIDリストを抽出
      const uuids = data.rows.map((book: BookBase) => book.uuid)

      // このページの書籍を処理
      const errors = await processSinglePage(uuids)
      allErrors = [...allErrors, ...errors]

      // 処理済み件数を更新
      processedCount.value += uuids.length

      // 少し待機（APIへの負荷軽減）
      await new Promise(resolve => setTimeout(resolve, 100))

    } catch (e) {
      console.error(`ページ ${page + 1} の処理中にエラー:`, e)
      allErrors.push(`ページ ${page + 1} の処理に失敗`)
    }
  }

  // 完了メッセージ
  if (allErrors.length === 0) {
    pushNotice(`全${processedCount.value}件の変更が完了しました`, 'success')
  } else {
    pushNotice(
      `${processedCount.value}件中、一部の変更に失敗しました`,
      'warn'
    )
    console.error('エラー詳細:', allErrors)
  }

  isProcessing.value = false
}

/**
 * 変更を実行
 */
const submitDialog = async () => {
  if (!canSubmit.value || isProcessing.value) return

  // 確認ダイアログ（全ページモードの場合）
  if (targetMode.value === 'all') {
    const confirmed = confirm(
      `本当に全${totalCount.value}件を一括変更しますか？\nこの操作は取り消せません。`
    )
    if (!confirmed) return
  }

  try {
    if (targetMode.value === 'current') {
      await processCurrentPage()
    } else {
      await processAllPages()
    }

    // 検索を再実行
    emit('search')

    // ダイアログを閉じる
    dialogState.value = false
  } catch (e) {
    console.error('処理中にエラー:', e)
    pushNotice('処理中にエラーが発生しました', 'error')
    isProcessing.value = false
  }
}

defineExpose({
  openDialog
})
</script>

<style scoped>
.v-switch :deep(.v-label) {
  opacity: 1;
}
</style>
