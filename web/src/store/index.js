import Vue from 'vue'
import Vuex from 'vuex'

import userData from './modules/userData'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    userData
  }
})
