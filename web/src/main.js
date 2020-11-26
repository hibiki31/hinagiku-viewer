import Vue from 'vue'
import App from './App.vue'
import './registerServiceWorker'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'

import Notifications from 'vue-notification'
import velocity from 'velocity-animate'

Vue.config.productionTip = false
Vue.use(Notifications, { velocity })

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')
