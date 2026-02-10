import { defineStore } from 'pinia'
import { apiClient } from '@/func/client'
import type { components } from '@/api'

type SystemSettingSchema = components['schemas']['SystemSettingSchema']
type SystemSettingValueSchema = components['schemas']['SystemSettingValueSchema']
type SystemSettingBulkUpdateSchema = components['schemas']['SystemSettingBulkUpdateSchema']

interface SystemSettingsState {
  settings: SystemSettingSchema[]
  isLoading: boolean
  categories: string[]
}

export const useSystemSettingsStore = defineStore('systemSettings', {
  state: (): SystemSettingsState => ({
    settings: [],
    isLoading: false,
    categories: [],
  }),

  getters: {
    /**
     * カテゴリ一覧を取得
     */
    getCategories: (state) => {
      const categorySet = new Set<string>()
      state.settings.forEach((setting) => {
        if (setting.category) {
          categorySet.add(setting.category)
        }
      })
      return Array.from(categorySet).sort()
    },

    /**
     * カテゴリ別に設定を取得
     */
    getSettingsByCategory: (state) => (category: string) => {
      return state.settings.filter((setting) => setting.category === category)
    },

    /**
     * キーで設定を取得
     */
    getSettingByKey: (state) => (key: string) => {
      return state.settings.find((setting) => setting.key === key)
    },
  },

  actions: {
    /**
     * 設定一覧を取得
     */
    async fetchSettings(category?: string) {
      this.isLoading = true
      try {
        const { data, error } = await apiClient.GET('/api/system/settings', {
          params: {
            query: category ? { category } : {},
          },
        })
        if (error) throw error
        if (data) {
          this.settings = data.settings
        }
      } catch (error) {
        console.error('設定の取得に失敗:', error)
        throw error
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 個別設定を取得
     */
    async fetchSettingByKey(key: string) {
      try {
        const { data, error } = await apiClient.GET('/api/system/settings/{key}', {
          params: {
            path: { key },
          },
        })
        if (error) throw error
        return data
      } catch (error) {
        console.error(`設定 ${key} の取得に失敗:`, error)
        throw error
      }
    },

    /**
     * 設定を更新
     */
    async updateSetting(key: string, value: string) {
      try {
        const body: SystemSettingValueSchema = { value }
        const { data, error } = await apiClient.PUT('/api/system/settings/{key}', {
          params: {
            path: { key },
          },
          body,
        })
        if (error) throw error

        // ローカルの設定も更新
        const index = this.settings.findIndex((s) => s.key === key)
        if (index !== -1 && data) {
          this.settings[index] = data
        }
        return data
      } catch (error) {
        console.error(`設定 ${key} の更新に失敗:`, error)
        throw error
      }
    },

    /**
     * 設定を一括更新
     */
    async bulkUpdateSettings(settings: Record<string, string>) {
      try {
        const body: SystemSettingBulkUpdateSchema = { settings }
        const { error } = await apiClient.POST('/api/system/settings/bulk', {
          body,
        })
        if (error) throw error

        // 更新後に設定一覧を再取得
        await this.fetchSettings()
      } catch (error) {
        console.error('設定の一括更新に失敗:', error)
        throw error
      }
    },

    /**
     * 設定を作成
     */
    async createSetting(setting: components['schemas']['SystemSettingCreateSchema']) {
      try {
        const { data, error } = await apiClient.POST('/api/system/settings', {
          body: setting,
        })
        if (error) throw error

        // 設定一覧を再取得
        await this.fetchSettings()
        return data
      } catch (error) {
        console.error('設定の作成に失敗:', error)
        throw error
      }
    },

    /**
     * 設定を削除
     */
    async deleteSetting(key: string) {
      try {
        const { error } = await apiClient.DELETE('/api/system/settings/{key}', {
          params: {
            path: { key },
          },
        })
        if (error) throw error

        // ローカルの設定も削除
        this.settings = this.settings.filter((s) => s.key !== key)
      } catch (error) {
        console.error(`設定 ${key} の削除に失敗:`, error)
        throw error
      }
    },
  },
})
