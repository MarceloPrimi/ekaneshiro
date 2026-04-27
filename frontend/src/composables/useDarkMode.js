import { ref, watchEffect } from 'vue'

// Singleton — estado compartilhado entre todos os componentes
const dark = ref(localStorage.getItem('sgk_dark') === 'true')

// Sincroniza a classe no <html> sempre que o valor muda
watchEffect(() => {
  document.documentElement.classList.toggle('dark', dark.value)
  localStorage.setItem('sgk_dark', String(dark.value))
})

export function useDarkMode() {
  function toggle() {
    dark.value = !dark.value
  }
  return { dark, toggle }
}
