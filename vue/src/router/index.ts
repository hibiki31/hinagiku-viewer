/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory, type NavigationGuardNext, type RouteLocationNormalized } from 'vue-router'
import { setupLayouts } from 'virtual:generated-layouts'
import { routes } from 'vue-router/auto-routes'
import { useUserDataStore } from '@/stores/userData'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: setupLayouts(routes),
})

// 認証ガード
router.beforeEach((to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
  const userDataStore = useUserDataStore()
  const isAuthed = userDataStore.isAuthed

  // ログインしているのにログインページに行く場合
  if (isAuthed && to.path === '/login') {
    next('/')
    return
  }

  // 認証が必要なページに未認証でアクセスした場合
  if (!isAuthed && to.path !== '/login') {
    next('/login')
    return
  }

  next()
})

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err: any, to: RouteLocationNormalized) => {
  if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
    if (!localStorage.getItem('vuetify:dynamic-reload')) {
      console.log('Reloading page to fix dynamic import error')
      localStorage.setItem('vuetify:dynamic-reload', 'true')
      location.assign(to.fullPath)
    } else {
      console.error('Dynamic import error, reloading page did not fix it', err)
    }
  } else {
    console.error(err)
  }
})

router.isReady().then(() => {
  localStorage.removeItem('vuetify:dynamic-reload')
})

export default router
