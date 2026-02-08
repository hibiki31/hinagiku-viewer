import { defineStore } from 'pinia'
import axios from '@/func/axios'
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
            await axios.get('/api/auth/validate', {
              headers: {
                Authorization: `Bearer ${accessToken}`
              }
            })
            this.authenticaitonSuccessful(accessToken)
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
      // axiosのデフォルトヘッダーに認証トークンを設定
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

      this.accessToken = accessToken
      this.username = username || null
      this.isAuthed = true
      this.isLoaded = false
    },

    authenticaitonFail() {
      this.isAuthed = false
      this.isLoaded = false
      Cookies.remove('accessToken')
      delete axios.defaults.headers.common['Authorization']
    },

    async authVerification() {
      if (!this.accessToken) return

      try {
        await axios.get('/api/auth/validate', {
          headers: {
            Authorization: `Bearer ${this.accessToken}`
          }
        })
      } catch {
        this.authenticaitonFail()
      }
    }
  }
})
