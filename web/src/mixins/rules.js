import Vue from 'vue'

Vue.mixin({
  methods: {
    // 必須
    $_required: (value) => !!value || 'Required.',
    // 64文字以下
    $_limitLength64: (value) => {
      if (value === undefined) {
        return false || 'requird'
      } else {
        return value.length <= 64 || '64 characters maximum.'
      }
    },
    // 文字種制限
    $_characterRestrictions (value) {
      const regex = new RegExp(/^[A-Za-z0-9-_]*$/)
      return regex.test(value) || 'Can use character A-Z, a-z, 0-9, -, _'
    },
    // 先頭文字制限
    $_firstCharacterRestrictions (value) {
      const regex = new RegExp(/^[A-Za-z].*/)
      return regex.test(value) || 'Can use first character A-Z, a-z'
    },
    // 数字だけ
    $_intValueRestrictions (value) {
      const regex = new RegExp(/^[0-9]*$/)
      return regex.test(value) || 'Only Int value'
    }
  }
})
