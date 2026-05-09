import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
    { path: '/timeline', name: 'timeline', component: () => import('../views/Timeline.vue') },
    { path: '/projects', name: 'projects', component: () => import('../views/Projects.vue') },
    { path: '/files', name: 'files', component: () => import('../views/Files.vue') },
    { path: '/git', name: 'git', component: () => import('../views/Git.vue') },
    { path: '/reports', name: 'reports', component: () => import('../views/Reports.vue') },
    { path: '/settings', name: 'settings', component: () => import('../views/Settings.vue') },
  ],
})

export default router
