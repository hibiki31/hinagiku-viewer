<template>
  <v-app>
    <!-- 通知 -->
    <notifications position="top right" width="290px" class="pt-14">
      <template #body="props">
        <v-alert
          :type="props.item.type"
          class="text-caption ma-1"
          density="compact"
          border="start"
          variant="text"
          style="background-color: white"
        >
          <v-alert-title class="text-subtitle-2">{{ props.item.title }}</v-alert-title>
          {{ props.item.text }}
        </v-alert>
      </template>
    </notifications>
    <!-- メイン -->
    <v-main>
      <router-view v-slot="{ Component }">
        <transition name="fade">
          <component :is="Component" />
        </transition>
      </router-view>
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import { onMounted } from 'vue'
import { useUserDataStore } from '@/stores/userData'
import axios from '@/func/axios'
import { usePushNotice } from '@/composables/utility'

const userDataStore = useUserDataStore()
const { pushNotice } = usePushNotice()

// package.json の version からビルド時に注入
const version = __APP_VERSION__

onMounted(async () => {
  // axiosインターセプター設定
  axios.interceptors.response.use(
    response => {
      return response
    },
    error => {
      if (!error.response) {
        throw error
      }
      const status = error.response.status
      if (status === 401) {
        if (userDataStore.isAuthed) {
          pushNotice('認証エラーが発生したためログアウトします', 'error')
          userDataStore.authenticaitonFail()
          location.reload()
        }
        return false
      }
      throw error
    }
  )

  // バージョンチェック
  try {
    const res = await axios.get('/api/version')
    if (version !== res.data.version) {
      if (localStorage.apiVersion === res.data.version) {
        pushNotice('クライアントとAPIでバージョン齟齬があります', 'error')
        return
      }
      pushNotice(res.data.version + 'にバージョンアップを行います', 'info')
      localStorage.apiVersion = res.data.version
      setTimeout(() => {
        location.reload()
      }, 3000)
    }
  } catch {
    console.error('バージョンチェックエラー')
  }
})
</script>

<style lang="scss">
html {
  -webkit-touch-callout: none;
  scrollbar-width: none;
}
.selectable {
  -webkit-touch-callout: text;
}
html::-webkit-scrollbar {
  display: none;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>
