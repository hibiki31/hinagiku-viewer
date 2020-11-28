import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    showMenuBer: true
  },
  mutations: {
    showMenuBer (state) {
      state.showMenuBer = true
    },
    hideMenuBer (state) {
      state.showMenuBer = false
    }
  },
  actions: {
    showMenuBer (context) {
      context.commit('showMenuBer')
    },
    hideMenuBer (context) {
      context.commit('hideMenuBer')
    }
  },
  modules: {
  }
})
