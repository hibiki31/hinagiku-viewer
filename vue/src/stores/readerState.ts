import { defineStore } from 'pinia'
import { apiClient } from '@/func/client'
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
  // 新規追加パラメータ
  fileNameLike?: string | null
  cached?: boolean | null
  authorIsFavorite?: boolean | null
  seriesId?: string | null
  tag?: string | null
  state?: string | null
  uuid?: string | null
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
    titleLike: null,
    sortKey: undefined,
    sortDesc: false
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
        const { data, error } = await apiClient.GET('/api/books', {
          params: {
            query: {
              fullText: query.fullText || undefined,
              titleLike: query.titleLike || undefined,
              authorLike: query.authorLike || undefined,
              rate: query.rate ?? undefined,
              genreId: query.genre || undefined,
              libraryId: query.libraryId ?? undefined,
              limit: query.limit,
              offset: query.offset,
              sortKey: query.sortKey,
              sortDesc: query.sortDesc,
              // 新規追加パラメータ
              fileNameLike: query.fileNameLike || undefined,
              cached: query.cached ?? undefined,
              authorIsFavorite: query.authorIsFavorite ?? undefined,
              seriesId: query.seriesId || undefined,
              tag: query.tag || undefined,
              state: (query.state === 'missing_file' || query.state === 'duplicate_missing_file') ? query.state : undefined,
              uuid: query.uuid || undefined,
            }
          }
        })
        if (error) throw error
        if (data) {
          this.setBooksResult(data)
        }
      } catch (error) {
        console.error('書籍検索エラー:', error)
      }
    }
  }
})
