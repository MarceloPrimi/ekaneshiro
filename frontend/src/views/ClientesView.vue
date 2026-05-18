<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-5 gap-3 flex-wrap">
      <h2 class="text-xl font-bold text-gray-800">Clientes</h2>
      <div class="flex items-center gap-3">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/>
          </svg>
          <input v-model="busca" type="text" placeholder="Buscar cliente..." class="border border-gray-200 text-sm pl-9 pr-3 py-2 rounded-lg w-52 focus:outline-none focus:ring-2 focus:ring-rose-300" />
        </div>
        <button class="bg-rose-600 text-white text-sm font-semibold px-4 py-2 rounded-lg hover:bg-rose-700 transition-colors" @click="abrirNovo">
          + Novo
        </button>
      </div>
    </div>

    <!-- Tabela -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-x-auto">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600 hidden sm:table-cell">Telefone</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600 hidden md:table-cell">Email</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="c in clientesFiltrados"
            :key="c.id"
            class="hover:bg-rose-50 cursor-pointer"
            @click="abrirCliente(c)"
          >
            <td class="px-4 py-3 font-medium text-gray-800">{{ c.nome }}</td>
            <td class="px-4 py-3 text-gray-500 hidden sm:table-cell">{{ c.telefone || '-' }}</td>
            <td class="px-4 py-3 text-gray-500 hidden md:table-cell">{{ c.email || '-' }}</td>
            <td class="px-4 py-3 text-right">
              <button class="text-xs text-red-400 hover:text-red-600 hover:underline" @click.stop="confirmarRemover(c)">Remover</button>
            </td>
          </tr>
          <tr v-if="clientesFiltrados.length === 0">
            <td colspan="4" class="px-4 py-8 text-center text-sm text-gray-400">Nenhum cliente encontrado.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Drawer (modal largo) -->
    <div v-if="drawer" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="fechar">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden">

        <!-- Cabeçalho do drawer -->
        <div class="flex items-start justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div>
            <h3 class="text-lg font-bold text-gray-800">{{ form.nome || 'Novo Cliente' }}</h3>
            <p v-if="clienteSelecionado?.id" class="text-xs text-gray-400 mt-0.5">
              {{ historicoItens.length }} visita{{ historicoItens.length !== 1 ? 's' : '' }} registrada{{ historicoItens.length !== 1 ? 's' : '' }}
            </p>
          </div>
          <button @click="fechar" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Corpo: dois painéis -->
        <div class="flex flex-1 overflow-hidden">

          <!-- Esquerda: Formulário -->
          <div class="w-72 flex-shrink-0 overflow-y-auto border-r border-gray-100 p-5">
            <form @submit.prevent="salvar" class="space-y-4">

              <!-- Nome -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Nome</label>
                <input v-model="form.nome" required class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>

              <!-- Telefone -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Número de telefone</label>
                <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-rose-400">
                  <span class="flex items-center gap-1 px-3 py-2 bg-gray-50 text-sm text-gray-600 border-r border-gray-200 select-none whitespace-nowrap">🇧🇷 +55</span>
                  <input v-model="form.telefone" class="flex-1 px-3 py-2 text-sm focus:outline-none" placeholder="(11) 99999-9999" />
                </div>
              </div>

              <!-- Email -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Endereço de e-mail</label>
                <input v-model="form.email" type="email" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>

              <!-- Notas -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Notas do cliente</label>
                <textarea
                  v-model="form.observacoes"
                  rows="3"
                  class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 resize-none"
                ></textarea>
              </div>

              <!-- Campos personalizados -->
              <div>
                <div class="flex items-center justify-between mb-2">
                  <label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Campos personalizados</label>
                  <button
                    type="button"
                    class="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-rose-600 transition-colors"
                    :title="editandoCampos ? 'Concluir edição' : 'Gerenciar campos'"
                    @click="editandoCampos = !editandoCampos"
                  >
                    <!-- ícone de sliders -->
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/>
                    </svg>
                  </button>
                </div>

                <div v-if="form.campos_dinamicos.length === 0 && !editandoCampos" class="text-xs text-gray-400 italic px-1">Nenhum campo adicionado.</div>

                <div v-for="(campo, i) in form.campos_dinamicos" :key="i" class="mb-2">
                  <!-- modo edição: renomear / remover -->
                  <div v-if="editandoCampos" class="flex gap-1.5 items-center">
                    <input
                      v-model="campo.chave"
                      placeholder="Nome do campo"
                      class="flex-1 border border-gray-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-rose-400"
                    />
                    <button type="button" class="text-gray-300 hover:text-red-500 text-lg leading-none px-1" @click="removeCampo(i)">×</button>
                  </div>
                  <!-- modo normal: label + value input -->
                  <div v-else>
                    <label class="block text-xs font-medium text-gray-500 mb-0.5">{{ campo.chave }}</label>
                    <input v-model="campo.valor" class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
                  </div>
                </div>

                <button
                  v-if="editandoCampos"
                  type="button"
                  class="mt-1 w-full border border-dashed border-gray-300 text-xs text-gray-500 hover:border-rose-400 hover:text-rose-600 rounded-lg py-1.5 transition-colors"
                  @click="addCampo"
                >+ Adicionar campo</button>
              </div>

              <p v-if="modalError" class="text-sm text-red-500">{{ modalError }}</p>

              <div class="flex gap-2 pt-1">
                <button type="button" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50" @click="fechar">Cancelar</button>
                <button type="submit" :disabled="saving" class="flex-1 bg-rose-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-rose-700 disabled:opacity-50">
                  {{ saving ? 'Salvando...' : 'Salvar' }}
                </button>
              </div>
            </form>
          </div>

          <!-- Direita: Histórico de visitas -->
          <div class="flex-1 overflow-y-auto p-5">
            <h4 class="text-sm font-semibold text-gray-700 mb-4">Visitas anteriores</h4>

            <div v-if="!clienteSelecionado?.id" class="text-sm text-gray-400 italic">Salve o cliente para ver o histórico.</div>
            <div v-else-if="loadingHistorico" class="text-sm text-gray-400">Carregando...</div>
            <div v-else-if="historicoItens.length === 0" class="text-sm text-gray-400 italic">Nenhuma visita registrada.</div>

            <div
              v-for="(item, idx) in historicoItens"
              :key="idx"
              class="mb-3 bg-gray-50 rounded-xl p-3.5 border border-gray-100"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-2.5 min-w-0">
                  <span class="mt-1.5 flex-shrink-0 w-2.5 h-2.5 rounded-full" :class="statusDot(item.agStatus)"></span>
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-gray-800 truncate">{{ item.servico?.nome }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">Colaborador: {{ item.profissional?.nome }}</p>
                    <p class="text-xs text-gray-400 mt-0.5">* {{ item.servico?.nome }}: {{ item.servico?.duracao_minutos }}min ({{ diaSemana(item.data_hora_inicio) }})</p>
                  </div>
                </div>
                <div class="text-right flex-shrink-0">
                  <p class="text-sm font-medium text-gray-700">{{ formatData(item.data_hora_inicio) }}</p>
                  <p class="text-xs text-gray-400">{{ formatHora(item.data_hora_inicio) }}</p>
                </div>
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
import { useToast } from '@/composables/useToast'

const { sucesso: toastSucesso } = useToast()

const clientes = ref([])
const loading = ref(true)
const busca = ref('')
const drawer = ref(false)
const clienteSelecionado = ref(null)
const saving = ref(false)
const modalError = ref('')
const editandoCampos = ref(false)
const form = ref({ nome: '', email: '', telefone: '', observacoes: '', campos_dinamicos: [] })

const historico = ref([])
const loadingHistorico = ref(false)

// ─── Computed ──────────────────────────────────────────────────────────────

const clientesFiltrados = computed(() => {
  const q = busca.value.trim().toLowerCase()
  if (!q) return clientes.value
  return clientes.value.filter(c =>
    c.nome.toLowerCase().includes(q) ||
    (c.telefone && c.telefone.includes(q)) ||
    (c.email && c.email.toLowerCase().includes(q))
  )
})

// achata os itens de todos os agendamentos, mais recente primeiro
const historicoItens = computed(() => {
  const items = []
  for (const ag of historico.value) {
    for (const item of ag.itens ?? []) {
      items.push({ ...item, agStatus: ag.status })
    }
  }
  return items.sort((a, b) => new Date(b.data_hora_inicio) - new Date(a.data_hora_inicio))
})

// ─── Formatadores ──────────────────────────────────────────────────────────

const DIAS = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']

function formatData(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`
}

function formatHora(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' })
}

function diaSemana(dateStr) {
  if (!dateStr) return ''
  return DIAS[new Date(dateStr).getDay()]
}

const STATUS_DOT = {
  pendente:   'bg-yellow-400',
  confirmado: 'bg-blue-400',
  concluido:  'bg-green-400',
  cancelado:  'bg-red-400',
}

function statusDot(status) {
  return STATUS_DOT[status] ?? 'bg-gray-300'
}

// ─── CRUD ──────────────────────────────────────────────────────────────────

async function fetchClientes() {
  loading.value = true
  const { data } = await api.get('/clientes/')
  clientes.value = data
  loading.value = false
}

async function fetchHistorico(clienteId) {
  loadingHistorico.value = true
  historico.value = []
  try {
    const { data } = await api.get(`/agendamentos/?cliente_id=${clienteId}`)
    historico.value = data
  } finally {
    loadingHistorico.value = false
  }
}

function abrirNovo() {
  clienteSelecionado.value = null
  form.value = { nome: '', email: '', telefone: '', observacoes: '', campos_dinamicos: [] }
  historico.value = []
  editandoCampos.value = false
  modalError.value = ''
  drawer.value = true
}

function abrirCliente(c) {
  clienteSelecionado.value = c
  form.value = {
    nome: c.nome,
    email: c.email || '',
    telefone: c.telefone || '',
    observacoes: c.observacoes || '',
    campos_dinamicos: c.campos_dinamicos ? JSON.parse(JSON.stringify(c.campos_dinamicos)) : [],
  }
  editandoCampos.value = false
  modalError.value = ''
  drawer.value = true
  fetchHistorico(c.id)
}

function fechar() {
  drawer.value = false
  clienteSelecionado.value = null
}

function addCampo() {
  form.value.campos_dinamicos.push({ chave: '', valor: '' })
}

function removeCampo(i) {
  form.value.campos_dinamicos.splice(i, 1)
}

async function salvar() {
  modalError.value = ''
  saving.value = true
  try {
    const payload = {
      nome: form.value.nome,
      email: form.value.email || null,
      telefone: form.value.telefone || null,
      observacoes: form.value.observacoes || null,
      campos_dinamicos: form.value.campos_dinamicos.length ? form.value.campos_dinamicos : null,
    }
    if (clienteSelecionado.value?.id) {
      const { data } = await api.patch(`/clientes/${clienteSelecionado.value.id}`, payload)
      clienteSelecionado.value = data
      const idx = clientes.value.findIndex(c => c.id === data.id)
      if (idx !== -1) clientes.value[idx] = data
      toastSucesso('Cliente salvo com sucesso!')
    } else {
      const { data } = await api.post('/clientes/', payload)
      clientes.value = [...clientes.value, data].sort((a, b) => a.nome.localeCompare(b.nome))
      clienteSelecionado.value = data
      toastSucesso('Cliente criado com sucesso!')
      await fetchHistorico(data.id)
    }
  } catch (e) {
    modalError.value = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    saving.value = false
  }
}

async function confirmarRemover(c) {
  if (!confirm(`Remover o cliente "${c.nome}"?`)) return
  await api.delete(`/clientes/${c.id}`)
  if (clienteSelecionado.value?.id === c.id) fechar()
  await fetchClientes()
}

onMounted(fetchClientes)
</script>

