<template>
  <div class="booksList">
    <v-app-bar color="primary" dark dense flat app clipped-left>
      <v-app-bar-nav-icon @click="showDrawer = !showDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title></v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field v-model="queryTitle" hide-details single-line></v-text-field>
      <v-btn icon @click="$refs.searchDialog.openDialog()"><v-icon>mdi-magnify</v-icon></v-btn>
      <v-btn icon @click="reload()"><v-icon>mdi-reload</v-icon></v-btn>
    </v-app-bar>
    <!-- ドロワー -->
    <v-navigation-drawer v-model="showDrawer" app clipped>
      <v-list nav dense>
        <v-list-item-group>
          <v-select :items="libraryList" label="Library" v-model="queryLibrary" item-text="name" item-value="id" dense
            class="pr-2 pl-2 pt-3"></v-select>
        </v-list-item-group>
      </v-list>

      <!-- 評価するところ -->
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group>
          <v-rating v-model="queryRate" small></v-rating>
        </v-list-item-group>
        <v-list-item-group>
          <v-btn small color="primary" dark @click="queryRate = null" class="ma-1" width="70">
            All Rate
          </v-btn>
          <v-btn small color="gray" dark @click="queryRate = 0" class="ma-1" width="70">
            No Rate
          </v-btn>
        </v-list-item-group>
      </v-list>
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group>
          <v-btn class="ma-1" small color="error" @click="exportDialog = true" disabled>Range Export<v-icon
              class="pl-1">mdi-export</v-icon></v-btn>
          <v-btn class="ma-1" small color="primary" @click="$refs.rangeChangeDialog.openDialog()">Range
            Change<v-icon>mdi-pen</v-icon></v-btn>
          <v-btn class="ma-1" small @click="loadLibrary">
            Load Library<v-icon class="pl-2">mdi-book-refresh</v-icon>
          </v-btn>
          <v-btn class="ma-1" small @click="toDuplicateView">
            Duplicate List<v-icon class="pl-2">mdi-content-duplicate</v-icon>
          </v-btn>
        </v-list-item-group>
      </v-list>
      <v-divider></v-divider>
      <v-switch @change="$store.dispatch('setShowListMode', $event)" class="ma-3" label="リスト表示" dense
        hide-details></v-switch>
      <!-- ライセンス -->
      <v-divider class="pb-2"></v-divider>
      <span class="subtitle-2 ml-3">Develop by
        <a href="https://github.com/hibiki31" class="blue--text">@hibiki31</a></span>
      <span class="subtitle-2 ml-3">v{{ this.version }}</span>
      <div class="subtitle-2 ml-3">
        Icons made by
        <a href="https://www.flaticon.com/authors/icon-pond" title="Icon Pond" class="blue--text">Icon Pond</a>
      </div>
    </v-navigation-drawer>
    <v-progress-linear indeterminate color="yellow darken-2" v-show="isLoading"></v-progress-linear>
    <!-- メインの一覧 -->
    <v-container v-show="!isLoading">
      <BooksListTable v-if="showListMode" @toReaderPage="toReaderPage" @openMenu="openMenu" @search="search" />
    </v-container>
    <v-pagination v-model="page" :length="maxPage" :total-visible="17" class="ma-3"></v-pagination>
  </div>
</template>


<script lang="ts" setup>
import client from '../func/client'
import router from '../router'

const res = client.GET("/api/books")
console.log(res)
</script>
