import Vue from 'vue'
import VueRouter from 'vue-router'
import Books from '../views/Books.vue'
import BookReader from '../views/BookReader.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Books',
    component: Books
  },
  {
    path: '/books/:uuid',
    name: 'BookReader',
    component: BookReader,
    meta: {
      requiresAuth: true
    }
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
