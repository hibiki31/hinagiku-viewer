// import type { Ref } from "vue";
 
export default defineNuxtRouteMiddleware((to, from) => {
  console.log('common middleware')
  return navigateTo('/')
})