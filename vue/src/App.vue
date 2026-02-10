<template>
  <v-app>
    <!-- 通知 -->
    <notifications position="top right" width="290px" class="pt-14" style="pointer-events: none; z-index: 999;">
      <template #body="props">
        <v-alert
          :type="props.item.type"
          class="text-caption ma-1"
          density="compact"
          border="start"
          variant="text"
          style="background-color: white; pointer-events: auto;"
        >
          <v-alert-title class="text-subtitle-2">
            {{ props.item.title }}
          </v-alert-title>
          {{ props.item.text }}
        </v-alert>
      </template>
    </notifications>
    <!-- ルーター -->
    <router-view v-slot="{ Component }">
      <transition name="fade">
        <component :is="Component" />
      </transition>
    </router-view>
  </v-app>
</template>

<script lang="ts" setup>
import { onMounted } from 'vue'
import { apiClient } from '@/func/client'
import { usePushNotice } from '@/composables/utility'
import { useAppStore } from '@/stores/app'

const { pushNotice } = usePushNotice()
const appStore = useAppStore()

// package.json の version からビルド時に注入
const version = __APP_VERSION__

onMounted(async () => {
  // バージョンチェック
  try {
    const { data, error } = await apiClient.GET('/api/version')
    if (error) throw error
    if (data) {
      // APIバージョンをストアに保存
      appStore.setApiVersion(data.version)

      if (version !== data.version) {
        if (localStorage.apiVersion === data.version) {
          pushNotice('クライアントとAPIでバージョン齟齬があります', 'error')
          return
        }
        pushNotice(data.version + 'にバージョンアップを行います', 'info')
        localStorage.apiVersion = data.version
        setTimeout(() => {
          location.reload()
        }, 3000)
      }
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
