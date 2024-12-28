import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/servers'
  },
  {
    path: '/servers',
    name: 'servers',
    component: () => import('../views/ServersView.vue'),
    meta: {
      title: '服务器管理',
      icon: 'Monitor'
    }
  },
  {
    path: '/tasks',
    name: 'tasks', 
    component: () => import('../views/TasksView.vue'),
    meta: {
      title: '任务管理',
      icon: 'List'
    }
  },
  {
    path: '/alerts',
    name: 'alerts',
    component: () => import('../views/AlertsView.vue'),
    meta: {
      title: '告警中心',
      icon: 'Warning'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - RemoteBuilder` : 'RemoteBuilder'
  next()
})

export default router 