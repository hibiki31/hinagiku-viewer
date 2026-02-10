<template>
  <div class="system-settings">
    <v-app-bar color="primary" dark density="compact" elevation="4">
      <v-btn icon @click="goBack">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <v-toolbar-title>システム設定</v-toolbar-title>
      <v-spacer />
      <v-btn
        :disabled="!hasChanges || isSaving"
        :loading="isSaving"
        icon
        @click="saveAllChanges"
      >
        <v-icon>mdi-content-save</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-card v-if="!isAdmin" class="mt-4">
          <v-card-text class="text-center py-8">
            <v-icon size="64" color="error">
              mdi-lock
            </v-icon>
            <div class="text-h6 mt-4">
              アクセス権限がありません
            </div>
            <div class="text-body-2 text-grey mt-2">
              この機能は管理者のみ使用できます
            </div>
          </v-card-text>
        </v-card>

        <div v-else>
          <!-- ローディング表示 -->
          <v-progress-linear
            v-if="settingsStore.isLoading"
            indeterminate
            color="primary"
            class="mb-4"
          />

          <!-- カテゴリがない場合 -->
          <v-card v-if="!settingsStore.isLoading && categories.length === 0" class="mt-4">
            <v-card-text class="text-center py-8">
              <v-icon size="64" color="grey">
                mdi-cog-outline
              </v-icon>
              <div class="text-h6 mt-4">
                設定項目がありません
              </div>
              <div class="text-body-2 text-grey mt-2">
                システム設定が登録されていません
              </div>
            </v-card-text>
          </v-card>

          <!-- カテゴリタブ -->
          <v-card v-if="categories.length > 0" class="mt-4">
            <v-tabs v-model="selectedTab" bg-color="primary">
              <v-tab
                v-for="category in categories"
                :key="category"
                :value="category"
              >
                {{ category || '未分類' }}
              </v-tab>
            </v-tabs>

            <v-window v-model="selectedTab">
              <v-window-item
                v-for="category in categories"
                :key="category"
                :value="category"
              >
                <v-card-text>
                  <v-list>
                    <template
                      v-for="setting in getSettingsByCategory(category)"
                      :key="setting.key"
                    >
                      <v-list-item class="px-0">
                        <div class="setting-item">
                          <!-- 設定キー・説明 -->
                          <div class="setting-header mb-2">
                            <div class="d-flex align-center">
                              <span class="text-subtitle-1 font-weight-bold">
                                {{ setting.key }}
                              </span>
                              <v-chip
                                v-if="setting.isPublic"
                                size="x-small"
                                color="success"
                                class="ml-2"
                              >
                                公開
                              </v-chip>
                              <v-chip
                                v-else
                                size="x-small"
                                color="grey"
                                class="ml-2"
                              >
                                非公開
                              </v-chip>
                              <v-chip
                                size="x-small"
                                color="info"
                                class="ml-2"
                              >
                                {{ setting.dataType }}
                              </v-chip>
                            </div>
                            <div
                              v-if="setting.description"
                              class="text-body-2 text-grey mt-1"
                            >
                              {{ setting.description }}
                            </div>
                          </div>

                          <!-- 入力フィールド -->
                          <div class="setting-input">
                            <!-- boolean型 -->
                            <v-switch
                              v-if="setting.dataType === 'boolean'"
                              :model-value="getEditValue(setting.key) === 'true'"
                              color="primary"
                              hide-details
                              @update:model-value="
                                (value) => updateEditValue(setting.key, value ? 'true' : 'false')
                              "
                            />

                            <!-- number型 -->
                            <v-text-field
                              v-else-if="setting.dataType === 'number'"
                              :model-value="getEditValue(setting.key)"
                              type="number"
                              variant="outlined"
                              density="compact"
                              hide-details
                              @update:model-value="
                                (value) => updateEditValue(setting.key, String(value))
                              "
                            />

                            <!-- string型（デフォルト） -->
                            <v-text-field
                              v-else
                              :model-value="getEditValue(setting.key)"
                              variant="outlined"
                              density="compact"
                              hide-details
                              @update:model-value="
                                (value) => updateEditValue(setting.key, String(value))
                              "
                            />
                          </div>

                          <!-- 更新情報 -->
                          <div class="setting-footer mt-2">
                            <div class="text-caption text-grey">
                              最終更新: {{ formatDate(setting.updatedAt) }}
                              <span v-if="setting.updatedBy">
                                ({{ setting.updatedBy }})
                              </span>
                            </div>
                          </div>
                        </div>
                      </v-list-item>
                      <v-divider />
                    </template>
                  </v-list>
                </v-card-text>
              </v-window-item>
            </v-window>
          </v-card>

          <!-- 保存ボタン（下部固定） -->
          <v-card
            v-if="hasChanges"
            class="save-bar"
            elevation="8"
          >
            <v-card-text class="d-flex align-center justify-space-between py-2">
              <div>
                <span class="text-subtitle-2">
                  {{ changedCount }}件の変更があります
                </span>
              </div>
              <div>
                <v-btn
                  variant="text"
                  @click="resetChanges"
                >
                  キャンセル
                </v-btn>
                <v-btn
                  color="primary"
                  variant="flat"
                  :loading="isSaving"
                  @click="saveAllChanges"
                >
                  保存
                </v-btn>
              </div>
            </v-card-text>
          </v-card>
        </div>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSystemSettingsStore } from '@/stores/systemSettings'
import { useUserDataStore } from '@/stores/userData'
import { usePushNotice } from '@/composables/utility'
import { useTitle } from '@/composables/title'

// ページタイトル設定
useTitle('システム設定')

const router = useRouter()
const settingsStore = useSystemSettingsStore()
const userDataStore = useUserDataStore()
const { pushNotice } = usePushNotice()

const selectedTab = ref<string>('')
const editValues = ref<Record<string, string>>({})
const isSaving = ref(false)

// 管理者チェック
const isAdmin = computed(() => userDataStore.isAdmin)

// カテゴリ一覧
const categories = computed(() => settingsStore.getCategories)

// 変更があるかチェック
const hasChanges = computed(() => Object.keys(editValues.value).length > 0)

// 変更された設定の数
const changedCount = computed(() => Object.keys(editValues.value).length)

/**
 * カテゴリ別に設定を取得
 */
const getSettingsByCategory = (category: string) => {
  return settingsStore.getSettingsByCategory(category)
}

/**
 * 編集中の値を取得
 */
const getEditValue = (key: string): string => {
  if (key in editValues.value) {
    return editValues.value[key]
  }
  const setting = settingsStore.getSettingByKey(key)
  return setting?.value || ''
}

/**
 * 編集値を更新
 */
const updateEditValue = (key: string, value: string) => {
  const setting = settingsStore.getSettingByKey(key)
  if (setting && setting.value !== value) {
    editValues.value[key] = value
  } else {
    delete editValues.value[key]
  }
}

/**
 * 変更をリセット
 */
const resetChanges = () => {
  editValues.value = {}
  pushNotice('変更をキャンセルしました', 'info')
}

/**
 * 全ての変更を保存
 */
const saveAllChanges = async () => {
  if (!hasChanges.value) return

  isSaving.value = true
  try {
    await settingsStore.bulkUpdateSettings(editValues.value)
    pushNotice('設定を保存しました', 'success')
    editValues.value = {}
  } catch (error) {
    pushNotice('設定の保存に失敗しました', 'error')
    console.error('保存エラー:', error)
  } finally {
    isSaving.value = false
  }
}

/**
 * 日時フォーマット
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('ja-JP')
}

/**
 * 戻る
 */
const goBack = () => {
  if (hasChanges.value) {
    if (confirm('保存されていない変更があります。破棄しますか？')) {
      router.push('/')
    }
  } else {
    router.push('/')
  }
}

onMounted(async () => {
  // 管理者でない場合は何もしない
  if (!isAdmin.value) {
    return
  }

  // 設定一覧を取得
  try {
    await settingsStore.fetchSettings()
    // 最初のカテゴリを選択
    if (categories.value.length > 0) {
      selectedTab.value = categories.value[0]
    }
  } catch (error) {
    pushNotice('設定の取得に失敗しました', 'error')
    console.error('設定取得エラー:', error)
  }
})
</script>

<style scoped>
.system-settings {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.setting-item {
  width: 100%;
}

.setting-header {
  border-left: 3px solid rgb(var(--v-theme-primary));
  padding-left: 12px;
}

.setting-input {
  padding-left: 15px;
}

.save-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
</style>
