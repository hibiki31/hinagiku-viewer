import Vue from 'vue'
import Vuex from 'vuex'
import Cookies from 'js-cookie'
import VueJwtDecode from 'vue-jwt-decode'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    showMenuBer: true,
    lastOpenUUID: '',
    lastOpenPage: 1,
    isLoaded: false,
    isAuthed: false,
    isAdmin: false,
    token: null,
    userId: null,
    timeOffcet: 0
  },
  getters: {
    loadToken: state => {
      return state.token
    }
  },
  mutations: {
    updateAuthState (state, responseData) {
      Cookies.remove('token')
      state.isLoaded = true

      if (responseData) {
        let token
        try {
          token = VueJwtDecode.decode(responseData.access_token)
        } catch (error) {
          return
        }
        state.isAuthed = true
        state.token = responseData.access_token
        state.userId = token.sub
        state.isAdmin = true
        Cookies.set('token', responseData.access_token)
      }
    },
    showMenuBer (state) {
      state.showMenuBer = true
    },
    hideMenuBer (state) {
      state.showMenuBer = false
    },
    setLastOpen (state, uuid, page) {
      state.lastOpenPage = page
      state.lastOpenUUID = uuid
    },
    loadToken (state) {
      state.token = Cookies.get('token')
    }
  },
  actions: {
    updateAuthState (context, responseData) {
      context.commit('updateAuthState', responseData)
    },
    showMenuBer (context) {
      context.commit('showMenuBer')
    },
    hideMenuBer (context) {
      context.commit('hideMenuBer')
    },
    setLastOpen (context, uuid, page) {
      context.commit('setLastOpen', uuid, page)
    },
    loadToken (context) {
      context.commit('loadToken')
    }
  },
  modules: {
  }
})
