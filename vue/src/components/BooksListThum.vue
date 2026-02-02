<template>
  <v-row>
    <v-col
      v-for="item in booksList"
      :id="item.uuid"
      :key="item.uuid"
      cols="4"
      xs="4"
      sm="3"
      md="2"
      lg="1"
      class="pt-5"
    >
      <v-card @click="$emit('toReaderPage', item)">
        <div class="text-center" style="position: absolute; z-index: 1; top: -15px">
          <v-icon :color="getBadge(item)" size="small">
            mdi-circle
          </v-icon>
        </div>
        <v-img
          aspect-ratio="0.7"
          :src="getCoverURL(item.uuid)"
          @contextmenu.prevent="$emit('openMenu', item)"
        />
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useReaderStateStore } from '@/stores/readerState'
import { useGetCoverURL } from '@/composables/utility'
import type { components } from '@/api'

type BookBase = components['schemas']['BookBase']

const readerStateStore = useReaderStateStore()
const { getCoverURL } = useGetCoverURL()

defineEmits<{
  toReaderPage: [item: BookBase]
  openMenu: [item: BookBase]
}>()

const booksList = computed(() => readerStateStore.booksList)

const getBadge = (item: BookBase): string => {
  if (item.userData.openPage !== null) {
    return 'rgba(245,175,44,0.7)'
  } else if (item.userData.readTimes === null) {
    return 'rgba(81, 221, 30, 0.45)'
  } else {
    return 'gray'
  }
}
</script>
