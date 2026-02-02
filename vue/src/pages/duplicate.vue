<template>
  <div class="duplicateList">
    <v-app-bar color="primary" dark density="compact" flat app>
      <v-app-bar-nav-icon @click="showDrawer = !showDrawer" />
      <v-toolbar-title />
      <v-spacer />
      <v-btn icon @click="reload()">
        <v-icon>mdi-reload</v-icon>
      </v-btn>
    </v-app-bar>
    <v-navigation-drawer v-model="showDrawer" app>
      <v-list nav density="compact">
        <v-list-item>
          <v-btn class="ma-1" size="small" @click="serachDuplicate">
            search<v-icon class="pl-2">
              mdi-content-duplicate
            </v-icon>
          </v-btn>
        </v-list-item>
        <v-list-item>
          <v-btn class="ma-1" size="small" @click="toBookList">
            BookList<v-icon class="pl-2">
              mdi-content
            </v-icon>
          </v-btn>
        </v-list-item>
      </v-list>
      <v-divider />
      <!-- ライセンス -->
      <v-divider class="pb-2" />
      <div class="text-subtitle-2 ml-3">
        Develop by
        <a href="https://github.com/hibiki31" class="text-blue">@hibiki31</a>
      </div>
      <div class="text-subtitle-2 ml-3">
        v{{ version }}
      </div>
      <div class="text-subtitle-2 ml-3">
        Icons made by
        <a href="https://www.flaticon.com/authors/icon-pond" title="Icon Pond" class="text-blue">Icon Pond</a>
      </div>
    </v-navigation-drawer>
    <v-progress-linear v-show="isLoading" indeterminate color="yellow-darken-2" />
    <v-container v-show="!isLoading">
      <div v-for="item in booksList" :id="item.duplicate_uuid" :key="item.duplicate_uuid" class="pb-5">
        {{ item.duplicate_uuid }}
        <v-row>
          <v-col
            v-for="item_book in item.books"
            :id="item_book.duplicate_uuid"
            :key="item_book.duplicate_uuid"
            xs="4"
            sm="3"
            md="3"
            lg="3"
            class="pt-5"
          >
            <v-card>
              <v-row>
                <v-col cols="4">
                  <v-img aspect-ratio="0.7" :src="getCoverURL(item_book.uuid)" />
                </v-col>
                <v-col cols="8">
                  {{ parseInt(String(item_book.size / 1024 / 1024), 10) }} MB 評価：{{
                    item_book.rate === null ? 'なし' : item_book.rate
                  }}
                  <div>{{ item_book.file }}</div>
                  <v-btn icon @click="deleteBook(item_book.uuid)">
                    <v-icon>mdi-delete-outline</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from '@/func/axios'
import { usePushNotice, useGetCoverURL } from '@/composables/utility'

interface DuplicateBook {
  duplicate_uuid: string
  books: {
    duplicate_uuid: string
    uuid: string
    size: number
    rate: number | null
    file: string
  }[]
}

const router = useRouter()
const { pushNotice } = usePushNotice()
const { getCoverURL } = useGetCoverURL()

const showDrawer = ref(true)
const isLoading = ref(true)
const version = '3.0.0'
const booksList = ref<DuplicateBook[]>([])

const serachDuplicate = async () => {
  try {
    const response = await axios.request({
      method: 'patch',
      url: '/media/library',
      data: { state: 'sim_all' }
    })
    pushNotice('重複の検索を開始' + response.data.status, 'success')
  } catch {
    pushNotice('重複の検索に失敗しました', 'error')
  }
}

const reload = async () => {
  try {
    const response = await axios.get('/media/books/duplicate')
    booksList.value = response.data
    isLoading.value = false
  } catch {
    pushNotice('データの読み込みに失敗しました', 'error')
    isLoading.value = false
  }
}

const deleteBook = async (uuid: string) => {
  try {
    const response = await axios.request({
      method: 'delete',
      url: '/api/books/' + uuid
    })
    pushNotice('削除しました' + response.data.status, 'success')
    reload()
  } catch {
    pushNotice('削除に失敗しました', 'error')
  }
}

const toBookList = () => {
  router.push('/')
}

onMounted(() => {
  reload()
})
</script>
