<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 w-full max-w-sm p-8">

      <!-- Brand -->
      <div class="mb-8">
        <h1 class="text-2xl font-semibold tracking-wide text-gray-900">Sanshin</h1>
        <p class="text-sm text-gray-400 mt-0.5">Beleza e gestão</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1.5">E-mail</label>
          <input
            v-model="form.email"
            type="email"
            required
            autocomplete="email"
            class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-transparent transition"
            placeholder="seu@email.com"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1.5">Senha</label>
          <input
            v-model="form.senha"
            type="password"
            required
            autocomplete="current-password"
            class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-transparent transition"
          />
        </div>
        <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-rose-600 text-white rounded-lg py-2.5 text-sm font-medium hover:bg-rose-700 disabled:opacity-50 transition-colors mt-2"
        >
          {{ loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = reactive({ email: '', senha: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.email, form.senha)
    router.push('/agendamentos')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erro ao fazer login.'
  } finally {
    loading.value = false
  }
}
</script>
