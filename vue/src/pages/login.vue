<template>
  <div class="Login">
    <SetupDialog ref="setupDialogRef" />
    <v-container class="fill-height" fluid>
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card v-if="userDataStore.isLoaded" flat>
            <v-card-text class="text-center">
              <div class="text-body-1 mb-3">
                Now loading...
              </div>
              <v-progress-circular indeterminate color="primary" />
            </v-card-text>
          </v-card>
          <v-card v-else class="elevation-12 mx-auto" max-width="500">
            <v-toolbar color="primary" dark>
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer />
            </v-toolbar>
            <v-form ref="formRef" v-model="isFormValid">
              <v-card-text>
                <v-text-field
                  v-model="loginForm.username"
                  :rules="[rules.required]"
                  label="userId"
                  name="userId"
                  variant="underlined"
                  prepend-icon="mdi-account"
                  required
                  type="text"
                />

                <v-text-field
                  id="password"
                  v-model="loginForm.password"
                  :rules="[rules.required]"
                  label="Password"
                  name="password"
                  variant="underlined"
                  prepend-icon="mdi-lock"
                  required
                  type="password"
                />
              </v-card-text>
              <v-card-actions>
                <v-spacer />
                <v-btn
                  variant="text"
                  color="secondary"
                  @click="openSetupDialog"
                >
                  Setup
                </v-btn>
                <v-btn
                  :disabled="!isFormValid"
                  :loading="isLoadingLogin"
                  color="primary"
                  type="submit"
                  @click.prevent="doLogin"
                >
                  Login
                </v-btn>
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
import { apiClient } from '@/func/client'
import { usePushNotice } from '@/composables/utility'
import { useTitle } from '@/composables/title'
import SetupDialog from '@/components/dialog/SetupDialog.vue'

// ページタイトル設定
useTitle('ログイン')

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
  required: (v: unknown) => !!(v as string)?.length || 'Required'
}

const openSetupDialog = () => {
  setupDialogRef.value?.openDialog()
}

const doLogin = async () => {
  isLoadingLogin.value = true

  try {
    const { data, error } = await apiClient.POST('/api/auth', {
      body: {
        username: loginForm.username,
        password: loginForm.password,
        scope: '',
      },
      bodySerializer: (body) => {
        const params = new URLSearchParams()
        for (const [key, value] of Object.entries(body)) {
          if (value !== undefined && value !== null) {
            params.append(key, String(value))
          }
        }
        return params.toString()
      },
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    if (error) throw error
    if (data) {
      pushNotice('ログイン成功', 'success')
      const accessToken = data.access_token
      userDataStore.authenticaitonSuccessful(accessToken)
      router.push('/')
    }
  } catch (error: unknown) {
    const fetchError = error as { status?: number }
    if (fetchError.status === 401) {
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
