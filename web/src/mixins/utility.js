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
    $_convertDateFormat (date, time = false) {
      if (!date) {
        return undefined
      } else if (typeof date !== 'object') {
        date = new Date(date)
      }
      const dateFormat = date.getFullYear() + '/' +
             ('0' + (date.getMonth() + 1)).slice(-2) + '/' +
             ('0' + date.getDate()).slice(-2)
      if (time) {
        const timeFormat = ('0' + date.getHours()).slice(-2) + ':' +
               ('0' + date.getMinutes()).slice(-2)
        return dateFormat + ' ' + timeFormat
      } else {
        return dateFormat
      }
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
    }
  }
})
