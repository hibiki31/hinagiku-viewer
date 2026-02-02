<template>
  <v-app>
    <!-- 通知 -->
    <notifications position="top right" width="400px">
      <template #body="props">
        <v-alert
          :type="props.item.type"
          class="ma-3 mb-0"
          border="start"
          variant="tonal"
        >
          <div class="d-flex align-center ml-3">
            <div class="text-body-2 mr-auto">{{ props.item.text }}</div>
          </div>
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
import { useRouter } from 'vue-router'
import { useUserDataStore } from '@/stores/userData'
import axios from '@/func/axios'
import Cookies from 'js-cookie'
import { usePushNotice } from '@/composables/utility'

const router = useRouter()
const userDataStore = useUserDataStore()
const { pushNotice } = usePushNotice()

// package.jsonからバージョン取得（実際にはハードコード）
const version = '3.0.0'

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

  // トークン取得
  const accessToken = Cookies.get('accessToken')

  if (accessToken) {
    try {
      await axios.get('/api/auth/validate', {
        headers: {
          Authorization: `Bearer ${accessToken}`
        }
      })
      userDataStore.authenticaitonSuccessful(accessToken)
      if (router.currentRoute.value.path === '/login') {
        router.push('/')
      }
    } catch (error) {
      userDataStore.authenticaitonFail()
    }
  } else {
    userDataStore.authenticaitonFail()
  }

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
  } catch (error) {
    console.error('バージョンチェックエラー:', error)
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
