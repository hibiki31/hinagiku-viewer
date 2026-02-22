<template>
  <!-- アプリバー -->
  <v-app-bar color="primary" density="compact" elevation="4" style="z-index: 1000">
    <v-app-bar-nav-icon @click="showDrawer = !showDrawer" />
    <v-toolbar-title class="text-body-1 font-weight-bold">
      {{ pageTitle }}
    </v-toolbar-title>
    <v-spacer />
    <!-- ページ固有アクション（各ページからTeleportで注入される） -->
    <div id="appbar-actions" class="d-flex align-center" />
  </v-app-bar>

  <!-- サイドバー -->
  <v-navigation-drawer v-model="showDrawer">
    <!-- ヘッダー -->
    <AppSidebarHeader />

    <v-divider />

    <!-- ページ固有サイドバーコンテンツ（各ページからTeleportで注入される） -->
    <div id="sidebar-extra-content" />

    <!-- メインナビゲーション -->
    <v-list nav density="comfortable">
      <v-list-subheader>メインメニュー</v-list-subheader>

      <v-list-item
        prepend-icon="mdi-bookshelf"
        title="書籍一覧"
        :active="route.path === '/'"
        color="primary"
        rounded="lg"
        @click="navigateTo('/')"
      />

      <v-list-item
        prepend-icon="mdi-content-duplicate"
        title="重複リスト"
        :active="route.path === '/duplicate'"
        color="primary"
        rounded="lg"
        @click="navigateTo('/duplicate')"
      />

      <v-list-item
        v-if="userDataStore.isAdmin"
        prepend-icon="mdi-progress-clock"
        title="タスク実行状況"
        :active="route.path === '/tasks'"
        color="primary"
        rounded="lg"
        @click="navigateTo('/tasks')"
      />

      <v-list-item
        v-if="userDataStore.isAdmin"
        prepend-icon="mdi-cog"
        title="システム設定"
        :active="route.path === '/settings'"
        color="primary"
        rounded="lg"
        @click="navigateTo('/settings')"
      />
    </v-list>

    <v-divider />

    <!-- ログアウト -->
    <AppLogoutListItem />

    <!-- フッター情報 -->
    <template #append>
      <v-divider />
      <AppSidebarFooter />
    </template>
  </v-navigation-drawer>

  <!-- メインコンテンツ -->
  <router-view />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserDataStore } from '@/stores/userData'
import AppSidebarHeader from '@/components/sidebar/AppSidebarHeader.vue'
import AppSidebarFooter from '@/components/sidebar/AppSidebarFooter.vue'
import AppLogoutListItem from '@/components/sidebar/AppLogoutListItem.vue'

const route = useRoute()
const router = useRouter()
const userDataStore = useUserDataStore()

const showDrawer = ref(true)

// ルートパスからページタイトルを解決
const pageTitle = computed(() => {
  const titleMap: Record<string, string> = {
    '/': '書籍一覧',
    '/duplicate': '重複リスト',
    '/tasks': 'タスク実行状況',
    '/settings': 'システム設定',
  }
  return titleMap[route.path] ?? ''
})

const navigateTo = (path: string) => {
  router.push(path)
}
</script>
