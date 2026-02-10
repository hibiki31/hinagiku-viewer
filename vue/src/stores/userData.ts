import { defineStore } from 'pinia'
import { apiClient } from '@/func/client'
import Cookies from 'js-cookie'

interface UserDataState {
  isLoaded: boolean
  isAuthed: boolean
  isInitialized: boolean
  accessToken: string | null
  username: string | null
  isAdmin: boolean
}

let _initPromise: Promise<void> | null = null

export const useUserDataStore = defineStore('userData', {
  state: (): UserDataState => ({
    isLoaded: true,
    isAuthed: false,
    isInitialized: false,
    accessToken: null,
    username: null,
    isAdmin: false
  }),

  actions: {
    /**
     * アプリ起動時にCookieからトークンを復元し、APIでバリデーションする。
     * 複数回呼ばれても最初の1回だけ実行される。
     */
    init(): Promise<void> {
      if (_initPromise) return _initPromise

      _initPromise = (async () => {
        const accessToken = Cookies.get('accessToken')

        if (accessToken) {
          try {
            const { data, error } = await apiClient.GET('/api/auth/validate')
            if (error) throw error
            if (data) {
              this.authenticaitonSuccessful(accessToken, data.username)
              this.isAdmin = data.is_admin
            }
          } catch {
            this.authenticaitonFail()
          }
        } else {
          this.authenticaitonFail()
        }

        this.isInitialized = true
      })()

      return _initPromise
    },

    authenticaitonSuccessful(accessToken: string, username?: string) {
      Cookies.set('accessToken', accessToken, { expires: 365 })

      this.accessToken = accessToken
      this.username = username || null
      this.isAuthed = true
      this.isLoaded = false
    },

    authenticaitonFail() {
      this.isAuthed = false
      this.isLoaded = false
      Cookies.remove('accessToken')
    },

    async authVerification() {
      if (!this.accessToken) return

      try {
        const { data, error } = await apiClient.GET('/api/auth/validate')
        if (error) throw error
        if (data) {
          this.isAdmin = data.is_admin
        }
      } catch {
        this.authenticaitonFail()
      }
    },

    /**
     * ログアウト処理
     * Cookieとストアの認証情報をクリアする
     */
    logout() {
      Cookies.remove('accessToken')
      this.accessToken = null
      this.username = null
      this.isAuthed = false
      this.isAdmin = false
    }
  }
})
