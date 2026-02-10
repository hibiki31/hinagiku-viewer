// Utilities
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    apiVersion: '' as string,
  }),
  actions: {
    setApiVersion(version: string) {
      this.apiVersion = version
    },
  },
})
