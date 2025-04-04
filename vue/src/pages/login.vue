<template>
  <div class="Login">
    <v-container class="fill-height" fluid v-if="auth.$state.tokenValidated && !auth.$state.authed">
      <v-row justify="center">
        <v-col cols="12" sm="8" md="4">
          <v-card>
            <v-toolbar color="primary" dark>
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-text-field v-model="username" label="userId" prepend-icon="mdi-account" required type="text"
                variant="underlined" density="compact" @keydown.enter="login">
              </v-text-field>

              <VTextField v-model="password" label="Password" prepend-icon="mdi-lock" required type="password"
                variant="underlined" density="compact" @keydown.enter="login" />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn depressed color="primary" type="submit" :loading="isLoadingLogin" @click="login">Login</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts" setup>
import api from '../func/axios'
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { sleep } from '../func/sleep'
import { useNotification } from '@kyvg/vue3-notification'
import { useAuthStore } from '../stores/auth'
import Cookies from 'js-cookie'
import client, {setToken} from '../func/client'

// module
const { notify } = useNotification()
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const password = ref('')
const username = ref('')
const isLoadingLogin = ref(false)
const accessToken = ref<string | undefined>(undefined)

const loadingLogin = async () => {
  await sleep(300)
  isLoadingLogin.value = false
}



const login = async () => {
  isLoadingLogin.value = true

  try {
    await loadingLogin()
    const res = await client.POST("/api/auth", {
      body: {
        scope: null,
        username: username.value,
        password: password.value
      },
      bodySerializer(body) {
        const fd = new FormData();
        for (const name in body) {
          fd.append(name, body[name]);
        }
        return fd;
      },
    })

    accessToken.value = res.data.access_token
  } catch (error) {
    await loadingLogin()
    notify({
      type: 'error',
      title: '認証失敗',
      text: 'ユーザ名またはパスワードが違います',
    })
    return error
  }

  notify({
    type: 'success',
    title: '認証成功',
    text: 'ホームへ遷移します',
  })
  if (accessToken.value) {
    await setToken(accessToken.value)
    await auth.loginSuccess(accessToken.value)
  }

  router.push((route.query.redirect as string | undefined) ?? '/')
}

const authAPI = () => {
  accessToken.value = Cookies.get('accessToken')

  if (!accessToken.value) {
    console.debug('token not found in cookie')
    auth.$state.tokenValidated = true
    return
  }

  api.get('/api/auth/validate', {
    headers: {
      Authorization: 'Bearer ' + accessToken.value,
    },
  }).then(() => {
    api.interceptors.request.use(
      (config) => {
        config.headers.Authorization = 'Bearer ' + accessToken.value
        return config
      },
      (err) => {
        return Promise.reject(err)
      },
    )
    notify({
      type: 'success',
      title: '認証成功',
      text: '認証情報が有効でした',
    })
    if (accessToken.value) {
      auth.loginSuccess(accessToken.value)
    }
    router.push((route.query.redirect as string | undefined) ?? '/')
  }).catch(() => {
    notify({
      type: 'error',
      title: '認証失敗',
      text: '認証情報が失効しました',
    })
    Cookies.remove('accessToken')
    auth.$state.tokenValidated = true
  })
}

onMounted(async () => {
  authAPI()
})
</script>