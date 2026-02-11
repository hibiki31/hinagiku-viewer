<template>
  <v-list-item
    class="px-2 py-3"
    prepend-icon="mdi-book-open-variant"
    title="Hinagiku Viewer"
  >
    <template #prepend>
      <v-icon color="primary" size="x-large">
        mdi-book-open-variant
      </v-icon>
    </template>
    <template #subtitle>
      <div class="text-caption">
        <div>WEB: v{{ version }}</div>
        <div v-if="appStore.apiVersion">API: v{{ appStore.apiVersion }}</div>
      </div>
    </template>
  </v-list-item>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const version = __APP_VERSION__
</script>
