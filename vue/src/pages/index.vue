<template>
  <div class="booksList">
    <!-- 前回の続きを開くか確認するダイアログ -->
    <v-dialog v-model="resumeDialog" max-width="450" persistent>
      <v-card>
        <v-card-title class="text-h6"> 読書を再開しますか？ </v-card-title>
        <v-card-text>
          前回読んでいた本があります。続きから開きますか？
          <div class="text-body-2 text-grey mt-2">
            ページ: {{ resumeBookPage }}
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="dismissResume"> 開かない </v-btn>
          <v-btn color="primary" variant="flat" @click="acceptResume">
            続きから開く
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <SearchDialog ref="searchDialogRef" @search="search" />
    <UnifiedBookInfoDialog
      ref="unifiedBookInfoDialogRef"
      @search="search"
      @open-book="toReaderPage"
      @author-click="handleAuthorClick"
    />
    <RangeChangeDialog ref="rangeChangeDialogRef" @search="search" />
    <!-- トップバー -->
    <v-app-bar color="primary" dark density="compact" elevation="4" style="z-index: 1000">
      <v-app-bar-nav-icon @click="showDrawer = !showDrawer" />
      <v-toolbar-title />
      <v-spacer />
      <v-text-field
        v-model="queryTitle"
        hide-details
        single-line
        variant="underlined"
        density="compact"
      />
      <v-btn icon @click="searchDialogRef?.openDialog()">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>
      <v-btn icon @click="reload()">
        <v-icon>mdi-reload</v-icon>
      </v-btn>
    </v-app-bar>
    <!-- ドロワー -->
    <v-navigation-drawer v-model="showDrawer">
      <!-- ヘッダー -->
      <v-list-item
        class="px-2 py-3"
        prepend-icon="mdi-book-open-variant"
        title="Hinagiku Viewer"
        :subtitle="`v${version}`"
      >
        <template #prepend>
          <v-icon color="primary" size="x-large">
            mdi-book-open-variant
          </v-icon>
        </template>
      </v-list-item>

      <v-divider />

      <!-- ライブラリ選択 -->
      <div class="px-4 pt-4 pb-2">
        <v-select
          v-model="queryLibrary"
          :items="libraryList"
          label="ライブラリ"
          item-title="name"
          item-value="id"
          density="comfortable"
          prepend-inner-icon="mdi-bookshelf"
          variant="outlined"
          hide-details
        />
      </div>

      <v-divider />

      <!-- 評価フィルター -->
      <v-list nav density="compact">
        <v-list-subheader>評価フィルター</v-list-subheader>
        <v-list-item>
          <div class="d-flex justify-center mb-2">
            <v-rating
              :model-value="queryRate ?? undefined"
              size="small"
              color="amber"
              active-color="amber"
              @update:model-value="(value) => (queryRate = value as number)"
            />
          </div>
          <v-btn-group
            divided
            density="compact"
            variant="outlined"
            class="w-100"
          >
            <v-btn
              :variant="queryRate === null ? 'flat' : 'outlined'"
              :color="queryRate === null ? 'primary' : undefined"
              size="small"
              @click="queryRate = null"
            >
              <v-icon start size="small"> mdi-format-list-bulleted </v-icon>
              全て
            </v-btn>
            <v-btn
              :variant="queryRate === 0 ? 'flat' : 'outlined'"
              :color="queryRate === 0 ? 'primary' : undefined"
              size="small"
              @click="queryRate = 0"
            >
              <v-icon start size="small"> mdi-star-off-outline </v-icon>
              未評価
            </v-btn>
          </v-btn-group>
        </v-list-item>
      </v-list>

      <v-divider />

      <!-- 操作メニュー -->
      <v-list nav density="comfortable">
        <v-list-subheader>操作</v-list-subheader>

        <v-list-item
          prepend-icon="mdi-export"
          title="範囲エクスポート"
          disabled
          @click="exportDialog = true"
        />

        <v-list-item
          prepend-icon="mdi-pencil"
          title="範囲変更"
          @click="rangeChangeDialogRef?.openDialog()"
        />

        <v-list-item
          prepend-icon="mdi-book-refresh"
          title="ライブラリ再読込"
          @click="loadLibrary"
        />

        <v-list-item
          prepend-icon="mdi-content-duplicate"
          title="重複リスト"
          @click="toDuplicateView"
        />
      </v-list>

      <v-divider />

      <!-- 表示設定 -->
      <v-list nav density="comfortable">
        <v-list-subheader>表示設定</v-list-subheader>
        <v-list-item>
          <v-switch
            :model-value="showListMode"
            label="リスト表示"
            color="primary"
            density="comfortable"
            hide-details
            @update:model-value="
              (value) => readerStateStore.setShowListMode(!!value)
            "
          >
            <template #prepend>
              <v-icon>{{
                showListMode ? "mdi-view-list" : "mdi-view-grid"
              }}</v-icon>
            </template>
          </v-switch>
        </v-list-item>

        <!-- ソートキー選択 -->
        <div class="pr-2 pl-2">
          <v-select
            v-model="querySortKey"
            :items="sortKeyOptions"
            label="ソートキー"
            item-title="title"
            item-value="value"
            density="comfortable"
            prepend-inner-icon="mdi-sort"
            variant="outlined"
            hide-details
            clearable
          />
        </div>

        <!-- ソート順序 -->
        <v-list-item>
          <v-btn-group
            divided
            density="compact"
            variant="outlined"
            class="w-100"
          >
            <v-btn
              :variant="querySortDesc === false ? 'flat' : 'outlined'"
              :color="querySortDesc === false ? 'primary' : undefined"
              size="small"
              @click="querySortDesc = false"
            >
              <v-icon start size="small"> mdi-sort-ascending </v-icon>
              昇順
            </v-btn>
            <v-btn
              :variant="querySortDesc === true ? 'flat' : 'outlined'"
              :color="querySortDesc === true ? 'primary' : undefined"
              size="small"
              @click="querySortDesc = true"
            >
              <v-icon start size="small"> mdi-sort-descending </v-icon>
              降順
            </v-btn>
          </v-btn-group>
        </v-list-item>
      </v-list>

      <v-divider />

      <!-- ログアウト -->
      <v-list nav density="comfortable">
        <v-list-item
          prepend-icon="mdi-logout"
          title="ログアウト"
          base-color="error"
          @click="handleLogout"
        />
      </v-list>

      <!-- フッター情報 -->
      <template #append>
        <v-divider />
        <v-list density="compact" class="py-2">
          <v-list-item density="compact" class="text-caption">
            <div class="text-center">
              Develop by
              <a
                href="https://github.com/hibiki31"
                class="text-primary text-decoration-none"
                target="_blank"
              >
                @hibiki31
              </a>
            </div>
          </v-list-item>
          <v-list-item density="compact" class="text-caption">
            <div class="text-center">
              Icons made by
              <a
                href="https://www.flaticon.com/authors/icon-pond"
                title="Icon Pond"
                class="text-primary text-decoration-none"
                target="_blank"
              >
                Icon Pond
              </a>
            </div>
          </v-list-item>
        </v-list>
      </template>
    </v-navigation-drawer>
    <!-- メインコンテンツ -->
    <v-main>
      <v-progress-linear
        v-show="isLoading"
        indeterminate
        color="yellow-darken-2"
      />
      <!-- メインの一覧 -->
      <v-container v-show="!isLoading" max-width="1900px">
        <BooksListTable
          v-if="showListMode"
          @to-reader-page="toReaderPage"
          @open-menu="openMenu"
          @search="search"
        />
        <BooksListThum
          v-else
          @to-reader-page="toReaderPage"
          @open-menu="openMenu"
          @open-in-new-tab="openInNewTab"
        />
      </v-container>
      <v-pagination
        v-model="page"
        :length="maxPage"
        :total-visible="17"
        class="ma-3"
      />
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useReaderStateStore } from "@/stores/readerState";
import { useUserDataStore } from "@/stores/userData";
import { apiClient } from "@/func/client";
import { usePushNotice } from "@/composables/utility";
import { useTitle } from "@/composables/title";
import SearchDialog from "@/components/dialog/SearchDialog.vue";
import UnifiedBookInfoDialog from "@/components/dialog/UnifiedBookInfoDialog.vue";
import RangeChangeDialog from "@/components/dialog/RangeChangeDialog.vue";
import BooksListTable from "@/components/BooksListTable.vue";
import BooksListThum from "@/components/BooksListThum.vue";
import type { components } from "@/api";

// ページタイトル設定
useTitle("ホーム");

type GetLibrary = components["schemas"]["GetLibrary"];
type BookBase = components["schemas"]["BookBase"];

const router = useRouter();
const readerStateStore = useReaderStateStore();
const userDataStore = useUserDataStore();
const { pushNotice } = usePushNotice();

const searchDialogRef = ref();
const unifiedBookInfoDialogRef = ref();
const rangeChangeDialogRef = ref();

const showDrawer = ref(true);
const isLoading = ref(true);
const exportDialog = ref(false);
const libraryList = ref<GetLibrary[]>([]);
const version = __APP_VERSION__;

// 前回の続きを開くか確認するダイアログ
const resumeDialog = ref(false);
const resumeBookUUID = ref("");
const resumeBookPage = ref(0);

// ソートキーのオプション
const sortKeyOptions = [
  { title: "タイトル", value: "title" },
  { title: "追加日", value: "addDate" },
  { title: "最終閲覧日", value: "userData.lastOpenDate" },
  { title: "評価", value: "userData.rate" },
  { title: "ページ数", value: "page" },
  { title: "サイズ", value: "size" },
];

const searchQuery = computed(() => readerStateStore.searchQuery);
const booksCount = computed(() => readerStateStore.booksCount);
const showListMode = computed(() => readerStateStore.showListMode);
const maxPage = computed(() =>
  Math.ceil(booksCount.value / searchQuery.value.limit),
);

const page = computed({
  get() {
    return Number(searchQuery.value.offset / searchQuery.value.limit) + 1;
  },
  set(value: number) {
    const query = { ...searchQuery.value };
    query.offset = query.limit * (value - 1);
    readerStateStore.setSearchQuery(query);
    search(false);
  },
});

const queryTitle = computed({
  get() {
    return searchQuery.value.fullText;
  },
  set(value: string) {
    const query = { ...searchQuery.value };
    query.fullText = value;
    readerStateStore.setSearchQuery(query);
    search(true);
  },
});

const queryLibrary = computed({
  get() {
    return searchQuery.value.libraryId;
  },
  set(value: number | null) {
    const query = { ...searchQuery.value };
    query.libraryId = value;
    readerStateStore.setSearchQuery(query);
    search(true);
  },
});

const queryRate = computed({
  get() {
    return searchQuery.value.rate;
  },
  set(value: number | null) {
    const query = { ...searchQuery.value };
    query.rate = value;
    readerStateStore.setSearchQuery(query);
    search(true);
  },
});

const querySortKey = computed({
  get() {
    return searchQuery.value.sortKey;
  },
  set(value: string | undefined) {
    const query = { ...searchQuery.value };
    query.sortKey = value;
    readerStateStore.setSearchQuery(query);
    search(true);
  },
});

const querySortDesc = computed({
  get() {
    return searchQuery.value.sortDesc ?? false;
  },
  set(value: boolean) {
    const query = { ...searchQuery.value };
    query.sortDesc = value;
    readerStateStore.setSearchQuery(query);
    search(true);
  },
});

const search = async (resetOffset = false) => {
  isLoading.value = true;
  await readerStateStore.serachBooks(resetOffset);
  pushNotice(booksCount.value + "件", "info");
  isLoading.value = false;
  scrollToUUID();
};

const reload = () => {
  const query = { ...searchQuery.value };
  query.fullText = "";
  readerStateStore.setSearchQuery(query);
  search(true);
};

const scrollToUUID = () => {
  setTimeout(() => {
    const backBookUUID = localStorage.backBookUUID;
    if (backBookUUID) {
      const element = document.getElementById(backBookUUID);
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }
    localStorage.removeItem("backBookUUID");
  }, 300);
};

const loadLibrary = async () => {
  try {
    const { error } = await apiClient.PATCH("/media/library", {
      body: { state: "load" },
    });
    if (error) throw error;
    pushNotice("ライブラリのリロードを開始", "success");
  } catch {
    pushNotice("ライブラリのリロードに失敗しました", "error");
  }
};

const openMenu = (item: BookBase) => {
  unifiedBookInfoDialogRef.value?.openDialog(item);
};

const handleAuthorClick = (author: {
  id: number | null;
  name: string | null;
}) => {
  const query = { ...searchQuery.value };
  query.fullText = author.name || "";
  readerStateStore.setSearchQuery(query);
  search(true);
};

const toReaderPage = async (item: BookBase) => {
  // ローカルストレージにパラメータ格納
  createCache(item);
  localStorage.setItem("searchQuery", JSON.stringify(searchQuery.value));
  localStorage.setItem("backBookUUID", item.uuid);

  // 移動
  router.push(`/books/${item.uuid}`);
};

const openInNewTab = (item: BookBase) => {
  // キャッシュの作成をリクエスト
  createCache(item);

  // 別タブで本を開く
  const url = router.resolve(`/books/${item.uuid}`).href;
  window.open(url, "_blank");
};

const createCache = (book: BookBase) => {
  pushNotice("キャッシュの作成をリクエスト", "info");
  apiClient.PATCH("/media/books", {
    body: {
      uuid: book.uuid,
      height: Math.round(window.innerHeight * window.devicePixelRatio),
    },
  });
};

const toDuplicateView = () => {
  router.push("/duplicate");
};

// ログアウト処理
const handleLogout = () => {
  userDataStore.logout();
  pushNotice("ログアウトしました", "success");
  router.push("/login");
};

// 前回の続きを開くダイアログのハンドラー
const acceptResume = () => {
  resumeDialog.value = false;
  router.push(
    `/books/${resumeBookUUID.value}?startPage=${resumeBookPage.value}`,
  );
};

const dismissResume = () => {
  resumeDialog.value = false;
  localStorage.removeItem("openBookUUID");
  localStorage.removeItem("openBookPage");
};

const initLibraryAndSearch = async () => {
  // ライブラリ情報取得
  try {
    const { data, error } = await apiClient.GET("/api/librarys");
    if (error) throw error;
    if (data) {
      libraryList.value = data;
    }
  } catch (error) {
    console.error("ライブラリ情報取得エラー:", error);
  }

  // 初期ロード
  search();
};

onMounted(async () => {
  // 前回開いていた本を取得
  const uuid = localStorage.openBookUUID;
  const openPage = localStorage.openBookPage;
  // 前回開いていた本が取得できたらダイアログで確認
  if (uuid && openPage) {
    resumeBookUUID.value = uuid;
    resumeBookPage.value = Number(openPage);
    resumeDialog.value = true;
  } else {
    localStorage.removeItem("openBookUUID");
    localStorage.removeItem("openBookPage");
  }

  await initLibraryAndSearch();
});
</script>
