<template>
 <v-dialog width="400" v-model="dialogState">
      <v-card>
        <v-form ref="nodeAddForm">
          <v-card-title>Setup</v-card-title>
          <v-card-text>
            初期設定を行います。管理者ユーザが存在する場合実行できません。
            <v-text-field
              v-model="postData.id"
              label="Admin user name"
              :rules="[$_required, $_limitLength64, $_characterRestrictions, $_firstCharacterRestrictions]"
              counter="64"
            ></v-text-field>
            <v-text-field
              v-model="postData.password"
              :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
              :rules="[$_required]"
              :type="show1 ? 'text' : 'password'"
              name="input-10-1"
              label="Password"
              hint="At least 1 characters"
              counter
              @click:append="show1 = !show1"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" v-on:click="runMethod">Setup</v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
</template>

<script>
import axios from '@/axios/index'

export default {
  name: 'SetUpDialog',
  data: function () {
    return {
      postData: {
        id: '',
        password: ''
      },
      show1: false,
      dialogState: false
    }
  },
  methods: {
    openDialog () {
      this.dialogState = true
    },
    runMethod () {
      if (!this.$refs.nodeAddForm.validate()) {
        return
      }
      axios.request({
        method: 'post',
        url: '/api/auth/setup',
        data: this.postData
      })
        .then(res => {
          this.$_pushNotice('Success setup', 'success')
          this.dialogState = false
        })
        .catch(error => {
          this.$_pushNotice(error.response.data.detail, 'error')
        })
    }
  }
}
</script>
