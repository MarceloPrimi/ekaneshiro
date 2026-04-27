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
      <button v-if="filtroStatus || filtroDe || filtroAte" @click="filtroStatus = ''; filtroDe = ''; filtroAte = ''" class="text-xs text-gray-400 hover:text-gray-600 px-2 py-1 rounded">✕ Limpar</button>
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
            <th class="text-left px-4 py-3 font-medium text-gray-600">ID</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Cliente</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Serviços</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Total</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Status</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Pagamento</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="ag in listaFiltrada" :key="ag.id" class="hover:bg-gray-50 align-top">
            <td class="px-4 py-3 text-gray-400">#{{ ag.id }}</td>
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
              <select
                :value="ag.status"
                class="border border-gray-200 rounded-md px-2 py-1 text-xs"
                @change="alterarStatus(ag.id, $event.target.value)"
              >
                <option value="pendente">Pendente</option>
                <option value="confirmado">Confirmado</option>
                <option value="concluido">Concluído</option>
                <option value="cancelado">Cancelado</option>
              </select>
            </td>
            <td class="px-4 py-3">
              <div v-if="ag.pagamento" class="text-xs">
                <span class="font-semibold text-green-700">R$ {{ Number(ag.pagamento.valor).toFixed(2) }}</span><br />
                <span class="text-gray-400">{{ metodoPagLabel(ag.pagamento.metodo) }}</span><br />
                <span class="text-gray-400">{{ formatDate(ag.pagamento.pago_em) }}</span>
              </div>
              <span v-else class="text-xs text-gray-300 italic">Não pago</span>
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
            class="flex justify-between text-xs text-gray-600"
          >
            <span>{{ item.servico?.nome }}</span>
            <span>R$ {{ Number(item.servico?.preco).toFixed(2) }}</span>
          </div>
          <div class="border-t border-gray-200 pt-1 flex justify-between text-sm font-bold text-gray-800">
            <span>Total</span>
            <span>R$ {{ totalAgendamento(agSelecionado) }}</span>
          </div>
        </div>

        <form @submit.prevent="confirmarPagamento" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Valor cobrado (R$) *</label>
            <input
              v-model="formPag.valor"
              type="number"
              step="0.01"
              min="0.01"
              required
              class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
            />
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
import { ref, computed, onMounted } from 'vue'
import api from '@/api/client'

const agendamentos = ref([])
const loading = ref(true)
const filtroStatus = ref('')
const filtroDe = ref('')
const filtroAte = ref('')

const modalAberto = ref(false)
const agSelecionado = ref(null)
const saving = ref(false)
const erro = ref('')
const formPag = ref({ valor: '', metodo: '', novoStatus: '' })
const mostrarTotal = ref(true)

const totalRecebido = computed(() => {
  return listaFiltrada.value
    .filter(ag => ag.pagamento)
    .reduce((sum, ag) => sum + Number(ag.pagamento.valor || 0), 0)
    .toFixed(2)
})

const listaFiltrada = computed(() => {
  return agendamentos.value.filter(ag => {
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
  const { data } = await api.get('/agendamentos/')
  agendamentos.value = data
  loading.value = false
}

function alterarStatus(id, novoStatus) {
  api.patch(`/agendamentos/${id}/status`, { status: novoStatus }).then(fetchAgendamentos)
}

function abrirModal(ag) {
  agSelecionado.value = ag
  formPag.value = { valor: totalAgendamento(ag), metodo: '', novoStatus: '' }
  erro.value = ''
  modalAberto.value = true
}

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
    })
    modalAberto.value = false
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

function metodoPagLabel(m) {
  return { dinheiro: 'Dinheiro', pix: 'PIX', cartao_credito: 'Cartão Crédito', cartao_debito: 'Cartão Débito' }[m] ?? m
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', hour: '2-digit', minute: '2-digit' })
}

onMounted(fetchAgendamentos)
</script>
