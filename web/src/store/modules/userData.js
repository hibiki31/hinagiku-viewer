import axios from '@/axios/index'
import Cookies from 'js-cookie'

const defaultState = {
  isLoaded: true,
  isAuthed: false,
  accessToken: null,
  username: null,
  isAdmin: false
}

const state = Object.assign({}, defaultState)

const mutations = {
  authenticaitonSuccessful (state, accessToken, username) {
    Cookies.set('accessToken', accessToken)
    axios.interceptors.request.use(
      config => {
        config.headers.Authorization = `Bearer ${accessToken}`
        return config
      })
    state.accessToken = accessToken
    state.username = username
    state.isAuthed = true
    state.isLoaded = false
  },
  authenticaitonFail (state) {
    state.isAuthed = false
    state.isLoaded = false
    Cookies.remove('accessToken')
  }
}

const actions = {
  authenticaitonSuccessful (context, accessToken, username) {
    context.commit('authenticaitonSuccessful', accessToken, username)
  },
  authenticaitonFail (context) {
    context.commit('authenticaitonFail')
  },
  async authVerification (context) {
    context.commit('setToken')
    await axios
      .get('/api/auth/validate',
        {
          headers: {
            Authorization: `Bearer ${context.state.accessToken}`
          }
        }
      )
      .then(res => {
        console.log(res)
      })
  },
  async auth (context, username, password) {
    this.$notify({
      group: 'default',
      text: 'a',
      type: 'error',
      duration: 600
    })
    // フォームデータ作成
    const loginForm = new FormData()
    loginForm.append('username', username)
    loginForm.append('password', password)
    // トークン取得
    await axios
      .post('/api/auth', loginForm)
      .then(res => {
        if (res.status !== 200) {
          this.$_pushNotice('ユーザ名またはパスワードが違います', 'error')
          return false
        }
        context.commit('setToken', res.data.access_token)
      })
      .catch(async () => {
        this.$_pushNotice('サーバエラーが発生しました', 'error')
        return false
      })
  }
}

export default {
  state,
  mutations,
  actions
}
