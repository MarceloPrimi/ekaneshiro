import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

function resolveBaseURL() {
  const url = import.meta.env.VITE_API_URL
  if (url) return url
  if (import.meta.env.PROD) {
    throw new Error(
      'VITE_API_URL é obrigatória em produção. Defina a URL HTTPS da API no painel da Vercel.',
    )
  }
  return 'http://127.0.0.1:8000'
}

const api = axios.create({
  baseURL: resolveBaseURL(),
})

/** Token do Pinia ou localStorage (evita race no 1º paint após login/F5). */
export function getAuthToken() {
  try {
    const auth = useAuthStore()
    if (auth.token) return auth.token
  } catch {
    // Pinia ainda não ativo (raro)
  }
  return localStorage.getItem('sgk_token')
}

api.interceptors.request.use((config) => {
  const token = getAuthToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const hadAuth = Boolean(err.config?.headers?.Authorization)
    // Só desloga se o token FOI enviado e o servidor rejeitou (expirado/inválido).
    // 401 sem header = corrida no boot; deslogar aqui derrubava clientes/serviços em paralelo.
    if (
      err.response?.status === 401 &&
      hadAuth &&
      router.currentRoute.value.path !== '/login'
    ) {
      const auth = useAuthStore()
      auth.logout()
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default api
