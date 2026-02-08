import type { paths } from "@/api"
import createClient, { type Middleware } from "openapi-fetch"
import Cookies from "js-cookie"

/**
 * 認証ミドルウェア: CookieからBearerトークンを取得しリクエストヘッダーに付与
 */
const authMiddleware: Middleware = {
  async onRequest({ request }) {
    const token = Cookies.get("accessToken")
    if (token) {
      request.headers.set("Authorization", `Bearer ${token}`)
    }
    return request
  },
}

/**
 * エラーハンドリングミドルウェア: 401レスポンス時に自動ログアウト
 */
const errorMiddleware: Middleware = {
  async onResponse({ response }) {
    if (response.status === 401) {
      // 循環参照を避けるため動的インポート
      const { useUserDataStore } = await import("@/stores/userData")
      const userDataStore = useUserDataStore()
      if (userDataStore.isAuthed) {
        userDataStore.authenticaitonFail()
        window.location.reload()
      }
    }
    return response
  },
}

export const apiClient = createClient<paths>({
  baseUrl: import.meta.env.VITE_APP_API_HOST || "",
})

apiClient.use(authMiddleware)
apiClient.use(errorMiddleware)

export type APIClient = typeof apiClient
