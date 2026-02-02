<template>
  <v-dialog v-model="dialogState" max-width="600">
    <v-card>
      <v-card-title>検索</v-card-title>
      <v-card-text>
        <v-text-field
          spellcheck="false"
          label="タイトル"
          placeholder=" "
          v-model="searchQuery.titleLike"
        ></v-text-field>
        <v-text-field
          spellcheck="false"
          label="あいまい検索"
          placeholder=" "
          v-model="searchQuery.fullText"
        ></v-text-field>
        <v-row>
          <v-col cols="12" sm="6" md="4">
            <v-rating
              v-if="searchQuery.rate !== null"
              v-model="searchQuery.rate"
              size="small"
            ></v-rating>
            <v-rating
              v-else
              color="yellow-accent-4"
              v-model="searchQuery.rate"
              size="small"
            ></v-rating>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-btn size="small" color="primary" class="ma-1" @click="searchQuery.rate = null">
              All Rate
            </v-btn>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-btn size="small" color="grey" @click="searchQuery.rate = 0" class="ma-1">
              No Rate
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn color="error" variant="text" @click="dialogState = false">閉じる</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="primary" variant="text" @click="submitDialog()">検索</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useReaderStateStore } from '@/stores/readerState'

const readerStateStore = useReaderStateStore()

const emit = defineEmits<{
  search: []
}>()

const dialogState = ref(false)
const searchQuery = reactive({ ...readerStateStore.searchQuery })

const openDialog = () => {
  Object.assign(searchQuery, readerStateStore.searchQuery)
  dialogState.value = true
}

const submitDialog = async () => {
  await readerStateStore.setSearchQuery({ ...searchQuery })
  emit('search')
  dialogState.value = false
}

defineExpose({
  openDialog
})
</script>
