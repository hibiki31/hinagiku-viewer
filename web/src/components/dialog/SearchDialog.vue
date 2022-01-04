<template>
  <v-dialog v-model="dialogState">
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
              <v-rating v-if="searchQuery.rate !== null" v-model="searchQuery.rate" small></v-rating>
              <v-rating v-else color="yellow accent-4" v-model="searchQuery.rate" small ></v-rating>
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-btn
                small
                color="primary"
                dark
                class="ma-1"
                @click="searchQuery.rate = null">
                All Rate
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-btn small color="gray" dark @click="searchQuery.rate = 0" class="ma-1">
                No Rate
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
            <v-btn color="error" text @click="dialogState = false">閉じる</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="primary" text @click="submitDialog()">検索</v-btn>
        </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>

export default {
  data: function () {
    return {
      dialogState: false,
      searchQuery: {},
      topBerQuery: null
    }
  },
  methods: {
    openDialog () {
      this.dialogState = true
      this.searchQuery = this.$store.getters.searchQuery
    },
    async submitDialog () {
      await this.$store.dispatch('serachBooks', this.searchQuery)
    }
  }
}
</script>
