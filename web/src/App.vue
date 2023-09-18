<template>
  <v-app>
    <!-- 通知 -->
    <notifications group="default" animation-type="velocity" position="top right" class="mt-14">
      <template slot="body" slot-scope="props">
        <v-alert
          :type="props.item.type"
          class="ma-3 mb-0"
          border="left"
          colored-border
        >
          <div class="d-flex align-center ml-3">
            <div class="body-2 mr-auto">{{ props.item.text }}</div>
          </div>
        </v-alert>
      </template>
    </notifications>
    <!-- メイン -->
    <v-main>
      <transition name="fade">
      <router-view />
      </transition>
    </v-main>
  </v-app>
</template>

<script>
import store from './store'
import axios from './axios/index'
import router from './router'
import Cookies from 'js-cookie'

export default {
  name: 'App',
  data: () => ({
    version: require('../package.json').version,
    userId: ''
  }),
  mounted: async function () {
    axios.interceptors.response.use(response => {
      return response
    }, error => {
      if (!error.response) {
        // それぞれの.catchに引継ぎ
        throw error
      }
      const status = error.response.status
      if (status === 401) {
        if (store.state.userData.isAuthed) {
          this.$_pushNotice('認証エラーが発生したためログアウトします', 'error')
          store.dispatch('authenticaitonFail')
          location.reload(true)
        }
        // .catch無効
        return false
      }
      // それぞれの.catchに引継ぎ
      throw error
    })
    // トークン取得
    const accessToken = Cookies.get('accessToken')

    if (accessToken) {
      await axios
        .get('/api/auth/validate', {
          headers: {
            Authorization: `Bearer ${accessToken}`
          }
        })
        .then(res => {
          store.dispatch('authenticaitonSuccessful', accessToken)
          if (router.app._route.name === 'Login') {
            router.push(router.app._route.query.redirect || { name: 'BooksList' })
          }
        })
    } else {
      store.dispatch('authenticaitonFail')
    }

    axios.get('/api/version').then(res => {
      if (this.version !== res.data.version) {
        if (localStorage.apiVersion === res.data.version) {
          this.$_pushNotice('クライアントとAPIでバージョン齟齬があります', 'error')
          return
        }
        this.$_pushNotice(res.data.version + 'にバージョンアップを行います', 'info')
        localStorage.apiVersion = res.data.version
        setTimeout(() => {
          location.reload(true)
        }, 3000)
      }
    })
  }
}
</script>

<style lang="scss">
html {
  -webkit-touch-callout: none;
  scrollbar-width: none;
}
.selectable {
  -webkit-touch-callout: text;
}
html::-webkit-scrollbar {
  display:none;
}
</style>
