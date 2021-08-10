import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'

import VueCookies from 'vue-cookies'
import Cookies from 'js-cookie'
import axios from '@/axios/index'

import Notifications from 'vue-notification'
import velocity from 'velocity-animate'
import VueScrollTo from 'vue-scrollto'
import { VueHammer } from 'vue2-hammer'
import VueForceNextTick from 'vue-force-next-tick'

import './mixins/utility'
import './mixins/rules'

Vue.config.productionTip = false

Vue.use(Notifications, { velocity })
Vue.use(VueHammer)
Vue.use(VueCookies)
Vue.use(VueScrollTo)
Vue.use(VueForceNextTick)

const createApp = async () => {
  new Vue({
    router,
    store,
    vuetify,
    render: h => h(App)
  }).$mount('#app')

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
}

createApp()
