import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    showMenuBer: true,
    lastOpenUUID: '',
    lastOpenPage: 1
  },
  mutations: {
    showMenuBer (state) {
      state.showMenuBer = true
    },
    hideMenuBer (state) {
      state.showMenuBer = false
    },
    setLastOpen (state, uuid, page) {
      state.lastOpenPage = page
      state.lastOpenUUID = uuid
    }
  },
  actions: {
    showMenuBer (context) {
      context.commit('showMenuBer')
    },
    hideMenuBer (context) {
      context.commit('hideMenuBer')
    },
    setLastOpen (context, uuid, page) {
      context.commit('setLastOpen', uuid, page)
    }
  },
  modules: {
  }
})
