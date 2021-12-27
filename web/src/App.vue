<template>
  <v-app>
    <!-- 通知 -->
    <notifications group="default" animation-type="velocity">
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
        }).catch(error => {
          if (!error.response) {
            this.$_pushNotice('エラーが発生しました', 'error')
            return
          }
          const status = error.response.status
          if (status === 401 || status === 400) {
            this.$_pushNotice('認証エラーが発生したためログアウトします', 'error')
            store.dispatch('authenticaitonFail')
            router.push({
              name: 'Login'
            })
          }
        })
    } else {
      store.dispatch('authenticaitonFail')
    }

    axios
      .get('/api/version')
      .then(res => {
        if (this.version !== res.data.apiVersion) {
          if (localStorage.apiVersion === res.data.apiVersion) {
            this.$_pushNotice('クライアントとAPIでバージョン齟齬があります', 'error')
            return
          }
          this.$_pushNotice(res.data.apiVersion + 'にバージョンアップを行います', 'info')
          localStorage.apiVersion = res.data.apiVersion
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
}
.selectable {
  -webkit-touch-callout: text;
}
</style>
