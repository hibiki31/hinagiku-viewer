import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'

import VueCookies from 'vue-cookies'

import Notifications from 'vue-notification'
import velocity from 'velocity-animate'
import VueScrollTo from 'vue-scrollto'
import { VueHammer } from 'vue2-hammer'
import VueForceNextTick from 'vue-force-next-tick'

// 分割して書いているだけ
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
}

createApp()
