<template>
  <div>
    <h2 class="text-xl font-bold text-gray-800 mb-6">Relatórios — Google Sheets</h2>

    <div class="bg-white rounded-xl border border-gray-200 p-6 max-w-md">
      <p class="text-sm text-gray-500 mb-4">
        Exporta agendamentos e pagamentos do mês para a planilha mestre no Google Sheets.
        A operação é idempotente — os dados são sobrescritos a cada exportação.
      </p>
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Mês</label>
        <input
          v-model="mes"
          type="month"
          class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
        />
      </div>
      <button
        :disabled="loading || !mes"
        class="bg-rose-600 text-white text-sm font-semibold px-5 py-2 rounded-lg hover:bg-rose-700 disabled:opacity-50 transition-colors"
        @click="exportar"
      >
        {{ loading ? 'Exportando...' : 'Exportar' }}
      </button>

      <!-- Resultado -->
      <div v-if="resultado" class="mt-5 p-4 bg-green-50 border border-green-200 rounded-lg text-sm">
        <p class="font-semibold text-green-700 mb-2">Exportado com sucesso!</p>
        <ul class="text-green-700 space-y-1">
          <li>Mês: {{ resultado.mes_label }}</li>
          <li>Agendamentos: {{ resultado.agendamentos_exportados }}</li>
          <li>Pagamentos: {{ resultado.pagamentos_exportados }}</li>
        </ul>
        <a
          :href="resultado.spreadsheet_url"
          target="_blank"
          class="inline-block mt-3 text-rose-600 font-medium hover:underline"
        >
          Abrir planilha →
        </a>
      </div>

      <p v-if="erro" class="mt-4 text-sm text-red-600">{{ erro }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/client'

const mes = ref(new Date().toISOString().slice(0, 7))
const loading = ref(false)
const resultado = ref(null)
const erro = ref('')

async function exportar() {
  erro.value = ''
  resultado.value = null
  loading.value = true
  try {
    const { data } = await api.post('/relatorios/exportar', null, { params: { mes: mes.value } })
    resultado.value = data
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao exportar.'
  } finally {
    loading.value = false
  }
}
</script>
