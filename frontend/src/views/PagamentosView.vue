<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-800">Pagamentos</h2>
    </div>

    <!-- Card Total -->
    <div class="flex items-center gap-3 mb-5 bg-white border border-gray-200 rounded-xl px-5 py-3 w-fit shadow-sm">
      <div>
        <p class="text-xs text-gray-400 font-medium uppercase tracking-wide">Total recebido (filtro atual)</p>
        <p class="text-2xl font-bold text-gray-800 mt-0.5 transition-all">
          <span v-if="mostrarTotal">R$ {{ totalRecebido }}</span>
          <span v-else class="tracking-[0.25em] text-gray-400 text-xl select-none">••••••</span>
        </p>
      </div>
      <button
        @click="mostrarTotal = !mostrarTotal"
        class="ml-2 p-2 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
        :title="mostrarTotal ? 'Ocultar valor' : 'Mostrar valor'"
        type="button"
      >
        <svg v-if="mostrarTotal" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 012.163-3.592m3.08-2.634A9.954 9.954 0 0112 5c4.477 0 8.268 2.943 9.542 7a9.966 9.966 0 01-1.357 2.716M3 3l18 18" />
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
        <option value="cancelado">Cancelado</option>
      </select>
      <div class="flex items-center gap-2">
        <label class="text-xs text-gray-500 font-medium">De</label>
        <input v-model="filtroDe" type="date" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
      </div>
      <div class="flex items-center gap-2">
        <label class="text-xs text-gray-500 font-medium">Até</label>
        <input v-model="filtroAte" type="date" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
      </div>
      <button
        @click="filtroPendentePag = !filtroPendentePag; filtroStatus = ''"
        :class="[
          'text-xs font-medium px-3 py-2 rounded-lg border transition-colors',
          filtroPendentePag ? 'bg-yellow-500 text-white border-yellow-500' : 'border-yellow-300 text-yellow-700 hover:bg-yellow-50',
        ]"
      >Pendentes de pagamento</button>
      <button v-if="filtroStatus || filtroDe !== hoje || filtroAte !== hoje || filtroPendentePag" @click="filtroStatus = ''; filtroDe = hoje; filtroAte = hoje; filtroPendentePag = false" class="text-xs text-gray-400 hover:text-gray-600 px-2 py-1 rounded">✕ Limpar</button>
    </div>

    <!-- Tabela -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <div v-else-if="listaFiltrada.length === 0" class="p-8 text-center text-sm text-gray-400">
        Nenhum agendamento encontrado.
      </div>
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
            :class="[
              'hover:bg-gray-50 align-top',
              ag.status === 'concluido' && !ag.pagamento ? 'bg-red-50' : '',
            ]"
          >
            <td class="px-4 py-3 font-medium text-gray-800">{{ ag.cliente?.nome || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">
              <div v-for="item in ag.itens" :key="item.id" class="text-xs leading-5">
                {{ item.servico?.nome }}
                <span class="text-gray-400">· {{ item.profissional?.nome }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-sm font-semibold text-gray-700">
              R$ {{ totalAgendamento(ag) }}
            </td>
            <td class="px-4 py-3">
              <span :class="statusBadgeClass(ag.status)" class="text-xs font-semibold px-2.5 py-0.5 rounded-full">{{ statusLabel(ag.status) }}</span>
            </td>
            <td class="px-4 py-3">
              <div v-if="ag.pagamento" class="text-xs space-y-0.5">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span class="font-semibold text-green-700">R$ {{ Number(ag.pagamento.valor).toFixed(2) }}</span>
                  <span
                    v-if="Number(ag.pagamento.valor) < Number(totalAgendamento(ag)) && !ag.pagamento.credito_utilizado"
                    class="text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded font-medium"
                    :title="'Total original: R$ ' + totalAgendamento(ag)"
                  >-R$ {{ (Number(totalAgendamento(ag)) - Number(ag.pagamento.valor)).toFixed(2) }}</span>
                  <span
                    v-if="ag.pagamento.credito_utilizado && Number(ag.pagamento.credito_utilizado) > 0"
                    class="text-indigo-700 bg-indigo-100 px-1.5 py-0.5 rounded font-medium"
                    :title="'Crédito utilizado'"
                  >Crédito: R$ {{ Number(ag.pagamento.credito_utilizado).toFixed(2) }}</span>
                </div>
                <div class="text-gray-400">{{ metodoPagLabel(ag.pagamento.metodo) }}</div>
                <div class="text-gray-400">{{ formatDate(ag.pagamento.pago_em) }}</div>
              </div>
              <span v-else class="text-xs text-gray-300 italic">Não pago</span>
              <span
                v-if="ag.status === 'concluido' && !ag.pagamento"
                class="inline-block mt-1 text-xs font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-full"
              >Inadimplente</span>
            </td>
            <td class="px-4 py-3">
              <button
                v-if="!ag.pagamento && ag.status !== 'cancelado'"
                @click="abrirModal(ag)"
                class="text-xs bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-md font-medium"
              >
                Registrar pagamento
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Pagamento -->
    <div v-if="modalAberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-1">Registrar Pagamento</h3>
        <p class="text-sm text-gray-500 mb-4">
          Agendamento <strong>#{{ agSelecionado?.id }}</strong> · {{ agSelecionado?.cliente?.nome }}
        </p>

        <!-- Breakdown dos serviços -->
        <div class="bg-gray-50 rounded-lg p-3 mb-4 space-y-1">
          <div
            v-for="item in agSelecionado?.itens"
            :key="item.id"
            class="flex justify-between items-center text-xs text-gray-600"
          >
            <span>{{ item.servico?.nome }}</span>
            <button
              type="button"
              class="text-xs font-semibold text-rose-600 hover:underline ml-2"
              @click="setValorBase(item.servico?.preco)"
            >R$ {{ Number(item.servico?.preco).toFixed(2) }}</button>
          </div>
          <div class="border-t border-gray-200 pt-1 flex justify-between items-center text-sm font-bold text-gray-800">
            <span>Total</span>
            <button
              type="button"
              class="font-bold text-gray-800 hover:text-rose-600 transition-colors"
              @click="setValorBase(totalAgendamento(agSelecionado))"
            >R$ {{ totalAgendamento(agSelecionado) }}</button>
          </div>
        </div>

        <form @submit.prevent="confirmarPagamento" class="space-y-4">
          <div v-if="Number(agSelecionado?.cliente?.saldo_credito) > 0" class="bg-indigo-50 border border-indigo-100 rounded-lg p-3 mb-4">
            <div class="flex justify-between items-center mb-2">
              <label class="text-sm font-semibold text-indigo-800">Usar Crédito (Saldo: R$ {{ Number(agSelecionado?.cliente?.saldo_credito).toFixed(2) }})</label>
            </div>
            <input
              v-model="formPag.credito_utilizado"
              type="number"
              step="0.01"
              min="0"
              :max="agSelecionado?.cliente?.saldo_credito"
              class="w-full border border-indigo-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white"
              placeholder="0.00"
            />
          </div>

          <div class="flex gap-3">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Desconto (R$)</label>
              <input
                v-model="formPag.desconto"
                type="number"
                step="0.01"
                min="0"
                class="w-full border border-amber-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 bg-amber-50"
                placeholder="0.00"
              />
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Valor a cobrar (R$) *</label>
              <input
                v-model="formPag.valor"
                type="number"
                step="0.01"
                min="0.01"
                required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                :class="{ 'border-amber-400 bg-amber-50': Number(formPag.desconto) > 0 || Number(formPag.credito_utilizado) > 0 }"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Método *</label>
            <select
              v-model="formPag.metodo"
              required
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            >
              <option value="">Selecione...</option>
              <option value="dinheiro">Dinheiro</option>
              <option value="pix">PIX</option>
              <option value="cartao_credito">Cartão de Crédito</option>
              <option value="cartao_debito">Cartão de Débito</option>
            </select>
          </div>

          <div v-if="formPag.metodo === 'dinheiro' && creditoGerado > 0" class="bg-green-50 text-green-800 p-2 rounded text-xs font-semibold mt-2">
            R$ {{ creditoGerado.toFixed(2) }} será adicionado como crédito ao cliente.
          </div>

          <!-- Alterar status junto com o pagamento -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status do agendamento</label>
            <select
              v-model="formPag.novoStatus"
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            >
              <option value="">Manter atual ({{ statusLabel(agSelecionado?.status) }})</option>
              <option value="concluido">Marcar como Concluído</option>
              <option value="confirmado">Marcar como Confirmado</option>
            </select>
          </div>

          <p v-if="erro" class="text-sm text-red-600">{{ erro }}</p>

          <div class="flex gap-3 pt-1">
            <button
              type="button"
              @click="modalAberto = false"
              class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 bg-green-600 hover:bg-green-700 text-white rounded-lg py-2 text-sm font-semibold disabled:opacity-50"
            >
              {{ saving ? 'Salvando...' : 'Confirmar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '@/api/client'
import { useToast } from '@/composables/useToast'

const { sucesso: toastSucesso } = useToast()

const agendamentos = ref([])
const loading = ref(true)
const filtroStatus = ref('')
const filtroPendentePag = ref(false)
const hoje = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' })
const filtroDe = ref(hoje)
const filtroAte = ref(hoje)

const modalAberto = ref(false)
const agSelecionado = ref(null)
const saving = ref(false)
const erro = ref('')
const formPag = ref({ valor: '', desconto: '0.00', credito_utilizado: '0.00', metodo: '', novoStatus: '' })
const mostrarTotal = ref(false)
const baseValorModal = ref('0.00') // base antes do desconto (total ou preço de serviço selecionado)

const totalRecebido = computed(() => {
  return listaFiltrada.value
    .filter(ag => ag.pagamento)
    .reduce((sum, ag) => sum + Number(ag.pagamento.valor || 0), 0)
    .toFixed(2)
})

const listaFiltrada = computed(() => {
  return agendamentos.value.filter(ag => {
    if (filtroPendentePag.value && ag.pagamento) return false
    if (filtroStatus.value && ag.status !== filtroStatus.value) return false
    if (filtroDe.value || filtroAte.value) {
      const dataRef = ag.itens?.[0]?.data_hora_inicio ?? ag.criado_em
      const d = new Date(dataRef)
      const dSemHora = new Date(d.getFullYear(), d.getMonth(), d.getDate())
      if (filtroDe.value) {
        const de = new Date(filtroDe.value + 'T00:00:00')
        if (dSemHora < de) return false
      }
      if (filtroAte.value) {
        const ate = new Date(filtroAte.value + 'T23:59:59')
        if (dSemHora > ate) return false
      }
    }
    return true
  })
})

async function fetchAgendamentos() {
  loading.value = true
  // Busca apenas o intervalo do filtro (por padrão, só "hoje"), em vez de baixar
  // 6+ meses de agendamentos e filtrar tudo no navegador. Isso reduz drasticamente
  // o payload e a serialização no servidor — principal causa da lentidão da tela.
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

// Refaz a busca no servidor sempre que o intervalo de datas mudar.
// (status e "pendentes de pagamento" continuam sendo filtrados em memória, pois
// já estão dentro do intervalo carregado e o custo é desprezível.)
let _debounceFetch
watch([filtroDe, filtroAte], () => {
  clearTimeout(_debounceFetch)
  _debounceFetch = setTimeout(fetchAgendamentos, 250)
})

function alterarStatus(id, novoStatus) {
  api.patch(`/agendamentos/${id}/status`, { status: novoStatus }).then(fetchAgendamentos)
}

function setValorBase(preco) {
  const v = Number(preco).toFixed(2)
  baseValorModal.value = v
  formPag.value.valor = v
  formPag.value.desconto = '0.00'
  formPag.value.credito_utilizado = '0.00'
}

function abrirModal(ag) {
  agSelecionado.value = ag
  const total = totalAgendamento(ag)
  baseValorModal.value = total
  formPag.value = { valor: total, desconto: '0.00', credito_utilizado: '0.00', metodo: '', novoStatus: '' }
  erro.value = ''
  modalAberto.value = true
}

// Desconto reduz sempre a partir do valor base selecionado (total ou serviço isolado)
watch([() => formPag.value.desconto, () => formPag.value.credito_utilizado], ([desc, cred]) => {
  if (!agSelecionado.value) return
  const newValor = Math.max(0, Number(baseValorModal.value) - Number(desc || 0) - Number(cred || 0)).toFixed(2)
  if (Number(newValor) !== Number(formPag.value.valor)) formPag.value.valor = newValor
})

const creditoGerado = computed(() => {
  if (formPag.value.metodo !== 'dinheiro') return 0
  const valorDevido = Math.max(0, Number(baseValorModal.value) - Number(formPag.value.desconto || 0) - Number(formPag.value.credito_utilizado || 0))
  return Math.max(0, Number(formPag.value.valor) - valorDevido)
})

async function confirmarPagamento() {
  saving.value = true
  erro.value = ''
  try {
    // Muda o status primeiro, se escolheu
    if (formPag.value.novoStatus) {
      await api.patch(`/agendamentos/${agSelecionado.value.id}/status`, {
        status: formPag.value.novoStatus,
      })
    }
    await api.post(`/agendamentos/${agSelecionado.value.id}/pagamento`, {
      valor: formPag.value.valor,
      metodo: formPag.value.metodo,
      credito_utilizado: formPag.value.credito_utilizado || 0,
    })
    modalAberto.value = false
    toastSucesso('Pagamento registrado com sucesso!')
    await fetchAgendamentos()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao registrar pagamento.'
  } finally {
    saving.value = false
  }
}

function totalAgendamento(ag) {
  if (!ag?.itens) return '0.00'
  return ag.itens.reduce((sum, item) => sum + Number(item.servico?.preco || 0), 0).toFixed(2)
}

function statusLabel(s) {
  return { pendente: 'Pendente', confirmado: 'Confirmado', concluido: 'Concluído', cancelado: 'Cancelado' }[s] ?? s
}

function statusBadgeClass(s) {
  return {
    pendente:   'bg-yellow-100 text-yellow-800',
    confirmado: 'bg-blue-100 text-blue-800',
    concluido:  'bg-green-100 text-green-800',
    cancelado:  'bg-red-100 text-red-800',
  }[s] ?? 'bg-gray-100 text-gray-600'
}

function metodoPagLabel(m) {
  return { dinheiro: 'Dinheiro', pix: 'PIX', cartao_credito: 'Cartão Crédito', cartao_debito: 'Cartão Débito' }[m] ?? m
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' })
}

onMounted(fetchAgendamentos)
</script>
