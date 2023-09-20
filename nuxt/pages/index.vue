<template>
  <v-app>
    <v-app-bar color="primary" density="compact">
      <v-app-bar-nav-icon></v-app-bar-nav-icon>
      <v-toolbar-title></v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field density="compact" variant="outlined" append-inner-icon="mdi-magnify" single-line
        hide-details></v-text-field>
      <v-btn icon><v-icon>mdi-reload</v-icon></v-btn>
    </v-app-bar>
    <v-main>
      <p>{{ count }}</p>
      <p>{{ double }}</p>
      <v-btn @click="decrement">減</v-btn>
      <v-btn @click="increment">増</v-btn>
      {{ data }}
    </v-main>
    
  </v-app>
</template>

<script setup lang="ts">
import { useCounter } from '@/composables/count'
import { useBaseFetch } from '@/composables/fetch'

const { count, double, increment, decrement } =  useCounter()
const { data, pending, error, refresh } = await useBaseFetch("/api/version")


</script>
