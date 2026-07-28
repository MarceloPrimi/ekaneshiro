<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
      <h2 class="text-xl font-bold text-gray-800">Pagamentos</h2>
      <button
        @click="novaComandaVazia"
        class="flex items-center gap-2 text-sm bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Nova comanda
      </button>
    </div>

    <!-- Card Total -->
    <div class="flex items-center gap-3 mb-5 bg-white border border-gray-200 rounded-xl px-5 py-3 w-fit shadow-sm">
      <div>
        <p class="text-xs text-gray-400 font-medium uppercase tracking-wide">Total recebido (filtro atual)</p>
        <p class="text-2xl font-bold text-gray-800 mt-0.5">
          <span v-if="mostrarTotal">R$ {{ totalRecebido }}</span>
          <span v-else class="tracking-[0.25em] text-gray-400 text-xl select-none">••••••</span>
        </p>
      </div>
      <button @click="mostrarTotal = !mostrarTotal" class="ml-2 p-2 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors" type="button">
        <svg v-if="mostrarTotal" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 012.163-3.592m3.08-2.634A9.954 9.954 0 0112 5c4.477 0 8.268 2.943 9.542 7a9.966 9.966 0 01-1.357 2.716M3 3l18 18"/>
        </svg>
      </button>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         SEÇÃO 1: COMANDAS
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
        <div class="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-rose-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
          <h3 class="text-lg font-bold text-gray-800">Comandas</h3>
          <span v-if="comandasFiltradas.length" class="bg-rose-100 text-rose-700 text-xs font-bold px-2 py-0.5 rounded-full">{{ comandasFiltradas.length }}</span>
        </div>
        <div class="flex items-center gap-2 flex-wrap">
          <input 
            v-model="filtroComandaData" 
            type="date" 
            class="border border-gray-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-rose-400"
          />
          <select 
            v-model="filtroComandaStatus" 
            class="border border-gray-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-rose-400"
          >
            <option value="">Todos</option>
            <option value="pendente">Pendentes</option>
            <option value="pago">Pagos</option>
          </select>
          <button @click="fetchComandas" class="text-xs text-gray-400 hover:text-gray-600 p-1.5">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
        </div>
      </div>
      
      <div v-if="loadingComandas" class="text-sm text-gray-400 p-4">Carregando comandas...</div>
      <div v-else-if="comandasFiltradas.length === 0" class="bg-gray-50 rounded-xl border border-gray-100 p-6 text-center text-sm text-gray-400">
        Nenhuma comanda encontrada para o filtro selecionado.
      </div>
      <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <div 
          v-for="c in comandasFiltradas" 
          :key="c.id" 
          @click="abrirComanda(c)"
          class="bg-white border border-gray-200 rounded-xl p-4 hover:border-rose-300 hover:shadow-md cursor-pointer transition-all"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-rose-600">#{{ String(c.id).padStart(4, '0') }}</span>
              <span 
                :class="c.status === 'fechada' ? 'bg-green-100 text-green-700' : c.status === 'cancelada' ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'"
                class="text-xs font-medium px-1.5 py-0.5 rounded"
              >{{ c.status === 'fechada' ? 'Fechada' : c.status === 'cancelada' ? 'Cancelada' : 'Aberta' }}</span>
            </div>
            <span class="text-xs text-gray-400">{{ formatDateShort(c.aberta_em) }}</span>
          </div>
          <div class="space-y-1 mb-3">
            <div v-for="item in c.itens?.slice(0, 3)" :key="item.id" class="text-xs text-gray-600">
              <span class="font-medium">{{ item.servico?.nome || item.descricao }}</span>
              <span class="text-gray-400"> · {{ item.cliente?.nome }}</span>
            </div>
            <div v-if="c.itens?.length > 3" class="text-xs text-gray-400 italic">
              +{{ c.itens.length - 3 }} itens
            </div>
          </div>
          <div class="flex items-center justify-between pt-2 border-t border-gray-100">
            <div class="text-xs">
              <span class="text-gray-500">Total:</span>
              <span class="font-bold text-gray-800 ml-1">R$ {{ fmt(c.total_itens) }}</span>
            </div>
            <div v-if="c.status === 'cancelada'" class="text-xs text-gray-400">—</div>
            <div v-else-if="Number(c.total_itens) === 0" class="text-xs text-gray-400 italic">Sem itens</div>
            <div v-else-if="Number(c.saldo_restante) > 0" class="text-xs">
              <span class="text-amber-600 font-semibold">Falta: R$ {{ fmt(c.saldo_restante) }}</span>
            </div>
            <div v-else class="text-xs text-green-600 font-semibold">Pago ✓</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         SEÇÃO 2: PAGAMENTOS PENDENTES (Agendamentos sem pagamento)
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div class="mb-8">
      <div class="flex items-center gap-2 mb-3">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <h3 class="text-lg font-bold text-gray-800">Pagamentos Pendentes</h3>
        <span v-if="pagamentosPendentes.length" class="bg-amber-100 text-amber-700 text-xs font-bold px-2 py-0.5 rounded-full">{{ pagamentosPendentes.length }}</span>
      </div>
      
      <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
        <div v-else-if="pagamentosPendentes.length === 0" class="p-6 text-center text-sm text-gray-400">
          Nenhum agendamento pendente de pagamento.
        </div>
        <div v-else class="divide-y divide-gray-100">
          <div 
            v-for="ag in pagamentosPendentes" 
            :key="ag.id"
            class="flex items-center justify-between px-4 py-3 hover:bg-gray-50"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-sm font-semibold text-gray-800">{{ ag.cliente?.nome }}</span>
                <span :class="statusBadgeClass(ag.status)" class="text-xs font-semibold px-2 py-0.5 rounded-full">{{ statusLabel(ag.status) }}</span>
              </div>
              <div class="text-xs text-gray-500 mt-0.5">
                {{ ag.itens?.map(i => i.servico?.nome).join(', ') }}
              </div>
              <div class="text-xs text-gray-400 mt-0.5">
                {{ formatDate(ag.itens?.[0]?.data_hora_inicio) }}
              </div>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0 ml-3">
              <div class="text-right">
                <div class="text-sm font-bold text-gray-800">R$ {{ totalAgendamento(ag) }}</div>
              </div>
              <button
                @click="abrirComandaParaAgendamento(ag)"
                :disabled="abrindoComanda === ag.id"
                class="text-xs bg-rose-600 hover:bg-rose-700 text-white px-3 py-1.5 rounded-lg font-medium disabled:opacity-50 transition-colors whitespace-nowrap"
              >
                {{ abrindoComanda === ag.id ? 'Abrindo...' : 'Abrir comanda' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════════════════
         SEÇÃO 3: HISTÓRICO DE AGENDAMENTOS (Pagos)
         ═══════════════════════════════════════════════════════════════════════════ -->
    <div>
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <h3 class="text-lg font-bold text-gray-800">Histórico de Pagamentos</h3>
        </div>
        <div class="flex items-center gap-2">
          <input v-model="filtroDe" type="date" class="border border-gray-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-rose-400"/>
          <span class="text-xs text-gray-400">até</span>
          <input v-model="filtroAte" type="date" class="border border-gray-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-rose-400"/>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
        <div v-else-if="agendamentosPagos.length === 0" class="p-6 text-center text-sm text-gray-400">
          Nenhum pagamento registrado no período.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Cliente</th>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Serviços</th>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Valor</th>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Método</th>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Data</th>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="ag in agendamentosPagos" :key="ag.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-800">{{ ag.cliente?.nome || '-' }}</td>
              <td class="px-4 py-3 text-gray-600">
                <div v-for="item in ag.itens" :key="item.id" class="text-xs leading-5">
                  {{ item.servico?.nome }}
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="font-semibold text-green-700">R$ {{ Number(ag.pagamento?.valor || 0).toFixed(2) }}</span>
                <span v-if="Number(ag.pagamento?.credito_utilizado) > 0" class="block text-xs text-indigo-600">
                  (crédito: R$ {{ Number(ag.pagamento.credito_utilizado).toFixed(2) }})
                </span>
              </td>
              <td class="px-4 py-3 text-gray-600 text-xs">{{ metodoPagLabel(ag.pagamento?.metodo) }}</td>
              <td class="px-4 py-3 text-gray-400 text-xs">{{ formatDate(ag.pagamento?.pago_em) }}</td>
              <td class="px-4 py-3">
                <button
                  @click="abrirModalEditar(ag)"
                  class="text-xs text-amber-600 hover:text-amber-700 font-medium"
                >Editar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Comanda Modal (componente compartilhado) -->
    <ComandaModal
      v-model="comanda"
      :agendamentos="agendamentos"
      @fechada="onComandaFechada"
      @cancelada="onComandaCancelada"
    />

    <!-- Modal Editar Pagamento (legado) -->
    <div v-if="modalEditarAberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-1">Editar Pagamento</h3>
        <p class="text-sm text-gray-500 mb-4">#{{ agEditarSelecionado?.id }} · {{ agEditarSelecionado?.cliente?.nome }}</p>
        <p class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mb-4">
          Atenção: corrige o registro sem recalcular saldo de crédito.
        </p>
        <form @submit.prevent="confirmarEdicaoPagamento" class="space-y-4">
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Valor (R$) *</label>
              <input v-model="formEditar.valor" type="number" step="0.01" min="0.01" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"/>
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Crédito utilizado</label>
              <input v-model="formEditar.credito_utilizado" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"/>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Método *</label>
            <select v-model="formEditar.metodo" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400">
              <option value="">Selecione...</option>
              <option value="dinheiro">Dinheiro</option>
              <option value="pix">PIX</option>
              <option value="cartao_credito">Cartão de Crédito</option>
              <option value="cartao_debito">Cartão de Débito</option>
            </select>
          </div>
          <p v-if="erroEditar" class="text-sm text-red-600">{{ erroEditar }}</p>
          <div class="flex gap-3 pt-1">
            <button type="button" @click="modalEditarAberto = false" class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50">Cancelar</button>
            <button type="submit" :disabled="savingEditar" class="flex-1 bg-amber-500 hover:bg-amber-600 text-white rounded-lg py-2 text-sm font-semibold disabled:opacity-50">
              {{ savingEditar ? 'Salvando...' : 'Salvar correção' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated } from 'vue'
import api from '@/api/client'
import { useToast } from '@/composables/useToast'
import ComandaModal from '@/components/ComandaModal.vue'

defineOptions({ name: 'PagamentosView' })

const { sucesso: toastSucesso } = useToast()

// ── Agendamentos ──────────────────────────────────────────────────────────────
const agendamentos = ref([])
const loading = ref(true)
const hoje = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' })
const filtroDe = ref(hoje)
const filtroAte = ref(hoje)
const mostrarTotal = ref(false)

// ── Comandas ───────────────────────────────────────────────────────────────────
const comandas = ref([])
const loadingComandas = ref(false)
const comanda = ref(null)
const abrindoComanda = ref(null)

// ── Filtros de Comandas ────────────────────────────────────────────────────────
const filtroComandaData = ref(hoje)
const filtroComandaStatus = ref('pendente')

// ── Editar pagamento (legado) ─────────────────────────────────────────────────
const modalEditarAberto = ref(false)
const agEditarSelecionado = ref(null)
const savingEditar = ref(false)
const erroEditar = ref('')
const formEditar = ref({ valor: '', credito_utilizado: '0.00', metodo: '' })

// ── Computed ──────────────────────────────────────────────────────────────────

const comandasFiltradas = computed(() => comandas.value)

const pagamentosPendentes = computed(() =>
  agendamentos.value.filter(ag => 
    !ag.pagamento && 
    ag.status !== 'cancelado' && 
    ag.status !== 'pre_agendamento'
  )
)

const agendamentosPagos = computed(() =>
  agendamentos.value.filter(ag => ag.pagamento)
)

const totalRecebido = computed(() =>
  agendamentosPagos.value
    .reduce((sum, ag) => sum + Number(ag.pagamento?.valor || 0), 0)
    .toFixed(2)
)

// ── Fetch ─────────────────────────────────────────────────────────────────────

async function fetchAgendamentos() {
  loading.value = true
  const params = {}
  if (filtroDe.value) params.data_inicio = filtroDe.value
  if (filtroAte.value) params.data_fim = filtroAte.value
  try {
    const { data } = await api.get('/agendamentos/', { params })
    agendamentos.value = data
  } finally {
    loading.value = false
  }
}

async function fetchComandas() {
  loadingComandas.value = true
  try {
    const params = new URLSearchParams()
    if (filtroComandaData.value) {
      params.append('data_inicio', filtroComandaData.value)
      params.append('data_fim', filtroComandaData.value)
    }
    if (filtroComandaStatus.value) {
      params.append('pago_filtro', filtroComandaStatus.value)
    }
    const { data } = await api.get(`/comandas/?${params.toString()}`)
    comandas.value = data
  } finally {
    loadingComandas.value = false
  }
}

let _debounce
watch([filtroDe, filtroAte], () => {
  clearTimeout(_debounce)
  _debounce = setTimeout(fetchAgendamentos, 250)
})

let _debounceComandas
watch([filtroComandaData, filtroComandaStatus], () => {
  clearTimeout(_debounceComandas)
  _debounceComandas = setTimeout(fetchComandas, 250)
})

// ── Abrir comanda ─────────────────────────────────────────────────────────────

async function novaComandaVazia() {
  try {
    const { data } = await api.post('/comandas/', {})
    comanda.value = { ...data, itens: [], pagamentos: [], total_itens: '0.00', total_pago: '0.00', saldo_restante: '0.00' }
  } catch (e) {
    console.error('Erro ao criar comanda:', e)
  }
}

async function abrirComanda(c) {
  try {
    const { data } = await api.get(`/comandas/${c.id}`)
    comanda.value = data
  } catch (e) {
    console.error('Erro ao abrir comanda:', e)
  }
}

async function abrirComandaParaAgendamento(ag) {
  abrindoComanda.value = ag.id
  try {
    const { data: nova } = await api.post('/comandas/', {})
    comanda.value = {
      ...nova,
      itens: [], pagamentos: [],
      total_itens: '0.00', total_pago: '0.00', saldo_restante: '0.00',
      _carregando: true,
    }
    abrindoComanda.value = null

    await api.post(`/comandas/${nova.id}/itens/agendamento`, {
      agendamento_id: ag.id,
      cliente_id: ag.cliente_id,
    })
    const { data } = await api.get(`/comandas/${nova.id}`)
    comanda.value = data
  } catch (e) {
    abrindoComanda.value = null
    if (comanda.value) {
      comanda.value = { ...comanda.value, _carregando: false }
    }
  }
}

function onComandaFechada() {
  fetchAgendamentos()
  fetchComandas()
}

function onComandaCancelada() {
  fetchAgendamentos()
  fetchComandas()
}

// ── Editar pagamento legado ───────────────────────────────────────────────────

function abrirModalEditar(ag) {
  agEditarSelecionado.value = ag
  formEditar.value = { valor: ag.pagamento?.valor ?? '', credito_utilizado: ag.pagamento?.credito_utilizado ?? '0.00', metodo: ag.pagamento?.metodo ?? '' }
  erroEditar.value = ''
  modalEditarAberto.value = true
}

async function confirmarEdicaoPagamento() {
  savingEditar.value = true
  erroEditar.value = ''
  try {
    await api.put(`/agendamentos/${agEditarSelecionado.value.id}/pagamento`, {
      valor: formEditar.value.valor,
      metodo: formEditar.value.metodo,
      credito_utilizado: formEditar.value.credito_utilizado || 0,
    })
    modalEditarAberto.value = false
    toastSucesso('Pagamento corrigido com sucesso!')
    await fetchAgendamentos()
  } catch (e) {
    erroEditar.value = e.response?.data?.detail || 'Erro ao editar pagamento.'
  } finally {
    savingEditar.value = false
  }
}

// ── Utilitários ───────────────────────────────────────────────────────────────

function totalAgendamento(ag) {
  return (ag?.itens ?? []).reduce((s, i) => s + Number(i.servico?.preco || 0), 0).toFixed(2)
}

function fmt(v) {
  return Number(v || 0).toFixed(2)
}

function statusLabel(s) {
  return { pendente: 'Pendente', confirmado: 'Confirmado', concluido: 'Concluído', pre_agendamento: 'Pré-agendamento', cancelado: 'Cancelado' }[s] ?? s
}

function statusBadgeClass(s) {
  return { pendente: 'bg-red-600 text-white', confirmado: 'bg-green-700 text-white', concluido: 'bg-blue-700 text-white', pre_agendamento: 'bg-red-700 text-white', cancelado: 'bg-red-700 text-white' }[s] ?? 'bg-gray-500 text-white'
}

function metodoPagLabel(m) {
  return { dinheiro: 'Dinheiro', pix: 'PIX', cartao_credito: 'Cartão Crédito', cartao_debito: 'Cartão Débito' }[m] ?? m
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' })
}

function formatDateShort(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' })
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
const lastFetchAt = ref(0)
const STALE_MS = 5 * 60 * 1000

onMounted(() => { 
  fetchAgendamentos()
  fetchComandas()
  lastFetchAt.value = Date.now() 
})

onActivated(() => {
  if (lastFetchAt.value && Date.now() - lastFetchAt.value > STALE_MS) {
    fetchAgendamentos()
    fetchComandas()
    lastFetchAt.value = Date.now()
  }
})
</script>
