<template>
  <v-row>
    <v-col
      v-for="item in booksList"
      :key="item.uuid"
      :id="item.uuid"
      cols="4"
      xs="4"
      sm="3"
      md="2"
      lg="1"
      class="pt-5"
    >
      <v-card @click="$emit('toReaderPage', item)">
        <div class="text-center" style="position: absolute; z-index: 1; top: -15px">
          <v-icon :color="getBadge(item)" size="small">mdi-circle</v-icon>
        </div>
        <v-img
          aspect-ratio="0.7"
          :src="getCoverURL(item.uuid)"
          @contextmenu.prevent="$emit('openMenu', item)"
        ></v-img>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useReaderStateStore } from '@/stores/readerState'
import { useGetCoverURL } from '@/composables/utility'

const readerStateStore = useReaderStateStore()
const { getCoverURL } = useGetCoverURL()

defineEmits<{
  toReaderPage: [item: any]
  openMenu: [item: any]
}>()

const booksList = computed(() => readerStateStore.booksList)

const getBadge = (item: any): string => {
  if (item.userData.openPage !== null) {
    return 'rgba(245,175,44,0.7)'
  } else if (item.userData.readTimes === null) {
    return 'rgba(81, 221, 30, 0.45)'
  } else {
    return 'gray'
  }
}
</script>
