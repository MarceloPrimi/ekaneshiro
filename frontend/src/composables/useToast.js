import { ref } from 'vue'

// Estado compartilhado no nível do módulo — uma única instância em toda a app
const _toasts = ref([])
let _nextId = 0

export function useToast() {
  function sucesso(msg = 'Salvo com sucesso!') {
    const id = ++_nextId
    _toasts.value.push({ id, msg, type: 'success' })
    setTimeout(() => {
      _toasts.value = _toasts.value.filter(t => t.id !== id)
    }, 3000)
  }

  function erro(msg = 'Erro ao executar ação.') {
    const id = ++_nextId
    _toasts.value.push({ id, msg, type: 'error' })
    setTimeout(() => {
      _toasts.value = _toasts.value.filter(t => t.id !== id)
    }, 4000)
  }

  return { toasts: _toasts, sucesso, erro }
}
