<template>
    <v-dialog width="320" v-model="dialogState">
        <v-card>
            <v-card-title>編集</v-card-title>
            <v-card-text>
                <v-text-field
                    spellcheck="false"
                    label="名前"
                    placeholder=" "
                    v-model="item.name"
                ></v-text-field>
                <v-text-field
                    spellcheck="false"
                    label="コード"
                    placeholder=" "
                    v-model="item.code"
                ></v-text-field>
                <v-row>
                    <v-color-picker
                    v-model="item.color"
                    show-swatches
                    mode="hexa"
                    hide-mode-switch
                    ></v-color-picker>
                </v-row>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="runMethod()">更新</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index'

export default {
  data: function () {
    return {
      dialogState: false,
      item: {
        id: '',
        name: '',
        color: '',
        code: ''
      }
    }
  },
  methods: {
    openDialog (item = {}) {
      this.item = item
      this.dialogState = true
    },
    submitDialog () {
      axios
        .put('/api/category/big', this.item)
        .then((res) => {
          if (res.status !== 200) {
            this.$_pushNotice('処理に失敗しました', 'error')
            return
          }
          this.$_pushNotice('成功しました', 'success')
        })
        .catch(async () => {
          this.$_pushNotice('サーバーエラーが発生しました', 'error')
        })
      this.dialogState = false
    }
  }
}
</script>
