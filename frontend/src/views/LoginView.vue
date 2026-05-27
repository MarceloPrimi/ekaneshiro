<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="bg-white rounded-2xl shadow-sm border border-gray-200 w-full max-w-sm p-8">

      <!-- Brand -->
      <div class="mb-8 flex justify-center items-center pt-2 pb-1">
        <img
          src="/logo.png"
          alt="Logo Sanshin"
          class="block w-36 h-36 object-contain object-center"
        />
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1.5">Usuário</label>
          <input
            v-model="form.username"
            type="text"
            required
            autocomplete="username"
            class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300 focus:border-transparent transition"
            placeholder="seu_usuario"
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
const form = reactive({ username: '', senha: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(form.username, form.senha)
    router.push('/agendamentos')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erro ao fazer login.'
  } finally {
    loading.value = false
  }
}
</script>
