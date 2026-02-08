/**
 * main.ts
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createApp } from 'vue'

// PWA
import { registerSW } from 'virtual:pwa-register'

const app = createApp(App)

registerPlugins(app)

app.mount('#app')

// Service Worker登録
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const updateSW = registerSW({
  onNeedRefresh() {
    console.log('新しいバージョンが利用可能です')
    // 自動更新を実行（必要に応じて確認ダイアログを表示することも可能）
  },
  onOfflineReady() {
    console.log('オフラインで使用可能です')
  },
  onRegistered(registration) {
    console.log('Service Worker登録完了', registration)
  },
  onRegisterError(error) {
    console.error('Service Worker登録エラー', error)
  },
})
