<template>
  <div>
    <v-data-table
      :headers="headers"
      :items="booksList"
      :items-per-page="searchQuery.limit"
      hide-default-footer
      density="compact"
    >
      <template #[`item.title`]="{ item }">
        <div>{{ item.title }}</div>
      </template>
      <template #[`item.publisher`]="{ item }">
        {{ item.publisher?.name }}
      </template>
      <template #[`item.actions`]="{ item }">
        <v-icon size="small" class="mr-2" @click="emit('toReaderPage', item)">
          mdi-book-open-blank-variant
        </v-icon>
        <v-icon size="small" class="mr-2" @click="emit('openMenu', item)">
          mdi-tooltip-edit-outline
        </v-icon>
      </template>
      <template #[`item.authors`]="{ item }">
        <BaseAuthorChip :open-book="item" @search="emit('search')" />
      </template>
      <template #[`item.size`]="{ item }">
        {{ fitByte(item.size) }}
      </template>
      <template #[`item.addDate`]="{ item }">
        {{ convertDateFormat(item.addDate) }}
      </template>
      <template #[`item.userData.rate`]="{ item }">
        {{ item.userData?.rate || '-' }}
      </template>
    </v-data-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useReaderStateStore } from '@/stores/readerState'
import { useFitByte, useConvertDateFormat } from '@/composables/utility'
import BaseAuthorChip from './BaseAuthorChip.vue'
import type { components } from '@/api'

type BookBase = components['schemas']['BookBase']

const readerStateStore = useReaderStateStore()
const { fitByte } = useFitByte()
const { convertDateFormat } = useConvertDateFormat()

const emit = defineEmits<{
  toReaderPage: [item: BookBase]
  openMenu: [item: BookBase]
  search: []
}>()

const headers = [
  { title: 'title', key: 'title' },
  { title: 'authors', key: 'authors', sortable: false },
  { title: 'publisher', key: 'publisher.name' },
  { title: 'rate', key: 'userData.rate', width: 60 },
  { title: 'addDate', key: 'addDate', width: 110 },
  { title: 'last', key: 'userData.lastOpenDate', width: 110 },
  { title: 'size', key: 'size', width: 80 },
  { title: 'page', key: 'page', width: 60 },
  { title: 'actions', key: 'actions', sortable: false, width: 100 }
]

const searchQuery = computed(() => readerStateStore.searchQuery)
const booksList = computed(() => readerStateStore.booksList)
</script>
