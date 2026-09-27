/* Aplica dark mode antes do render para evitar flash (arquivo externo = CSP script-src 'self'). */
if (localStorage.getItem('sgk_dark') === 'true') {
  document.documentElement.classList.add('dark')
}
