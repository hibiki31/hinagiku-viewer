<template>
  <v-list nav density="comfortable">
    <v-list-item
      prepend-icon="mdi-logout"
      title="ログアウト"
      base-color="error"
      @click="handleLogout"
    />
  </v-list>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useUserDataStore } from '@/stores/userData'
import { usePushNotice } from '@/composables/utility'

const router = useRouter()
const userDataStore = useUserDataStore()
const { pushNotice } = usePushNotice()

const handleLogout = () => {
  userDataStore.logout()
  pushNotice('ログアウトしました', 'success')
  router.push('/login')
}
</script>
