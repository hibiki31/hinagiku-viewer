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

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

const appInit = async () => {
  const token = Cookies.get('token')

  if (!token) {
    store.dispatch('updateAuthState', {})
    if (router.app._route.name === 'Login' && router.app._route.query.redirect) {
      router.push({ name: 'Login' })
    }
  } else {
    await axios
      .get('/api/auth/validate',
        {
          headers: {
            Authorization: 'Bearer ' + token
          }
        }
      )
      .then(res => {
        store.dispatch('updateAuthState', res.data)
        if (router.app._route.name === 'Login') {
          router.push(router.app._route.query.redirect || { name: 'BooksList' })
        }
      })
      .catch(() => {
        store.dispatch('updateAuthState', {})
      })
  }
}

appInit()
