<template>
  <div class="min-h-screen flex bg-gray-50">
    <!-- Overlay mobile -->
    <div
      v-if="drawerOpen"
      class="fixed inset-0 bg-black/40 z-40 lg:hidden"
      @click="drawerOpen = false"
    />

    <!-- Sidebar / Drawer -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 flex flex-col bg-white border-r border-gray-200 transition-all duration-300 ease-in-out',
        drawerOpen
          ? 'w-56 pointer-events-auto'
          : 'w-0 lg:w-14 overflow-hidden pointer-events-none lg:pointer-events-auto',
      ]"
    >
      <!-- Brand + toggle -->
      <div class="flex items-center justify-between px-3 py-4 border-b border-gray-200 flex-shrink-0 h-14">
        <div v-if="drawerOpen" class="flex items-center overflow-hidden">
          <img src="/logo.png" alt="Logo Sanshin" class="w-12 h-12 rounded-md object-contain flex-shrink-0" />
        </div>
        <button
          class="ml-auto w-8 h-8 flex items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors flex-shrink-0"
          @click="drawerOpen = !drawerOpen"
          :title="drawerOpen ? 'Fechar menu' : 'Abrir menu'"
        >
          <PanelLeftClose v-if="drawerOpen" class="w-4 h-4" />
          <Menu v-else class="w-4 h-4" />
        </button>
      </div>

      <!-- Nav links -->
      <nav class="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto overflow-x-hidden">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :title="drawerOpen ? '' : item.label"
          class="flex items-center gap-3 px-2 py-2 rounded-lg text-sm font-medium text-gray-500 hover:bg-rose-50 hover:text-rose-600 transition-colors whitespace-nowrap"
          active-class="bg-rose-50 text-rose-600"
          @click="closeMobileDrawer"
        >
          <component :is="item.icon" class="w-4 h-4 flex-shrink-0" />
          <span v-if="drawerOpen" class="truncate">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <!-- Footer: username + logout + dark mode + minha senha -->
      <div class="px-2 py-3 border-t border-gray-200 flex-shrink-0">
        <p v-if="drawerOpen" class="text-xs text-gray-400 truncate px-1 mb-2">{{ auth.user?.username }}</p>
        <div class="flex items-center" :class="drawerOpen ? 'justify-between px-1' : 'flex-col gap-1 items-center'">
          <button
            class="flex items-center gap-2 text-xs text-gray-400 hover:text-rose-500 transition-colors"
            title="Minha senha"
            @click="abrirModalSenha"
          >
            <KeyRound class="w-4 h-4" />
            <span v-if="drawerOpen">Minha senha</span>
          </button>
          <button
            class="flex items-center gap-2 text-xs text-gray-400 hover:text-rose-500 transition-colors"
            title="Sair"
            @click="auth.logout(); $router.push('/login')"
          >
            <LogOut class="w-4 h-4" />
            <span v-if="drawerOpen">Sair</span>
          </button>
          <button
            class="w-7 h-7 flex items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            :title="dark ? 'Modo claro' : 'Modo escuro'"
            @click="toggleDark()"
          >
            <Sun v-if="dark" class="w-4 h-4" />
            <Moon v-else class="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Hamburger button (mobile, shown when drawer is closed) -->
    <button
      class="fixed top-[max(0.75rem,env(safe-area-inset-top))] left-3 z-50 lg:hidden w-11 h-11 flex items-center justify-center bg-white border border-gray-200 rounded-xl shadow-sm text-gray-500 hover:bg-gray-50 transition-colors"
      :class="{ 'opacity-0 pointer-events-none': drawerOpen }"
      @click="drawerOpen = true"
      aria-label="Abrir menu"
    >
      <Menu class="w-5 h-5" />
    </button>

    <!-- Main content -->
    <main
      class="flex-1 overflow-auto p-4 pt-14 sm:p-6 sm:pt-6 transition-all duration-300 ease-in-out"
      :class="[
        drawerOpen ? 'lg:ml-56' : 'lg:ml-14',
        bottomNavMinimized ? 'pb-[calc(2.5rem+env(safe-area-inset-bottom))]' : 'pb-[calc(5rem+env(safe-area-inset-bottom))]',
        'lg:pb-6 lg:pt-6'
      ]"
    >
      <!-- KeepAlive mantém views em memória entre navegações.
           NÃO use :key="route.path" aqui — isso remonta a view a cada troca
           e quebra cache, fetch e a transição no mobile. -->
      <RouterView v-slot="{ Component }">
        <KeepAlive :include="KEEP_ALIVE_VIEWS">
          <component :is="Component" />
        </KeepAlive>
      </RouterView>
    </main>

    <!-- Modal: Minha Senha -->
    <div v-if="modalSenha" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-[60] p-4" @click.self="modalSenha = false">
      <div class="bg-white w-full sm:max-w-sm sm:rounded-xl rounded-t-3xl shadow-xl overflow-hidden pb-[env(safe-area-inset-bottom)]">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1"></div>
        <div class="px-6 pt-5 pb-2">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Alterar senha</h3>
          <form id="form-minha-senha" @submit.prevent="salvarMinhaSenha" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Senha atual</label>
              <input v-model="formSenha.senha_atual" type="password" required autocomplete="current-password"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nova senha</label>
              <input v-model="formSenha.nova_senha" type="password" required minlength="6" autocomplete="new-password"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Confirmar nova senha</label>
              <input v-model="formSenha.confirmar" type="password" required minlength="6" autocomplete="new-password"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <p v-if="erroSenha" class="text-sm text-red-600">{{ erroSenha }}</p>
          </form>
        </div>
        <div class="flex gap-2 px-6 py-4 border-t border-gray-100">
          <button type="button" @click="modalSenha = false" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button type="submit" form="form-minha-senha" :disabled="salvandoSenha" class="flex-1 bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ salvandoSenha ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- TOAST NOTIFICATIONS -->
    <transition-group
      tag="div"
      name="toast"
      class="fixed bottom-[calc(5rem+env(safe-area-inset-bottom))] lg:bottom-6 right-4 z-[100] flex flex-col gap-2 pointer-events-none"
    >
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="[
          'pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium min-w-[220px] max-w-xs',
          t.type === 'success' ? 'bg-green-600 text-white' : 'bg-red-600 text-white',
        ]"
      >
        <svg v-if="t.type === 'success'" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
        {{ t.msg }}
      </div>
    </transition-group>

    <!-- BOTTOM NAVIGATION BAR (mobile only) — z-30 fica ABAIXO dos modais (z-50/z-60) -->
    <nav 
      :class="[
        'fixed left-0 right-0 z-30 bg-white border-t border-gray-100 shadow-[0_-1px_8px_rgba(0,0,0,0.06)] lg:hidden transition-all duration-300 ease-in-out pb-[env(safe-area-inset-bottom)]',
        bottomNavMinimized ? 'bottom-0 h-[calc(1.5rem+env(safe-area-inset-bottom))]' : 'bottom-0'
      ]"
    >
      <button
        @click="bottomNavMinimized = !bottomNavMinimized"
        class="absolute -top-8 left-1/2 -translate-x-1/2 w-14 h-8 bg-white border border-b-0 border-gray-100 rounded-t-xl flex items-center justify-center text-gray-400 hover:text-rose-600 shadow-[0_-2px_4px_rgba(0,0,0,0.04)]"
        :title="bottomNavMinimized ? 'Expandir menu' : 'Minimizar menu'"
        aria-label="Alternar menu inferior"
      >
        <ChevronDown :class="['w-5 h-5 transition-transform', bottomNavMinimized ? 'rotate-180' : '']" />
      </button>
      
      <div v-if="!bottomNavMinimized" class="flex">
        <RouterLink
          v-for="item in navItemsPrimary"
          :key="item.to"
          :to="item.to"
          class="flex-1 flex flex-col items-center justify-center py-2.5 gap-1 text-gray-400 hover:text-rose-600 transition-colors min-h-[60px]"
          active-class="text-rose-600"
          @click="drawerOpen = false; moreOpen = false"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span class="text-[10px] font-medium leading-none truncate max-w-[4.5rem] text-center">{{ item.label }}</span>
        </RouterLink>
        <button
          v-if="navItemsMore.length"
          type="button"
          class="flex-1 flex flex-col items-center justify-center py-2.5 gap-1 transition-colors min-h-[60px]"
          :class="moreOpen || isMoreRouteActive ? 'text-rose-600' : 'text-gray-400 hover:text-rose-600'"
          @click="moreOpen = !moreOpen"
        >
          <MoreHorizontal class="w-5 h-5" />
          <span class="text-[10px] font-medium leading-none">Mais</span>
        </button>
      </div>
      
      <div v-else class="flex items-center justify-center h-6" @click="bottomNavMinimized = false">
        <span class="text-[10px] text-gray-400">Toque para expandir menu</span>
      </div>
    </nav>

    <!-- Sheet "Mais" (admin + overflow) -->
    <div v-if="moreOpen" class="fixed inset-0 z-[55] lg:hidden" @click.self="moreOpen = false">
      <div class="absolute inset-0 bg-black/40" @click="moreOpen = false"></div>
      <div class="absolute inset-x-0 bottom-0 bg-white rounded-t-3xl shadow-2xl p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
        <div class="w-10 h-1 bg-gray-300 rounded-full mx-auto mb-4"></div>
        <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 px-1">Mais opções</p>
        <RouterLink
          v-for="item in navItemsMore"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 px-3 py-3.5 rounded-xl text-sm font-medium text-gray-700 hover:bg-rose-50 hover:text-rose-600"
          active-class="bg-rose-50 text-rose-600"
          @click="moreOpen = false; drawerOpen = false"
        >
          <component :is="item.icon" class="w-5 h-5" />
          {{ item.label }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

// Views mantidas em memória entre navegações — trocar de aba e voltar é instantâneo.
const KEEP_ALIVE_VIEWS = ['AgendamentosView', 'PagamentosView', 'ProfissionaisView', 'ServicosView', 'ProdutosView']
import {
  Calendar,
  CreditCard,
  Scissors,
  Sparkles,
  Package,
  BarChart2,
  Users,
  Menu,
  PanelLeftClose,
  LogOut,
  Sun,
  Moon,
  KeyRound,
  ChevronDown,
  MoreHorizontal,
} from '@lucide/vue'
import { useAuthStore } from '@/stores/auth'
import { useDarkMode } from '@/composables/useDarkMode'
import { useToast } from '@/composables/useToast'
import api from '@/api/client'

const auth = useAuthStore()
const route = useRoute()
const { dark, toggle: toggleDark } = useDarkMode()
const { toasts, sucesso: toastSucesso, erro: toastErro } = useToast()

const NAV_DESKTOP = 1024
const drawerOpen = ref(window.innerWidth >= NAV_DESKTOP)
const bottomNavMinimized = ref(false)
const moreOpen = ref(false)

/** Ao entrar em viewport mobile (DevTools ou resize), fecha o drawer —
 *  senão o overlay fixed inset-0 fica preso e bloqueia todos os cliques. */
function syncDrawerOnResize() {
  if (window.innerWidth < NAV_DESKTOP) {
    drawerOpen.value = false
  }
}
onMounted(() => window.addEventListener('resize', syncDrawerOnResize))
onUnmounted(() => window.removeEventListener('resize', syncDrawerOnResize))

// --- modal minha senha ---
const modalSenha = ref(false)
const salvandoSenha = ref(false)
const erroSenha = ref('')
const formSenha = ref({ senha_atual: '', nova_senha: '', confirmar: '' })

function abrirModalSenha() {
  formSenha.value = { senha_atual: '', nova_senha: '', confirmar: '' }
  erroSenha.value = ''
  modalSenha.value = true
  moreOpen.value = false
}

async function salvarMinhaSenha() {
  erroSenha.value = ''
  if (formSenha.value.nova_senha !== formSenha.value.confirmar) {
    erroSenha.value = 'As senhas não conferem.'
    return
  }
  salvandoSenha.value = true
  try {
    await api.patch('/usuarios/me/senha', {
      senha_atual: formSenha.value.senha_atual,
      nova_senha: formSenha.value.nova_senha,
    })
    modalSenha.value = false
    toastSucesso('Senha alterada com sucesso!')
  } catch (e) {
    erroSenha.value = e.response?.data?.detail || 'Erro ao alterar senha.'
  } finally {
    salvandoSenha.value = false
  }
}

function closeMobileDrawer() {
  if (window.innerWidth < NAV_DESKTOP) drawerOpen.value = false
}

const navItems = computed(() => {
  const items = [
    { to: '/agendamentos', icon: Calendar, label: 'Agendamentos' },
    { to: '/pagamentos', icon: CreditCard, label: 'Pagamentos' },
    { to: '/profissionais', icon: Scissors, label: 'Profissionais' },
    { to: '/servicos', icon: Sparkles, label: 'Serviços' },
    { to: '/produtos', icon: Package, label: 'Produtos' },
  ]
  if (auth.isAdmin) {
    items.push({ to: '/relatorios', icon: BarChart2, label: 'Relatórios' })
    items.push({ to: '/usuarios', icon: Users, label: 'Usuários' })
  }
  return items
})

// 4 principais na barra; o restante (Produtos + admin) no sheet "Mais"
const navItemsPrimary = computed(() => navItems.value.slice(0, 4))
const navItemsMore = computed(() => navItems.value.slice(4))
const isMoreRouteActive = computed(() =>
  navItemsMore.value.some((item) => route.path.startsWith(item.to)),
)
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>

