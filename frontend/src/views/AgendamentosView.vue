<template>
  <div class="flex flex-col h-full">

    <!-- Header -->
    <div class="flex items-center justify-between mb-3 flex-shrink-0 gap-2 flex-wrap">
      <h2 class="text-xl font-bold text-gray-800">Agendamentos</h2>
      <div class="flex items-center gap-2 flex-wrap">
        <!-- Busca por cliente -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/>
          </svg>
          <input
            v-model="buscaCalendario"
            type="text"
            placeholder="Buscar cliente..."
            class="border border-gray-200 text-gray-600 text-sm pl-9 pr-8 py-2 rounded-lg w-44 focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <button
            v-if="buscaCalendario"
            @click="buscaCalendario = ''"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-base leading-none"
          >×</button>
        </div>
        <!-- Filtro por profissional: visível apenas para recepcionista/admin -->
        <select
          v-if="isRecepcionistaOuAdmin"
          v-model="filtroProfissional"
          class="border border-gray-200 text-gray-600 text-sm px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
        >
          <option :value="null">Todos os profissionais</option>
          <option v-for="p in profissionais" :key="p.id" :value="p.id">{{ p.nome }}</option>
        </select>
        <button
          class="border border-gray-200 text-gray-600 text-sm font-medium px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1.5"
          @click="showClientesPanel = true"
        >
          👥 Clientes
        </button>
        <button
          class="bg-rose-600 text-white text-sm font-semibold px-4 py-2 rounded-lg hover:bg-rose-700 transition-colors"
          @click="abrirModalNovo()"
        >
          + Novo
        </button>
      </div>
    </div>

    <!-- FullCalendar -->
    <div class="flex-1 bg-white border border-gray-200 rounded-xl overflow-hidden fc-wrapper">
      <FullCalendar v-if="!loading" :options="calendarOptions" />
      <div v-else class="p-10 text-center text-sm text-gray-400">Carregando...</div>
    </div>

    <!-- MODAL: Novo / Editar Agendamento -->
    <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-gray-800 mb-4">
          {{ modalMode === 'edit' ? `Editar Agendamento #${formData.id}` : 'Novo Agendamento' }}
        </h3>
        <form @submit.prevent="salvarModal" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Cliente *</label>
            <select v-model="formData.cliente_id" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
              <option value="">Selecione...</option>
              <option v-for="c in clientes" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </div>
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">Serviços *</label>
              <button type="button" class="text-xs text-rose-600 font-medium hover:underline" @click="addItem">+ Adicionar</button>
            </div>
            <div v-for="(item, idx) in formData.itens" :key="idx" class="border border-gray-200 rounded-lg p-3 mb-2 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-gray-500">Serviço {{ idx + 1 }}</span>
                <button v-if="formData.itens.length > 1" type="button" class="text-xs text-red-400 hover:text-red-600" @click="removeItem(idx)">Remover</button>
              </div>
              <div>
                <label class="block text-xs text-gray-600 mb-1">Serviço</label>
                <select v-model="item.servico_id" required class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
                  <option value="">Selecione...</option>
                  <option v-for="s in servicos" :key="s.id" :value="s.id">{{ s.nome }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-600 mb-1">Profissional</label>
                <select v-model="item.profissional_id" required class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
                  <option value="">Selecione...</option>
                  <option v-for="p in profissionais" :key="p.id" :value="p.id">{{ p.nome }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-600 mb-1">Data e Hora</label>
                <input v-model="item.data_hora_inicio" type="datetime-local" required class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Observações</label>
            <textarea v-model="formData.observacoes" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"></textarea>
          </div>
          <p v-if="modalError" class="text-sm text-red-500">{{ modalError }}</p>
          <div class="flex gap-2 pt-2">
            <button type="button" class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50" @click="showModal = false">Cancelar</button>
            <button type="submit" :disabled="saving" class="flex-1 bg-rose-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-rose-700 disabled:opacity-50">
              {{ saving ? 'Salvando...' : (modalMode === 'edit' ? 'Salvar' : 'Criar') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL: Detalhe -->
    <div v-if="detalheAg" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="text-lg font-bold text-gray-800">{{ detalheAg.cliente?.nome || '—' }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">#{{ detalheAg.id }} · Criado {{ formatDateShort(detalheAg.criado_em) }}</p>
          </div>
          <button @click="detalheAg = null" class="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>
        <div class="space-y-2 mb-4">
          <div v-for="item in detalheAg.itens" :key="item.id" class="flex items-center gap-3 bg-gray-50 rounded-lg px-3 py-2">
            <div class="text-lg">✂️</div>
            <div>
              <div class="text-sm font-medium text-gray-800">{{ item.servico?.nome }}</div>
              <div class="text-xs text-gray-500">{{ item.profissional?.nome }} · {{ formatDate(item.data_hora_inicio) }}</div>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-3 mb-4">
          <label class="text-sm font-medium text-gray-700">Status</label>
          <select
            :value="detalheAg.status"
            class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm"
            @change="alterarStatus(detalheAg.id, $event.target.value); detalheAg.status = $event.target.value"
          >
            <option value="pendente">Pendente</option>
            <option value="confirmado">Confirmado</option>
            <option value="concluido">Concluído</option>
            <option value="cancelado">Cancelado</option>
          </select>
        </div>
        <div v-if="detalheAg.observacoes" class="text-sm text-gray-500 mb-4 bg-gray-50 rounded-lg px-3 py-2">{{ detalheAg.observacoes }}</div>
        <div class="flex gap-2">
          <button @click="abrirModalEditar(detalheAg); detalheAg = null" class="flex-1 bg-rose-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-rose-700">✏️ Editar</button>
          <button @click="detalheAg = null" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50">Fechar</button>
        </div>
      </div>
    </div>

    <!-- PAINEL: Clientes -->
    <div v-if="showClientesPanel" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <h3 class="text-lg font-bold text-gray-800">Clientes</h3>
          <div class="flex items-center gap-2">
            <button class="bg-rose-600 text-white text-sm font-semibold px-4 py-1.5 rounded-lg hover:bg-rose-700" @click="abrirModalCliente()">+ Novo</button>
            <button @click="showClientesPanel = false; buscaCliente = ''" class="text-gray-400 hover:text-gray-600 text-xl leading-none ml-2">×</button>
          </div>
        </div>
        <!-- Busca -->
        <div class="px-6 py-3 border-b border-gray-100 flex-shrink-0">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/>
            </svg>
            <input
              v-model="buscaCliente"
              type="text"
              placeholder="Buscar por nome..."
              class="w-full border border-gray-200 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
          </div>
        </div>
        <div class="flex-1 overflow-auto">
          <div v-if="loadingClientes" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
          <div v-else-if="clientesFiltrados.length === 0" class="p-8 text-center text-sm text-gray-400">Nenhum cliente encontrado.</div>
          <table v-else class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-200 sticky top-0">
              <tr>
                <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
                <th class="text-left px-4 py-3 font-medium text-gray-600">Email</th>
                <th class="text-left px-4 py-3 font-medium text-gray-600">Telefone</th>
                <th class="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="c in clientesFiltrados" :key="c.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-800">{{ c.nome }}</td>
                <td class="px-4 py-3 text-gray-500">{{ c.email || '-' }}</td>
                <td class="px-4 py-3 text-gray-500">{{ c.telefone || '-' }}</td>
                <td class="px-4 py-3">
                  <button class="text-xs text-blue-600 hover:underline mr-3" @click="abrirModalCliente(c)">Editar</button>
                  <button class="text-xs text-red-500 hover:underline" @click="removerCliente(c.id)">Remover</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- MODAL: Novo / Editar Cliente -->
    <div v-if="showModalCliente" class="fixed inset-0 bg-black/40 flex items-center justify-center z-[60] p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">{{ editandoCliente ? 'Editar' : 'Novo' }} Cliente</h3>
        <form @submit.prevent="salvarCliente" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input v-model="formCliente.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="formCliente.email" type="email" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
            <input v-model="formCliente.telefone" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <p v-if="erroCliente" class="text-sm text-red-500">{{ erroCliente }}</p>
          <div class="flex gap-2 pt-2">
            <button type="button" class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50" @click="showModalCliente = false">Cancelar</button>
            <button type="submit" :disabled="savingCliente" class="flex-1 bg-rose-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-rose-700 disabled:opacity-50">
              {{ savingCliente ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import ptBrLocale from '@fullcalendar/core/locales/pt-br'
import api from '@/api/client'

// ─── State ─────────────────────────────────────────────────────────────────
const authStore = useAuthStore()
const isProfissional = computed(() => authStore.user?.role === 'profissional')
const isRecepcionistaOuAdmin = computed(() => ['recepcionista', 'admin'].includes(authStore.user?.role))

const agendamentos = ref([])
const clientes = ref([])
const servicos = ref([])
const profissionais = ref([])
const loading = ref(true)
const loadingClientes = ref(false)

const filtroProfissional = ref(null)
const buscaCalendario = ref('')

const showModal = ref(false)
const modalMode = ref('create')
const saving = ref(false)
const modalError = ref('')
const detalheAg = ref(null)
const formData = ref({ id: null, cliente_id: '', observacoes: '', itens: [] })

const showClientesPanel = ref(false)
const showModalCliente = ref(false)
const savingCliente = ref(false)
const erroCliente = ref('')
const editandoCliente = ref(null)
const formCliente = ref({ nome: '', email: '', telefone: '' })
const buscaCliente = ref('')

const clientesFiltrados = computed(() => {
  const q = buscaCliente.value.trim().toLowerCase()
  if (!q) return clientes.value
  return clientes.value.filter(c => c.nome.toLowerCase().includes(q))
})

// ─── FullCalendar ──────────────────────────────────────────────────────────
const STATUS_COLORS = {
  pendente:   { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
  confirmado: { bg: '#dbeafe', border: '#3b82f6', text: '#1e3a8a' },
  concluido:  { bg: '#dcfce7', border: '#22c55e', text: '#14532d' },
  cancelado:  { bg: '#fee2e2', border: '#ef4444', text: '#7f1d1d' },
}

const computedSlotMax = computed(() => {
  let maxH = 22
  for (const ag of agendamentos.value) {
    for (const item of ag.itens ?? []) {
      if (!item.data_hora_inicio) continue
      const h = new Date(item.data_hora_inicio).getHours()
      if (h >= maxH) maxH = h + 2
    }
  }
  return String(maxH).padStart(2, '0') + ':00:00'
})

const calendarEvents = computed(() => {
  const q = buscaCalendario.value.trim().toLowerCase()
  const profFiltroId = filtroProfissional.value ? Number(filtroProfissional.value) : null
  const events = []
  for (const ag of agendamentos.value) {
    if (q && !(ag.cliente?.nome ?? '').toLowerCase().includes(q)) continue
    const color = STATUS_COLORS[ag.status] ?? STATUS_COLORS.pendente
    for (const item of ag.itens ?? []) {
      // Se há filtro de profissional ativo, ignora itens de outros profissionais
      if (profFiltroId && item.profissional?.id !== profFiltroId) continue
      const servNome = item.servico?.nome ?? ''
      const profNome = item.profissional?.nome ?? ''
      events.push({
        id: `${ag.id}-${item.id}`,
        title: servNome ? `${ag.cliente?.nome ?? '—'} · ${servNome}` : (ag.cliente?.nome ?? '—'),
        start: item.data_hora_inicio,
        end: item.data_hora_fim ?? item.data_hora_inicio,
        backgroundColor: color.bg,
        borderColor: color.border,
        textColor: color.text,
        extendedProps: { ag, servNome, profNome },
      })
    }
  }
  return events
})

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  locale: ptBrLocale,
  initialView: 'timeGridWeek',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek',
  },
  allDaySlot: false,
  slotMinTime: '07:00:00',
  slotMaxTime: computedSlotMax.value,
  slotDuration: '00:30:00',
  slotLabelInterval: '01:00:00',
  slotLabelFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
  expandRows: true,
  nowIndicator: true,
  editable: false,
  droppable: false,
  eventDurationEditable: false,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: true,
  weekends: true,
  height: '100%',
  events: calendarEvents.value,
  eventClick: onEventClick,
  dateClick: onDateClick,
  eventContent: renderEventContent,
}))

function escapeHtml(str) {
  if (!str) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function renderEventContent(arg) {
  const { servNome, profNome } = arg.event.extendedProps
  const ag = arg.event.extendedProps.ag
  const clienteNome = ag?.cliente?.nome ?? arg.event.title
  const hora = arg.event.start
    ? new Date(arg.event.start).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    : ''

  const durMin = (arg.event.end && arg.event.start)
    ? (arg.event.end.getTime() - arg.event.start.getTime()) / 60000
    : 60

  // Primeiro nome apenas (para caixas pequenas)
  const firstName = (s) => s ? s.split(' ')[0] : ''

  if (durMin <= 30) {
    // 1 slot (~48px): cabe só 3 linhas — usa primeiro nome para economizar espaço
    const titleEsc = escapeHtml(firstName(clienteNome))
    const servEsc  = escapeHtml(servNome)
    const profHora = [firstName(profNome), hora].filter(Boolean).join(' · ')
    return {
      html: `<div class="fc-event-inner">
        <div class="fc-ev-title">${titleEsc}</div>
        ${servEsc ? `<div class="fc-ev-sub">${servEsc}</div>` : ''}
        <div class="fc-ev-time">${escapeHtml(profHora)}</div>
      </div>`,
    }
  }

  // 2+ slots: layout completo com nomes inteiros
  const titleEsc = escapeHtml(clienteNome)
  const servEsc  = escapeHtml(servNome)
  const profEsc  = escapeHtml(profNome)
  return {
    html: `<div class="fc-event-inner">
      <div class="fc-ev-title">${titleEsc}</div>
      ${servEsc ? `<div class="fc-ev-sub">${servEsc}</div>` : ''}
      ${profEsc ? `<div class="fc-ev-sub">${profEsc}</div>` : ''}
      <div class="fc-ev-time">${hora}</div>
    </div>`,
  }
}

function onEventClick(info) {
  detalheAg.value = info.event.extendedProps.ag
}

function onDateClick(info) {
  const dt = info.dateStr.includes('T') ? info.dateStr.slice(0, 16) : info.dateStr + 'T09:00'
  abrirModalNovo(dt)
}

async function onEventDrop(info) {
  const ag = info.event.extendedProps.ag
  const delta = info.event.start - new Date(ag.itens?.[0]?.data_hora_inicio)
  try {
    await api.put(`/agendamentos/${ag.id}`, {
      cliente_id: ag.cliente_id,
      observacoes: ag.observacoes || null,
      itens: ag.itens.map(i => ({
        servico_id: i.servico?.id ?? i.servico_id,
        profissional_id: i.profissional?.id ?? i.profissional_id,
        data_hora_inicio: new Date(new Date(i.data_hora_inicio).getTime() + delta).toISOString(),
      })),
    })
    await fetchAgendamentos()
  } catch (e) {
    info.revert()
    alert(e.response?.data?.detail || 'Erro ao mover agendamento.')
  }
}

// ─── Agendamento CRUD ──────────────────────────────────────────────────────
function emptyItem(dt = '') {
  return { servico_id: '', profissional_id: '', data_hora_inicio: dt }
}

function abrirModalNovo(dt = '') {
  modalMode.value = 'create'
  formData.value = { id: null, cliente_id: '', observacoes: '', itens: [emptyItem(dt)] }
  modalError.value = ''
  showModal.value = true
}

function abrirModalEditar(ag) {
  modalMode.value = 'edit'
  formData.value = {
    id: ag.id,
    cliente_id: ag.cliente_id,
    observacoes: ag.observacoes || '',
    itens: ag.itens.map(i => ({
      servico_id: i.servico?.id ?? i.servico_id,
      profissional_id: i.profissional?.id ?? i.profissional_id,
      data_hora_inicio: toDatetimeLocal(i.data_hora_inicio),
    })),
  }
  modalError.value = ''
  showModal.value = true
}

function addItem() { formData.value.itens.push(emptyItem()) }
function removeItem(idx) { formData.value.itens.splice(idx, 1) }

async function salvarModal() {
  modalError.value = ''
  saving.value = true
  try {
    const payload = {
      cliente_id: formData.value.cliente_id,
      observacoes: formData.value.observacoes || null,
      itens: formData.value.itens.map(i => ({
        servico_id: i.servico_id,
        profissional_id: i.profissional_id,
        data_hora_inicio: i.data_hora_inicio,
      })),
    }
    if (modalMode.value === 'edit') {
      await api.put(`/agendamentos/${formData.value.id}`, payload)
    } else {
      await api.post('/agendamentos/', payload)
    }
    showModal.value = false
    await fetchAgendamentos()
  } catch (e) {
    modalError.value = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    saving.value = false
  }
}

function alterarStatus(id, status) {
  api.patch(`/agendamentos/${id}/status`, { status }).then(fetchAgendamentos)
}

async function fetchAgendamentos() {
  loading.value = true
  const params = {}
  if (filtroProfissional.value) params.profissional_id = filtroProfissional.value
  const { data } = await api.get('/agendamentos/', { params })
  agendamentos.value = data
  loading.value = false
}

watch(filtroProfissional, fetchAgendamentos)

// ─── Clientes CRUD ─────────────────────────────────────────────────────────
function abrirModalCliente(cliente = null) {
  editandoCliente.value = cliente?.id || null
  formCliente.value = { nome: cliente?.nome || '', email: cliente?.email || '', telefone: cliente?.telefone || '' }
  erroCliente.value = ''
  showModalCliente.value = true
}

async function salvarCliente() {
  erroCliente.value = ''
  savingCliente.value = true
  try {
    if (editandoCliente.value) {
      await api.patch(`/clientes/${editandoCliente.value}`, formCliente.value)
    } else {
      await api.post('/clientes/', formCliente.value)
    }
    showModalCliente.value = false
    await fetchClientes()
  } catch (e) {
    erroCliente.value = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    savingCliente.value = false
  }
}

async function removerCliente(id) {
  if (!confirm('Remover este cliente?')) return
  await api.delete(`/clientes/${id}`)
  await fetchClientes()
}

async function fetchClientes() {
  loadingClientes.value = true
  const { data } = await api.get('/clientes/')
  clientes.value = data
  loadingClientes.value = false
}

// ─── Helpers ───────────────────────────────────────────────────────────────
function toDatetimeLocal(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0') + 'T' +
    String(d.getHours()).padStart(2, '0') + ':' +
    String(d.getMinutes()).padStart(2, '0')
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function formatDateShort(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit' })
}

async function fetchReferencias() {
  try {
    const [s, p] = await Promise.all([api.get('/servicos/'), api.get('/profissionais/')])
    servicos.value = s.data.filter(sv => sv.ativo !== false)
    profissionais.value = p.data
  } catch (e) { console.error('Erro ao carregar referências:', e) }
}

onMounted(() => Promise.all([fetchAgendamentos(), fetchClientes(), fetchReferencias()]))
</script>

<style>
.fc-wrapper .fc {
  font-family: inherit;
  height: 100%;
}
.fc-wrapper .fc-toolbar-title {
  font-size: 1rem;
  font-weight: 700;
}
.fc-wrapper .fc-button {
  background: white !important;
  border: 1px solid #e5e7eb !important;
  color: #374151 !important;
  font-size: 0.75rem !important;
  font-weight: 500 !important;
  padding: 4px 10px !important;
  box-shadow: none !important;
  border-radius: 6px !important;
}
.fc-wrapper .fc-button:hover {
  background: #f9fafb !important;
}
.fc-wrapper .fc-button-active,
.fc-wrapper .fc-button:focus {
  background: #e11d48 !important;
  border-color: #e11d48 !important;
  color: white !important;
  outline: none !important;
}
.fc-wrapper .fc-timegrid-slot {
  height: 3rem !important;
}
.fc-wrapper .fc-event {
  border-radius: 4px !important;
  cursor: pointer !important;
  padding: 1px 3px !important;
}
.fc-wrapper .fc-event-inner {
  display: flex;
  flex-direction: column;
  gap: 1px;
  overflow: hidden;
  height: 100%;
  min-height: 0;
}
.fc-wrapper .fc-ev-title {
  font-weight: 600;
  font-size: 0.72rem;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.fc-wrapper .fc-ev-sub {
  font-size: 0.65rem;
  opacity: 0.8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.fc-wrapper .fc-ev-time {
  font-size: 0.63rem;
  opacity: 0.65;
}
.fc-wrapper .fc-col-header-cell {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  padding: 6px 0;
}
.fc-wrapper .fc-timegrid-slot-label {
  font-size: 0.7rem;
  color: #9ca3af;
}
.fc-wrapper .fc-now-indicator-line {
  border-color: #e11d48;
}
.fc-wrapper .fc-now-indicator-arrow {
  border-top-color: #e11d48;
  border-bottom-color: #e11d48;
}
.fc-wrapper .fc-toolbar {
  padding: 8px 12px !important;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
