import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    baseURL: [null, undefined].includes(import.meta.env.VITE_APP_API_HOST) ? '' : import.meta.env.VITE_APP_API_HOST,
    token: '',
    tokenValidated: false,
    authed: false,
  }),
  actions: {
    loginSuccess(token: string) {
      this.token = token
      this.tokenValidated = true
      this.authed = true
    },
  },
})