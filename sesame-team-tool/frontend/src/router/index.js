import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import MatchPool from '../views/MatchPool.vue'
import FindScore from '../views/FindScore.vue'
import Profile from '../views/Profile.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/match-pool',
    name: 'MatchPool',
    component: MatchPool
  },
  {
    path: '/find-score',
    name: 'FindScore',
    component: FindScore
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

export default router
