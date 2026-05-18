<template>
  <div>
    <h2 class="text-xl font-bold text-gray-800 mb-6">Relatórios</h2>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Exportação Google Sheets -->
      <div class="bg-white rounded-xl border border-gray-200 p-6">
        <h3 class="text-base font-semibold text-gray-800 mb-1">Google Sheets – Exportar mês</h3>
        <p class="text-sm text-gray-500 mb-4">
          Exporta agendamentos e pagamentos do mês para a planilha mestre.
          A operação é idempotente – os dados são sobrescritos a cada exportação.
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

        <div v-if="resultado" class="mt-5 p-4 bg-green-50 border border-green-200 rounded-lg text-sm">
          <p class="font-semibold text-green-700 mb-2">Exportado com sucesso!</p>
          <ul class="text-green-700 space-y-1">
            <li>Mês: {{ resultado.mes_label }}</li>
            <li>Agendamentos: {{ resultado.agendamentos_exportados }}</li>
            <li>Pagamentos: {{ resultado.pagamentos_exportados }}</li>
          </ul>
          <a :href="resultado.spreadsheet_url" target="_blank" class="inline-block mt-3 text-rose-600 font-medium hover:underline">
            Abrir planilha →
          </a>
        </div>
        <p v-if="erro" class="mt-4 text-sm text-red-600">{{ erro }}</p>
      </div>

      <!-- Clientes únicos por profissional -->
      <div class="bg-white rounded-xl border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-base font-semibold text-gray-800">Clientes únicos por profissional</h3>
          <button
            class="text-xs text-rose-600 hover:underline font-medium"
            :disabled="loadingMetricas"
            @click="fetchMetricas"
          >
            {{ loadingMetricas ? 'Carregando...' : '↺ Atualizar' }}
          </button>
        </div>
        <p class="text-xs text-gray-400 mb-4">Baseado em agendamentos com status "Concluído".</p>
        <div v-if="loadingMetricas" class="py-6 text-center text-sm text-gray-400">Carregando...</div>
        <div v-else-if="!metricas.length" class="py-6 text-center text-sm text-gray-400">Nenhum dado disponível.</div>
        <div v-else class="space-y-3">
          <div
            v-for="(m, i) in metricas"
            :key="m.profissional_id"
            class="flex items-center gap-3"
          >
            <span class="text-xs text-gray-400 w-4 text-right">{{ i + 1 }}</span>
            <div class="flex-1">
              <div class="flex items-center justify-between mb-1">
                <span class="text-sm font-medium text-gray-700">{{ m.profissional_nome }}</span>
                <span class="text-sm font-bold text-rose-600">{{ m.clientes_unicos }}</span>
              </div>
              <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-2 bg-rose-400 rounded-full transition-all"
                  :style="{ width: maxClientes ? (m.clientes_unicos / maxClientes * 100) + '%' : '0%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Faturamento por profissional -->
      <div class="bg-white rounded-xl border border-gray-200 p-6 lg:col-span-2">
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h3 class="text-base font-semibold text-gray-800">Faturamento por profissional</h3>
            <p class="text-xs text-gray-400 mt-0.5">Serviços concluídos · preço próprio do profissional (ou padrão do catálogo)</p>
          </div>
          <div class="flex items-center gap-2">
            <input
              v-model="mesFaturamento"
              type="month"
              class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
            <button
              class="text-xs text-rose-600 hover:underline font-medium"
              :disabled="loadingFaturamento"
              @click="fetchFaturamento"
            >
              {{ loadingFaturamento ? 'Carregando...' : '↺' }}
            </button>
          </div>
        </div>

        <div v-if="loadingFaturamento" class="py-8 text-center text-sm text-gray-400">Carregando...</div>
        <div v-else-if="!faturamento" class="py-8 text-center text-sm text-gray-400">Selecione um mês e clique em atualizar.</div>
        <div v-else-if="!faturamento.por_profissional.length" class="py-8 text-center text-sm text-gray-400">
          Nenhum atendimento concluído em {{ faturamento.mes }}.
        </div>
        <div v-else>
          <div class="flex items-baseline gap-2 mb-5 pb-4 border-b border-gray-100">
            <span class="text-3xl font-bold text-gray-900">{{ formatCurrency(faturamento.total_geral) }}</span>
            <span class="text-sm text-gray-500">total em {{ faturamento.mes }}</span>
            <span class="ml-auto text-xs text-gray-400">
              {{ faturamento.por_profissional.reduce((s, p) => s + p.atendimentos, 0) }} atendimentos
            </span>
          </div>
          <div class="space-y-4">
            <div
              v-for="p in faturamento.por_profissional"
              :key="p.profissional_id"
            >
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-2 min-w-0">
                  <span class="text-sm font-medium text-gray-800 truncate">{{ p.profissional_nome }}</span>
                  <span class="text-xs text-gray-400 flex-shrink-0">{{ p.atendimentos }} atend.</span>
                </div>
                <span class="text-sm font-bold text-gray-700 flex-shrink-0 ml-3">{{ formatCurrency(p.total) }}</span>
              </div>
              <div class="h-2.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-2.5 rounded-full transition-all duration-500"
                  :style="{
                    width: faturamento.total_geral ? (p.total / faturamento.total_geral * 100) + '%' : '0%',
                    backgroundColor: profissionalColor(p.profissional_id),
                  }"
                ></div>
              </div>
              <div class="text-right text-xs text-gray-400 mt-0.5">
                {{ faturamento.total_geral ? ((p.total / faturamento.total_geral) * 100).toFixed(1) : 0 }}% do total
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
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

const metricas = ref([])
const loadingMetricas = ref(false)
const maxClientes = computed(() => metricas.value.reduce((max, m) => Math.max(max, m.clientes_unicos), 0))

async function fetchMetricas() {
  loadingMetricas.value = true
  try {
    const { data } = await api.get('/relatorios/clientes-por-profissional')
    metricas.value = data
  } catch (e) {
    console.error('Erro ao carregar métricas:', e)
  } finally {
    loadingMetricas.value = false
  }
}

const mesFaturamento = ref(new Date().toISOString().slice(0, 7))
const faturamento = ref(null)
const loadingFaturamento = ref(false)

async function fetchFaturamento() {
  loadingFaturamento.value = true
  try {
    const { data } = await api.get('/relatorios/faturamento', { params: { mes: mesFaturamento.value } })
    faturamento.value = data
  } catch (e) {
    console.error('Erro ao carregar faturamento:', e)
  } finally {
    loadingFaturamento.value = false
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

const COLORS = ['#e11d48', '#7c3aed', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
function profissionalColor(id) {
  return COLORS[id % COLORS.length]
}

onMounted(() => {
  fetchMetricas()
  fetchFaturamento()
})
</script>