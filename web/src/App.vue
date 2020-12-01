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
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',

  components: {
  },

  data: () => ({
    //
  })
}
</script>

<style lang="scss">
html {
  -webkit-user-select: none;
}
</style>