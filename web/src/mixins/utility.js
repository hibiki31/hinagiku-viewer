import Vue from 'vue'

Vue.mixin({
  methods: {
    $_sleep (msec) {
      return new Promise(resolve => setTimeout(resolve, msec))
    },
    $_convertNumFormat (num) {
      if (!num) {
        return 0
      } else if (num < 10000) {
        return num.toLocaleString()
      }
      const formatNum = String(num).slice(0, -3)
      return formatNum[0] + '.' + formatNum[1] + '万'
    },
    $_convertDateFormat (date) {
      if (!date) {
        return undefined
      }
      const dt = new Date(Date.parse(date))
      const y = dt.getFullYear()
      const m = ('00' + (dt.getMonth() + 1)).slice(-2)
      const d = ('00' + dt.getDate()).slice(-2)
      return (y + '-' + m + '-' + d)
    },
    $_pushNotice (text, type, color, icon, group = 'default') {
      this.$notify({
        group,
        text,
        type,
        duration: 600,
        data: { icon, color }
      })
    },
    $pushNotice (text, type, color, icon, group = 'default') {
      this.$notify({
        group,
        text,
        type,
        duration: 600,
        data: { icon, color }
      })
    },
    $_apiErrorHandler (error) {
      if (!error.response) {
        this.$_pushNotice('サーバーエラーが発生しました', 'error')
        return
      }
      const status = error.response.status
      if (status === 401 || status === 400) {
        this.$_pushNotice('認証エラーが発生しました', 'error')
      } else {
        this.$_pushNotice(error.response.data, 'error')
      }
    },
    $_getCoverURL (uuid) {
      const api = process.env.VUE_APP_API_HOST
      if (api) {
        return process.env.VUE_APP_API_HOST + '/media/books/' + uuid
      } else {
        return '/media/books/' + uuid
      }
    },
    $_fitByte (size) {
      if (size >= Math.pow(1024, 2)) {
        return Math.floor(size / Math.pow(1024, 2)).toFixed(1) + 'MB'
      } else {
        return size
      }
    }
  }
})
