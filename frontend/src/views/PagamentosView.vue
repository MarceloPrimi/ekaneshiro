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

    <!-- Filtros -->
    <div class="flex flex-wrap gap-3 mb-4">
      <select v-model="filtroStatus" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
        <option value="">Todos os status</option>
        <option value="pendente">Pendente</option>
        <option value="confirmado">Confirmado</option>
        <option value="concluido">Concluído</option>
        <option value="pre_agendamento">Pré-agendamento</option>
      </select>
      <div class="flex items-center gap-2">
        <label class="text-xs text-gray-500 font-medium">De</label>
        <input v-model="filtroDe" type="date" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-xs text-gray-500 font-medium">Até</label>
        <input v-model="filtroAte" type="date" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"/>
      </div>
      <button
        @click="filtroPendentePag = !filtroPendentePag; filtroStatus = ''"
        :class="['text-xs font-medium px-3 py-2 rounded-lg border transition-colors', filtroPendentePag ? 'bg-yellow-500 text-white border-yellow-500' : 'border-yellow-300 text-yellow-700 hover:bg-yellow-50']"
      >Pendentes de pagamento</button>
      <button
        v-if="filtroStatus || filtroDe !== hoje || filtroAte !== hoje || filtroPendentePag"
        @click="filtroStatus = ''; filtroDe = hoje; filtroAte = hoje; filtroPendentePag = false"
        class="text-xs text-gray-400 hover:text-gray-600 px-2 py-1 rounded"
      >✕ Limpar</button>
    </div>

    <!-- Tabela de agendamentos -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <div v-else-if="listaFiltrada.length === 0" class="p-8 text-center text-sm text-gray-400">Nenhum agendamento encontrado.</div>
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Cliente</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Serviços</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Total</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Status</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Pagamento</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="ag in listaFiltrada"
            :key="ag.id"
            :class="['hover:bg-gray-50 align-top', ag.status === 'concluido' && !ag.pagamento ? 'bg-red-50' : '']"
          >
            <td class="px-4 py-3 font-medium text-gray-800">{{ ag.cliente?.nome || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">
              <div v-for="item in ag.itens" :key="item.id" class="text-xs leading-5">
                {{ item.servico?.nome }} <span class="text-gray-400">· {{ item.profissional?.nome }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-sm font-semibold text-gray-700">R$ {{ totalAgendamento(ag) }}</td>
            <td class="px-4 py-3">
              <span :class="statusBadgeClass(ag.status)" class="text-xs font-semibold px-2.5 py-0.5 rounded-full">{{ statusLabel(ag.status) }}</span>
            </td>
            <td class="px-4 py-3">
              <div v-if="ag.pagamento" class="text-xs space-y-0.5">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span class="font-semibold text-green-700">R$ {{ Number(ag.pagamento.valor).toFixed(2) }}</span>
                  <span v-if="Number(ag.pagamento.credito_utilizado) > 0" class="text-indigo-700 bg-indigo-100 px-1.5 py-0.5 rounded font-medium">
                    Crédito: R$ {{ Number(ag.pagamento.credito_utilizado).toFixed(2) }}
                  </span>
                </div>
                <div class="text-gray-400">{{ metodoPagLabel(ag.pagamento.metodo) }}</div>
                <div class="text-gray-400">{{ formatDate(ag.pagamento.pago_em) }}</div>
              </div>
              <span v-else class="text-xs text-gray-300 italic">Não pago</span>
              <span v-if="ag.status === 'concluido' && !ag.pagamento"
                class="inline-block mt-1 text-xs font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-full">Inadimplente</span>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-col gap-1.5">
                <button
                  v-if="!ag.pagamento && ag.status !== 'cancelado' && ag.status !== 'pre_agendamento'"
                  @click="abrirComandaParaAgendamento(ag)"
                  :disabled="abrindoComanda === ag.id"
                  class="text-xs bg-rose-600 hover:bg-rose-700 text-white px-3 py-1.5 rounded-md font-medium disabled:opacity-50 flex items-center gap-1 transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                  </svg>
                  {{ abrindoComanda === ag.id ? 'Abrindo...' : 'Abrir comanda' }}
                </button>
                <button
                  v-if="ag.pagamento"
                  @click="abrirModalEditar(ag)"
                  class="text-xs bg-amber-500 hover:bg-amber-600 text-white px-3 py-1.5 rounded-md font-medium transition-colors"
                >Editar pagamento</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Comanda Modal (componente compartilhado) -->
    <ComandaModal
      v-model="comanda"
      :agendamentos="agendamentos"
      @fechada="fetchAgendamentos"
      @cancelada="fetchAgendamentos"
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
const filtroStatus = ref('')
const filtroPendentePag = ref(false)
const hoje = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' })
const filtroDe = ref(hoje)
const filtroAte = ref(hoje)
const mostrarTotal = ref(false)

// ── Comanda ───────────────────────────────────────────────────────────────────
const comanda = ref(null)
const abrindoComanda = ref(null) // id do agendamento em processamento

// ── Editar pagamento (legado) ─────────────────────────────────────────────────
const modalEditarAberto = ref(false)
const agEditarSelecionado = ref(null)
const savingEditar = ref(false)
const erroEditar = ref('')
const formEditar = ref({ valor: '', credito_utilizado: '0.00', metodo: '' })

// ── Computed ──────────────────────────────────────────────────────────────────

const totalRecebido = computed(() =>
  listaFiltrada.value
    .filter(ag => ag.pagamento)
    .reduce((sum, ag) => sum + Number(ag.pagamento?.valor || 0), 0)
    .toFixed(2)
)

const listaFiltrada = computed(() =>
  agendamentos.value.filter(ag => {
    if (filtroPendentePag.value && ag.pagamento) return false
    if (filtroStatus.value && ag.status !== filtroStatus.value) return false
    if (filtroDe.value || filtroAte.value) {
      const dataRef = ag.itens?.[0]?.data_hora_inicio ?? ag.criado_em
      const d = new Date(dataRef)
      const dSemHora = new Date(d.getFullYear(), d.getMonth(), d.getDate())
      if (filtroDe.value && dSemHora < new Date(filtroDe.value + 'T00:00:00')) return false
      if (filtroAte.value && dSemHora > new Date(filtroAte.value + 'T23:59:59')) return false
    }
    return true
  })
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

let _debounce
watch([filtroDe, filtroAte], () => {
  clearTimeout(_debounce)
  _debounce = setTimeout(fetchAgendamentos, 250)
})

// ── Abrir comanda ─────────────────────────────────────────────────────────────

/** Abre comanda do zero (sem agendamento). */
async function novaComandaVazia() {
  try {
    const { data } = await api.post('/comandas/', {})
    comanda.value = { ...data, itens: [], pagamentos: [], total_itens: '0.00', total_pago: '0.00', saldo_restante: '0.00' }
  } catch (e) {
    console.error('Erro ao criar comanda:', e)
  }
}

/**
 * Performance fix: exibe o modal logo após criar a comanda (~1.5s),
 * sem esperar o add de itens e o reload (~5s no total).
 * Os itens são adicionados em background com um spinner visível.
 */
async function abrirComandaParaAgendamento(ag) {
  abrindoComanda.value = ag.id
  try {
    // Passo 1: cria comanda → modal aparece imediatamente
    const { data: nova } = await api.post('/comandas/', {})
    comanda.value = {
      ...nova,
      itens: [], pagamentos: [],
      total_itens: '0.00', total_pago: '0.00', saldo_restante: '0.00',
      _carregando: true, // exibe spinner dentro do modal
    }
    abrindoComanda.value = null

    // Passo 2+3: adiciona itens e recarrega (enquanto modal já está visível)
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

function statusLabel(s) {
  return { pendente: 'Pendente', confirmado: 'Confirmado', concluido: 'Concluído', pre_agendamento: 'Pré-agendamento', cancelado: 'Cancelado' }[s] ?? s
}

function statusBadgeClass(s) {
  return { pendente: 'bg-gray-600 text-gray-100', confirmado: 'bg-green-700 text-white', concluido: 'bg-blue-700 text-white', pre_agendamento: 'bg-red-700 text-white', cancelado: 'bg-red-700 text-white' }[s] ?? 'bg-gray-500 text-white'
}

function metodoPagLabel(m) {
  return { dinheiro: 'Dinheiro', pix: 'PIX', cartao_credito: 'Cartão Crédito', cartao_debito: 'Cartão Débito' }[m] ?? m
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' })
}

// ── Lifecycle ─────────────────────────────────────────────────────────────────
const lastFetchAt = ref(0)
const STALE_MS = 5 * 60 * 1000

onMounted(() => { fetchAgendamentos(); lastFetchAt.value = Date.now() })
onActivated(() => {
  if (lastFetchAt.value && Date.now() - lastFetchAt.value > STALE_MS) {
    fetchAgendamentos(); lastFetchAt.value = Date.now()
  }
})
</script>
