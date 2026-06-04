import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('sgk_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('sgk_user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username, senha) {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', senha)
    // /login-full retorna token + dados do usuário em 1 round-trip (elimina /me sequencial)
    const { data } = await api.post('/usuarios/login-full', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    token.value = data.access_token
    localStorage.setItem('sgk_token', data.access_token)
    user.value = data.user
    localStorage.setItem('sgk_user', JSON.stringify(data.user))
  }

  async function fetchMe() {
    const { data } = await api.get('/usuarios/me')
    user.value = data
    localStorage.setItem('sgk_user', JSON.stringify(data))
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('sgk_token')
    localStorage.removeItem('sgk_user')
  }

  return { token, user, isAuthenticated, isAdmin, login, logout, fetchMe }
})
