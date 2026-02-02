import { defineStore } from 'pinia'
import axios from '@/func/axios'
import type { components } from '@/api'

type BookBase = components['schemas']['BookBase']

interface SearchQuery {
  limit: number
  offset: number
  title: string | null
  rate: number | null
  genre: string | null
  libraryId: number | null
  fullText: string
  authorLike: string | null
  titleLike: string | null
  sortKey?: string
  sortDesc?: boolean
}

type OpenBook = Partial<BookBase> & Pick<BookBase, 'userData'>

interface ReaderStateState {
  booksList: BookBase[]
  booksCount: number
  readerPage: number
  showListMode: boolean
  openBook: OpenBook
  searchQuery: SearchQuery
}

const baseState: ReaderStateState = {
  booksList: [],
  booksCount: 0,
  readerPage: 1,
  showListMode: false,
  openBook: {
    userData: {
      rate: null,
      openPage: null,
      readTimes: null,
      lastOpenDate: null
    }
  },
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

// localStorageから検索パラメータを復元
const loadSearchQuery = (): SearchQuery => {
  try {
    console.log('検索パラメータを復元')
    const getParam = JSON.parse(localStorage.getItem('searchQuery') || '{}')
    const query = { ...baseState.searchQuery }
    // 上書きじゃなくてあったKeyを追加
    for (const key in getParam) {
      if (key in query) {
        ;(query as Record<string, unknown>)[key] = getParam[key]
      }
    }
    return query
  } catch {
    localStorage.removeItem('searchQuery')
    return baseState.searchQuery
  }
}

export const useReaderStateStore = defineStore('readerState', {
  state: (): ReaderStateState => ({
    ...baseState,
    searchQuery: loadSearchQuery()
  }),

  actions: {
    setBooksResult(res: { rows: BookBase[], count: number }) {
      this.booksList = res.rows
      this.booksCount = res.count
    },

    setSearchQuery(searchQuery: SearchQuery) {
      this.searchQuery = searchQuery
      localStorage.setItem('searchQuery', JSON.stringify(searchQuery))
    },

    setOpenBook(openBook: OpenBook) {
      this.openBook = openBook
    },

    setShowListMode(showListMode: boolean) {
      this.showListMode = showListMode
    },

    async serachBooks(resetOffset: boolean = false) {
      const query = this.searchQuery
      if (resetOffset) {
        query.offset = 0
        this.setSearchQuery(query)
      }

      try {
        const response = await axios.get('/api/books', {
          params: query
        })
        this.setBooksResult(response.data)
      } catch (error) {
        console.error('書籍検索エラー:', error)
      }
    }
  }
})
