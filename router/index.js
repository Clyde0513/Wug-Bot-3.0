import { createRouter, createWebHistory } from 'vue-router'
import Home from '../src/Home.vue'

const routes = [
  // {
  //   path: '/',
  //   name: 'Home',
  //   component: Home
  // },
  {
    path: '/',
    name: 'Commands',
    component: () => import('../src/views/Commands.vue')
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: () => import('../src/views/Welcome.vue')
  },
  {
    path: '/interact',
    name: 'BotInterface',
    component: () => import('../src/views/BotInterface.vue')
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
