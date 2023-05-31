import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { MAIN_THEME, mainTheme} from '@/helpers/themes'
import { defaults } from '@/helpers/defaults'
import '@mdi/font/css/materialdesignicons.css'


export default defineNuxtPlugin(nuxtApp => {
  const vuetify = createVuetify({
    ssr: true,
    defaults,
    components,
    directives,
    // 他の設定をここに記述していく
    theme: {
      defaultTheme: MAIN_THEME,
      themes: {
        mainTheme,
      },
      // primary-darken-9 primary-lighten-9 までできるようにする
      variations: {
        colors: ['primary', 'secondary', 'accent'],
        lighten: 9,
        darken: 9,
      },
    }
  })

  // Vue.js で Vuetify を使用する
  nuxtApp.vueApp.use(vuetify)
})