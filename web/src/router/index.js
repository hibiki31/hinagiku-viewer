import Vue from 'vue'
import VueRouter from 'vue-router'
import VueHead from 'vue-head'

import store from '../store'

import BooksList from '../views/BooksList.vue'
import BookReader from '../views/BookReader.vue'
import Login from '../views/Login.vue'

Vue.use(VueRouter)
Vue.use(VueHead)

const routes = [
  {
    path: '/',
    name: 'BooksList',
    component: BooksList,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/books/:uuid',
    name: 'BookReader',
    component: BookReader,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthed = store.state.userData.isAuthed
  if (isAuthed || to.matched.some(record => !record.meta.requiresAuth)) {
    if ((to.name === 'Login' && isAuthed) || (to.name === 'Logout' && !isAuthed)) {
      // ログインしているのにログインページに行く場合
      next({
        name: 'BooksList'
      })
    } else {
      // 認証済みか認証がいらないページにアクセスした場合
      next()
    }
  } else {
    // 認証が必要なページに未認証でアクセスした場合
    next({
      name: 'Login'
    })
  }
})

export default router
