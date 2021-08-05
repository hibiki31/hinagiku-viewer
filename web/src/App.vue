<template>
  <v-app>
    <notifications group="default" animation-type="velocity">
      <template slot="body" slot-scope="props">
        <v-alert
          :type="props.item.type"
          class="ma-3 mb-0"
          border="left"
          colored-border
        >
          <div class="d-flex align-center ml-3">
            <div class="body-2 mr-auto">{{ props.item.text }}</div>
          </div>
        </v-alert>
      </template>
    </notifications>
    <v-main>
      <transition name="fade">
      <router-view />
      </transition>
    </v-main>
  </v-app>
</template>

<script>
import axios from '@/axios/index'
import Cookies from 'js-cookie'

export default {
  name: 'App',
  data: () => ({
    version: require('../package.json').version,
    userId: ''
  }),
  mounted: async function () {
    const token = Cookies.get('token')
    axios.interceptors.request.use(
      (config) => {
        config.headers.Authorization = 'Bearer ' + token
        return config
      },
      (err) => {
        return Promise.reject(err)
      }
    )
  }
}
</script>

<style lang="scss">
html {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  -khtml-user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
}
.selectable {
  -webkit-user-select: text;
  -moz-user-select: text;
  -ms-user-select: text;
  -khtml-user-select: text;
  -webkit-user-select: text;
  -webkit-touch-callout: text;
}
</style>
