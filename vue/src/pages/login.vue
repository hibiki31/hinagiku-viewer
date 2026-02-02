<template>
  <div class="Login">
    <SetupDialog ref="setupDialogRef" />
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card v-if="userDataStore.isLoaded" flat>
            <v-card-text class="text-center">
              <div class="text-body-1 mb-3">Now loading...</div>
              <v-progress-circular indeterminate color="primary" />
            </v-card-text>
          </v-card>
          <v-card v-else class="elevation-12">
            <v-toolbar color="primary" dark>
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-form ref="formRef" v-model="isFormValid">
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
                  @click="openSetupDialog"
                  variant="text"
                  color="secondary"
                >Setup</v-btn>
                <v-btn
                  @click.prevent="doLogin"
                  :disabled="!isFormValid"
                  :loading="isLoadingLogin"
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

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserDataStore } from '@/stores/userData'
import axios from '@/func/axios'
import { usePushNotice } from '@/composables/utility'
import SetupDialog from '@/components/dialog/SetupDialog.vue'

const router = useRouter()
const userDataStore = useUserDataStore()
const { pushNotice } = usePushNotice()

const setupDialogRef = ref<InstanceType<typeof SetupDialog> | null>(null)
const formRef = ref()
const isFormValid = ref(false)
const isLoadingLogin = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  required: (v: any) => !!v?.length || 'Required'
}

const openSetupDialog = () => {
  setupDialogRef.value?.openDialog()
}

const doLogin = async () => {
  isLoadingLogin.value = true
  const loginFormData = new FormData()
  loginFormData.append('username', loginForm.username)
  loginFormData.append('password', loginForm.password)

  try {
    const res = await axios.post('/api/auth', loginFormData)
    if (res.status === 200) {
      pushNotice('ログイン成功', 'success')
      const accessToken = res.data.access_token
      userDataStore.authenticaitonSuccessful(accessToken)
      router.push('/')
    } else {
      pushNotice('エラーが発生しました', 'error')
    }
  } catch (error: any) {
    if (error.response?.status === 401) {
      pushNotice('ユーザ名またはパスワードが違います', 'error')
    } else {
      pushNotice('サーバエラーが発生しました', 'error')
    }
  } finally {
    isLoadingLogin.value = false
  }
}
</script>

<style lang="scss" scoped>
.Login {
  > * {
    margin: auto;
  }
}
</style>
