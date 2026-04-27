<template>
  <div class="min-h-screen flex bg-gray-50">
    <!-- Sidebar -->
    <aside class="w-56 bg-white border-r border-gray-200 flex flex-col">
      <div class="px-5 py-4 border-b border-gray-200">
        <span class="text-lg font-bold text-rose-600">SGK</span>
        <span class="text-sm text-gray-500 ml-1">Kaneshiro</span>
      </div>
      <nav class="flex-1 px-3 py-4 space-y-1">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-rose-50 hover:text-rose-600 transition-colors"
          active-class="bg-rose-50 text-rose-600"
        >
          <span class="text-base">{{ item.icon }}</span>
          {{ item.label }}
        </RouterLink>
      </nav>
      <div class="px-4 py-3 border-t border-gray-200">
        <p class="text-xs text-gray-500 truncate">{{ auth.user?.email }}</p>
        <div class="flex items-center justify-between mt-1">
          <button
            class="text-xs text-gray-400 hover:text-red-500 transition-colors"
            @click="auth.logout(); $router.push('/login')"
          >
            Sair
          </button>
          <button
            class="w-7 h-7 flex items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            :title="dark ? 'Modo claro' : 'Modo escuro'"
            @click="toggleDark()"
          >
            <span class="text-base leading-none">{{ dark ? '☀️' : '🌙' }}</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main -->
    <main class="flex-1 overflow-auto p-6">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useDarkMode } from '@/composables/useDarkMode'

const auth = useAuthStore()
const { dark, toggle: toggleDark } = useDarkMode()

const navItems = computed(() => {
  const items = [
    { to: '/agendamentos', icon: '📅', label: 'Agendamentos' },
    { to: '/pagamentos', icon: '💰', label: 'Pagamentos' },
    { to: '/profissionais', icon: '✂️', label: 'Profissionais' },
    { to: '/servicos', icon: '💅', label: 'Serviços' },
    { to: '/produtos', icon: '📦', label: 'Produtos' },
  ]
  if (auth.isAdmin) {
    items.push({ to: '/relatorios', icon: '📊', label: 'Relatórios' })
    items.push({ to: '/usuarios', icon: '🔑', label: 'Usuários' })
  }
  return items
})
</script>
