import Vue from 'vue'
import Vuex from 'vuex'

import userData from './modules/userData'
import readerState from './modules/readerState'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    userData,
    readerState
  }
})
