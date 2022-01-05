import axios from '@/axios/index'

const baseState = {
  booksList: [],
  booksCount: 0,
  readerPage: 1,
  showListMode: false,
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

const state = Object.assign({}, baseState)

try {
  console.log('検索パラメータを復元')
  const getParam = JSON.parse(localStorage.getItem('searchQuery'))
  // 上書きじゃなくてあったKeyを追加
  for (const key in getParam) {
    state.searchQuery[key] = getParam[key]
  }
} catch (e) {
  localStorage.removeItem('searchQuery')
}

const mutations = {
  setBooksResult (state, res) {
    state.booksList = res.rows
    state.booksCount = res.count
  },
  setSearchQuery (state, searchQuery) {
    state.searchQuery = searchQuery
    localStorage.setItem('searchQuery', JSON.stringify(searchQuery))
  },
  setShowListMode (state, showListMode) {
    state.showListMode = showListMode
  }
}

const actions = {
  setSearchQuery (context, searchQuery) {
    context.commit('setSearchQuery', searchQuery)
  },
  async serachBooks (context, resetOffset) {
    const query = context.state.searchQuery
    if (resetOffset) {
      query.offset = 0
      context.commit('setSearchQuery', query)
    }
    await axios
      .get('/api/books', {
        params: query
      })
      .then((response) => {
        context.commit('setBooksResult', response.data)
      })
  },
  setShowListMode (context, showListMode) {
    context.commit('setShowListMode', showListMode)
  }
}

const getters = {
  booksList: state => state.booksList,
  booksCount: state => state.booksCount,
  searchQuery: state => state.searchQuery,
  showListMode: state => state.showListMode
}

export default {
  state,
  mutations,
  actions,
  getters
}
