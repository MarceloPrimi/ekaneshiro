import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/agendamentos' },
      { path: 'agendamentos', component: () => import('@/views/AgendamentosView.vue') },
      { path: 'pagamentos', component: () => import('@/views/PagamentosView.vue') },
      { path: 'profissionais', component: () => import('@/views/ProfissionaisView.vue') },
      { path: 'servicos', component: () => import('@/views/ServicosView.vue') },
      { path: 'produtos', component: () => import('@/views/ProdutosView.vue') },
      { path: 'relatorios', component: () => import('@/views/RelatoriosView.vue'), meta: { adminOnly: true } },
      { path: 'usuarios', component: () => import('@/views/UsuariosView.vue'), meta: { adminOnly: true } },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'
  if (to.meta.requiresAuth && auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      return '/login'
    }
  }
  if (to.meta.guest && auth.isAuthenticated) return '/agendamentos'
  if (to.meta.adminOnly && !auth.isAdmin) return '/agendamentos'
})

export default router
