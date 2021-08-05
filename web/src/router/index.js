import Vue from 'vue'
import VueRouter from 'vue-router'

import store from '../store'

import BooksList from '../views/BooksList.vue'
import BookReader from '../views/BookReader.vue'
import Login from '../views/Login.vue'

Vue.use(VueRouter)

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
  const isAuthed = store.state.isAuthed
  if (isAuthed || to.matched.some(record => !record.meta.requiresAuth)) {
    if ((to.name === 'Login' && isAuthed) || (to.name === 'Logout' && !isAuthed)) {
      next({ name: 'BooksList' })
    } else {
      next()
    }
  } else {
    next({
      name: 'Login'
    })
  }
})

export default router
