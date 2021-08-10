<template>
  <div class="Login">
    <setup-virty-dialog ref="setupVirtyDialog"/>
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card v-if="$store.state.userData.isLoaded" flat>
            <v-card-text class="text-center">
              <div class="body-1 mb-3">Now loading...</div>
              <v-progress-circular indeterminate color="primary" />
            </v-card-text>
          </v-card>
          <v-card v-else class="elevation-12">
            <v-toolbar color="primary" dark>
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-form ref="form" v-model="isFormValid">
              <v-card-text>
                <v-text-field
                  v-model="loginForm.username"
                  :rules="[rules.required]"
                  label="userId"
                  name="userId"
                  prepend-icon="mdi-account"
                  required
                  type="text"
                ></v-text-field>

                <v-text-field
                  v-model="loginForm.password"
                  :rules="[rules.required]"
                  id="password"
                  label="Password"
                  name="password"
                  prepend-icon="mdi-lock"
                  required
                  type="password"
                ></v-text-field>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  v-on:click="this.openSetupVirtyDialog"
                  depressed
                  text
                  color="secondary"
                >Setup</v-btn>
                <v-btn
                  @click.prevent="doLogin"
                  :disabled="!isFormValid"
                  :loading="isLoadingLogin"
                  depressed
                  color="primary"
                  type="submit"
                >Login</v-btn>
              </v-card-actions>
            </v-form>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style lang="scss">
.Login {
  > * {
    margin: auto;
  }
}
</style>

<script>
import axios from '@/axios/index'
import SetupVirtyDialog from '../components/dialog/SetupVirtyDialog.vue'

export default {
  name: 'Login',
  props: {
    source: String
  },
  components: {
    SetupVirtyDialog
  },
  data: () => ({
    isFormValid: false,
    isLoadingLogin: false,
    loginForm: {
      username: '',
      password: ''
    },
    rules: {
      required: (v) => !!v?.length
    }
  }),
  methods: {
    openSetupVirtyDialog () {
      this.$refs.setupVirtyDialog.openDialog()
    },
    async doLogio () {
      this.$store.dispatch('auth', this.loginForm.username, this.loginForm.password)
    },
    async doLogin () {
      this.isLoadingLogin = false
      const loginForm = new FormData()
      loginForm.append('username', this.loginForm.username)
      loginForm.append('password', this.loginForm.password)

      // トークン取得
      const accessToken = await axios
        .post('/api/auth', loginForm)
        .then(res => {
          if (res.status === 200) {
            this.$pushNotice('ログイン成功', 'success')
            return res.data.access_token
          } else {
            this.$pushNotice('エラーが発生しました', 'error')
            return false
          }
        })
        .catch(error => {
          if (error.response.status === 401) {
            this.$pushNotice('ユーザ名またはパスワードが違います', 'error')
          } else {
            this.$pushNotice('サーバエラーが発生しました', 'error')
          }
          return false
        })
      // トークン取得が取得できていたら格納
      if (accessToken) {
        this.$store.dispatch('authenticaitonSuccessful', accessToken)
        this.$router.push({
          name: 'BooksList'
        })
      }
      this.isLoadingLogin = false
    }
  }
}
</script>
