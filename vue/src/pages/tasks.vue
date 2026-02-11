<template>
  <v-container>
    <v-row>
      <v-col>
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon icon="mdi-cog-outline" class="mr-2"></v-icon>
            タスク実行状況
            <v-spacer></v-spacer>
            <v-btn
              icon="mdi-refresh"
              variant="text"
              @click="loadTasks"
              :loading="loading"
            ></v-btn>
          </v-card-title>

          <v-card-text>
            <!-- フィルター -->
            <v-row dense class="mb-4">
              <v-col cols="12" md="4">
                <v-select
                  v-model="statusFilter"
                  :items="statusOptions"
                  label="ステータスフィルタ"
                  clearable
                  density="compact"
                  @update:model-value="loadTasks"
                ></v-select>
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="taskTypeFilter"
                  :items="taskTypeOptions"
                  label="タスク種別フィルタ"
                  clearable
                  density="compact"
                  @update:model-value="loadTasks"
                ></v-select>
              </v-col>
            </v-row>

            <!-- タスク一覧 -->
            <v-list v-if="tasks.length > 0">
              <v-list-item
                v-for="task in tasks"
                :key="task.id"
                class="mb-2"
                border
                rounded
              >
                <template #prepend>
                  <v-avatar :color="getStatusColor(task.status)">
                    <v-icon :icon="getStatusIcon(task.status)" color="white"></v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>
                  {{ getTaskTypeName(task.taskType) }}
                  <v-chip
                    :color="getStatusColor(task.status)"
                    size="small"
                    class="ml-2"
                  >
                    {{ getStatusName(task.status) }}
                  </v-chip>
                </v-list-item-title>

                <v-list-item-subtitle class="mt-1">
                  <div class="d-flex flex-column">
                    <div v-if="task.currentStep" class="mb-1">
                      ステップ: {{ task.currentStep }}
                    </div>
                    <div v-if="task.message" class="mb-1">
                      {{ task.message }}
                    </div>
                    <div v-if="task.errorMessage" class="text-error mb-1">
                      エラー: {{ task.errorMessage }}
                    </div>
                    <div class="text-caption">
                      作成: {{ formatDate(task.createdAt) }}
                      <span v-if="task.startedAt"> / 開始: {{ formatDate(task.startedAt) }}</span>
                      <span v-if="task.completedAt"> / 完了: {{ formatDate(task.completedAt) }}</span>
                    </div>
                  </div>
                </v-list-item-subtitle>

                <!-- プログレスバー -->
                <template #append>
                  <div class="d-flex flex-column align-end" style="min-width: 200px;">
                    <div class="text-caption mb-1">
                      {{ task.currentItem }} / {{ task.totalItems || '?' }} アイテム ({{ task.progress }}%)
                    </div>
                    <v-progress-linear
                      :model-value="task.progress"
                      :color="getStatusColor(task.status)"
                      height="8"
                      rounded
                      style="width: 200px;"
                    ></v-progress-linear>
                  </div>
                </template>
              </v-list-item>
            </v-list>

            <!-- データがない場合 -->
            <v-alert v-else type="info" variant="tonal">
              タスクがありません
            </v-alert>

            <!-- ページネーション -->
            <v-pagination
              v-if="totalPages > 1"
              v-model="currentPage"
              :length="totalPages"
              @update:model-value="loadTasks"
              class="mt-4"
            ></v-pagination>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { apiClient } from '@/func/client'
import type { components } from '@/api'
import { usePushNotice } from '@/composables/utility'

type TaskSchema = components['schemas']['TaskSchema']

// Composables
const { pushNotice } = usePushNotice()

// State
const tasks = ref<TaskSchema[]>([])
const loading = ref(false)
const statusFilter = ref<string | null>(null)
const taskTypeFilter = ref<string | null>(null)
const currentPage = ref(1)
const totalPages = ref(1)
const itemsPerPage = 20

// 自動更新のタイマー
let autoRefreshTimer: ReturnType<typeof setInterval> | null = null

// フィルターオプション
const statusOptions = [
  { title: '待機中', value: 'pending' },
  { title: '実行中', value: 'running' },
  { title: '完了', value: 'completed' },
  { title: '失敗', value: 'failed' },
  { title: 'キャンセル', value: 'cancelled' },
]

const taskTypeOptions = [
  { title: 'ライブラリロード', value: 'load' },
  { title: '類似検索', value: 'sim_all' },
  { title: 'エクスポート', value: 'export' },
  { title: 'UUID エクスポート', value: 'export_uuid' },
  { title: 'メタデータ修正', value: 'fixmetadata' },
  { title: 'ルール適用', value: 'rule' },
  { title: 'サムネイル再作成', value: 'thumbnail_recreate' },
  { title: '整合性チェック', value: 'integrity_check' },
]

// タスク一覧取得
const loadTasks = async () => {
  loading.value = true
  try {
    const offset = (currentPage.value - 1) * itemsPerPage
    const { data, error } = await apiClient.GET('/api/tasks', {
      params: {
        query: {
          status: statusFilter.value || undefined,
          task_type: taskTypeFilter.value || undefined,
          limit: itemsPerPage,
          offset: offset,
        },
      },
    })

    if (error) {
      console.error('タスク一覧取得エラー:', error)
      pushNotice('タスク一覧の取得に失敗しました', 'error')
      return
    }

    if (data) {
      tasks.value = data.rows
      totalPages.value = Math.ceil(data.count / itemsPerPage)
    }
  } catch (err) {
    console.error('タスク一覧取得エラー:', err)
    pushNotice('タスク一覧の取得に失敗しました', 'error')
  } finally {
    loading.value = false
  }
}

// ステータス色
const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending':
      return 'grey'
    case 'running':
      return 'primary'
    case 'completed':
      return 'success'
    case 'failed':
      return 'error'
    case 'cancelled':
      return 'warning'
    default:
      return 'grey'
  }
}

// ステータスアイコン
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'pending':
      return 'mdi-clock-outline'
    case 'running':
      return 'mdi-loading'
    case 'completed':
      return 'mdi-check'
    case 'failed':
      return 'mdi-alert-circle'
    case 'cancelled':
      return 'mdi-cancel'
    default:
      return 'mdi-help'
  }
}

// ステータス名
const getStatusName = (status: string) => {
  switch (status) {
    case 'pending':
      return '待機中'
    case 'running':
      return '実行中'
    case 'completed':
      return '完了'
    case 'failed':
      return '失敗'
    case 'cancelled':
      return 'キャンセル'
    default:
      return status
  }
}

// タスク種別名
const getTaskTypeName = (taskType: string) => {
  const option = taskTypeOptions.find((opt) => opt.value === taskType)
  return option ? option.title : taskType
}

// 日時フォーマット
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

// 自動更新を開始
const startAutoRefresh = () => {
  // 実行中または待機中のタスクがある場合のみ自動更新
  const hasRunningTasks = tasks.value.some(
    (task) => task.status === 'running' || task.status === 'pending'
  )

  if (hasRunningTasks && !autoRefreshTimer) {
    autoRefreshTimer = setInterval(() => {
      loadTasks()
    }, 3000) // 3秒ごとに更新
  } else if (!hasRunningTasks && autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

// ライフサイクル
onMounted(() => {
  loadTasks()
  // 定期的に自動更新状態をチェック
  setInterval(() => {
    startAutoRefresh()
  }, 1000)
})

onUnmounted(() => {
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
  }
})
</script>

<style scoped>
.text-error {
  color: rgb(var(--v-theme-error));
}
</style>
