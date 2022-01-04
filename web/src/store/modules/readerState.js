import axios from '@/axios/index'
import Cookies from 'js-cookie'

const state = {
  isLoading: false,
  booksList: [],
  booksCount: 0,
  searchQuery: {
    limit: 60,
    offset: 0,
    title: null,
    rate: null,
    genre: null,
    libraryId: null,
    fullText: '',
    authorLike: null,
    titleLike: null
  }
}

// 検索パラメータを復元
try {
  const getParam = JSON.parse(localStorage.getItem('searchQuery'))
  // 上書きじゃなくてあったKeyを追加
  for (const key in getParam) {
    state.searchQuery[key] = getParam[key]
  }
} catch (e) {
  localStorage.removeItem('searchQuery')
}

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
  },
  setBooksResult (state, res) {
    state.booksList = res.books
    state.booksCount = res.count
  },
  setSearchQuery (state, searchQuery) {
    state.searchQuery = searchQuery
    localStorage.setItem('searchQuery', JSON.stringify(searchQuery))
  }
}

const actions = {
  authenticaitonSuccessful (context, accessToken, username) {
    context.commit('authenticaitonSuccessful', accessToken, username)
  },
  authenticaitonFail (context) {
    context.commit('authenticaitonFail')
  },
  setSearchQuery (context, searchQuery) {
    context.commit('setSearchQuery', searchQuery)
  },
  async serachBooks (context, searchQuery) {
    if (searchQuery !== undefined) {
      context.commit('setSearchQuery', searchQuery)
    }
    await axios
      .get('/api/books', {
        params: context.state.searchQuery
      })
      .then((response) => {
        context.commit('setBooksResult', response.data)
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

const getters = {
  booksList: state => state.booksList,
  booksCount: state => state.booksCount,
  searchQuery: state => state.searchQuery
}

export default {
  state,
  mutations,
  actions,
  getters
}
