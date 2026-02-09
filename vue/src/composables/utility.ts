import { notify } from "@kyvg/vue3-notification"

/**
 * スリープ関数
 */
export function useSleep() {
  const sleep = (msec: number) => {
    return new Promise(resolve => setTimeout(resolve, msec))
  }
  return { sleep }
}

/**
 * 数値フォーマット変換
 */
export function useConvertNumFormat() {
  const convertNumFormat = (num: number | null | undefined): string => {
    if (!num) {
      return '0'
    } else if (num < 10000) {
      return num.toLocaleString()
    }
    const formatNum = String(num).slice(0, -3)
    return formatNum[0] + '.' + formatNum[1] + '万'
  }
  return { convertNumFormat }
}

/**
 * 日付フォーマット変換
 */
export function useConvertDateFormat() {
  const convertDateFormat = (date: string | null | undefined): string | undefined => {
    if (!date) {
      return undefined
    }
    const dt = new Date(Date.parse(date))
    const y = dt.getFullYear()
    const m = ('00' + (dt.getMonth() + 1)).slice(-2)
    const d = ('00' + dt.getDate()).slice(-2)
    return (y + '-' + m + '-' + d)
  }
  return { convertDateFormat }
}

/**
 * 通知表示
 */
export function usePushNotice() {
  const pushNotice = (
    text: string,
    type: 'success' | 'error' | 'info' | 'warn' = 'info',
    title?: string,
    duration: number = 900
  ) => {
    notify({
      title: title || '',
      text,
      type,
      duration
    })
  }
  return { pushNotice }
}

/**
 * APIエラーハンドラー
 */
export function useApiErrorHandler() {
  const { pushNotice } = usePushNotice()

  const apiErrorHandler = (error: unknown) => {
    const fetchError = error as { status?: number; detail?: string; message?: string }
    if (!fetchError.status) {
      pushNotice('サーバーエラーが発生しました', 'error')
      return
    }
    if (fetchError.status === 401 || fetchError.status === 400) {
      pushNotice('認証エラーが発生しました', 'error')
    } else {
      pushNotice(fetchError.detail || fetchError.message || 'エラーが発生しました', 'error')
    }
  }
  return { apiErrorHandler }
}

/**
 * カバー画像URL取得
 */
export function useGetCoverURL() {
  const getCoverURL = (uuid: string): string => {
    const api = import.meta.env.VITE_APP_API_HOST
    if (api) {
      return api + '/media/books/' + uuid
    } else {
      return '/media/books/' + uuid
    }
  }
  return { getCoverURL }
}

/**
 * バイトサイズフィット
 */
export function useFitByte() {
  const fitByte = (size: number): string => {
    if (size >= Math.pow(1024, 2)) {
      return (size / Math.pow(1024, 2)).toFixed(1) + 'MB'
    } else if (size >= 1024) {
      return (size / 1024).toFixed(1) + 'KB'
    } else {
      return size + 'B'
    }
  }
  return { fitByte }
}
