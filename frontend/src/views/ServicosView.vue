<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-800">Serviços</h2>
      <button
        v-if="auth.isAdmin"
        @click="abrirModal"
        class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
      >
        + Novo Serviço
      </button>
    </div>

    <!-- Painel de Seções -->
    <div v-if="auth.isAdmin" class="mb-4 bg-white rounded-xl border border-gray-200 overflow-hidden">
      <button
        @click="gerenciandoSecoes = !gerenciandoSecoes"
        class="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
      >
        <span class="flex items-center gap-2">
          <span class="text-gray-400">▤</span>
          Seções
          <span class="ml-1 text-xs font-normal text-gray-400">({{ secoes.length }})</span>
        </span>
        <svg :class="gerenciandoSecoes ? 'rotate-180' : ''" class="w-4 h-4 text-gray-400 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>
      <div v-if="gerenciandoSecoes" class="border-t border-gray-100 px-4 py-4 space-y-3">
        <div v-if="!secoes.length" class="text-sm text-gray-400 italic">Nenhuma seção cadastrada.</div>
        <div v-else class="flex flex-wrap gap-2">
          <span
            v-for="sec in secoes"
            :key="sec.id"
            class="flex items-center gap-1.5 bg-rose-50 text-rose-700 text-xs font-medium px-3 py-1.5 rounded-full"
          >
            {{ sec.nome }}
            <button @click="excluirSecao(sec)" class="hover:text-red-700 ml-0.5" title="Excluir seção">✕</button>
          </span>
        </div>
        <form @submit.prevent="criarSecao" class="flex gap-2 mt-2">
          <input
            v-model="novaSecao"
            placeholder="Nova seção (ex: Corte, Manicure...)"
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
          />
          <button
            type="submit"
            :disabled="salvandoSecao || !novaSecao.trim()"
            class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-2 rounded-lg disabled:opacity-50"
          >+ Criar</button>
        </form>
        <p v-if="erroSecao" class="text-xs text-red-600">{{ erroSecao }}</p>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="!loading && servicos.length" class="flex flex-wrap items-center gap-2 px-4 py-3 border-b border-gray-100">
        <select v-model="filtroSecao" class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-1 focus:ring-rose-400 bg-white">
          <option :value="null">Todas as seções</option>
          <option v-for="sec in secoes" :key="sec.id" :value="sec.id">{{ sec.nome }}</option>
          <option :value="0">Sem seção</option>
        </select>
        <select v-model="filtroStatus" class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-1 focus:ring-rose-400 bg-white">
          <option value="todos">Todos</option>
          <option value="ativos">Apenas ativos</option>
          <option value="inativos">Apenas inativos</option>
        </select>
        <span class="text-xs text-gray-400">{{ servicosFiltrados.length }} resultado(s)</span>
      </div>
      <div v-if="selecaoIds.length" class="flex flex-wrap items-center gap-3 px-4 py-3 bg-rose-50 border-b border-rose-100">
        <span class="text-sm font-medium text-rose-700">{{ selecaoIds.length }} selecionado(s)</span>
        <select v-model="bulkAtribuirSecaoId" class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-rose-400 bg-white">
          <option :value="null">Atribuir seção…</option>
          <option v-for="sec in secoes" :key="sec.id" :value="sec.id">{{ sec.nome }}</option>
          <option :value="0">Remover seção</option>
        </select>
        <button
          :disabled="bulkAtribuirSecaoId === null || salvandoBulk"
          @click="aplicarBulkSecao"
          class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-1.5 rounded-lg disabled:opacity-50"
        >{{ salvandoBulk ? 'Aplicando...' : 'Aplicar' }}</button>
        <button
          v-if="auth.isAdmin"
          :disabled="salvandoBulk"
          @click="inativarBulkServicos"
          class="bg-amber-500 hover:bg-amber-600 text-white text-sm font-medium px-4 py-1.5 rounded-lg disabled:opacity-50"
        >{{ salvandoBulk ? 'Aplicando...' : 'Inativar selecionados' }}</button>
        <button
          v-if="auth.isAdmin"
          :disabled="salvandoBulk"
          @click="excluirBulkServicos"
          class="bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-4 py-1.5 rounded-lg disabled:opacity-50"
        >{{ salvandoBulk ? 'Aplicando...' : 'Excluir selecionados' }}</button>
        <button @click="selecaoIds = []" class="text-sm text-gray-500 hover:text-gray-700 ml-auto">Limpar</button>
      </div>
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <div v-else-if="!servicos.length" class="p-8 text-center text-sm text-gray-400">Nenhum serviço cadastrado.</div>

      <!-- Mobile: cards -->
      <div v-else class="sm:hidden divide-y divide-gray-100">
        <div v-for="s in servicosFiltrados" :key="s.id" class="p-4">
          <div class="flex items-start gap-3 mb-1">
            <input type="checkbox" :value="s.id" v-model="selecaoIds" class="accent-rose-600 mt-1 flex-shrink-0" />
            <div class="flex-1 flex items-start justify-between gap-2">
              <div>
                <p class="font-medium text-gray-800 text-sm">{{ s.nome }}</p>
                <span v-if="s.secao_id" class="text-xs text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full font-medium">{{ nomeSecao(s.secao_id) }}</span>
              </div>
              <span :class="s.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0">{{ s.ativo ? 'Ativo' : 'Inativo' }}</span>
            </div>
          </div>
          <p v-if="s.descricao" class="text-xs text-gray-400 mb-1">{{ s.descricao }}</p>
          <div class="flex items-center gap-3 text-xs text-gray-500 mb-3">
            <span>{{ s.duracao_minutos }} min</span>
            <span>·</span>
            <span class="font-medium text-gray-700">R$ {{ Number(s.preco).toFixed(2) }}</span>
            <span v-if="s.preco_minimo || s.preco_maximo" class="text-gray-400">(R$ {{ s.preco_minimo ? Number(s.preco_minimo).toFixed(2) : '—' }} → R$ {{ s.preco_maximo ? Number(s.preco_maximo).toFixed(2) : '—' }})</span>
          </div>
          <div v-if="auth.isAdmin" class="flex gap-2">
            <button @click="abrirModalEditar(s)" class="flex-1 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg py-2 px-3">Editar</button>
            <button @click="confirmarExclusao(s)" class="text-xs font-medium text-red-500 bg-red-50 hover:bg-red-100 rounded-lg py-2 px-3">Excluir</button>
          </div>
        </div>
      </div>

      <!-- Desktop: tabela -->
      <table v-if="!loading && servicos.length" class="hidden sm:table w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="px-4 py-3 w-10">
              <input type="checkbox" :checked="todosSelecionados" @change="toggleSelecionarTodos" class="accent-rose-600" />
            </th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Seção</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Descrição</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Duração</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Valor Base</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Range de Preço</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Ativo</th>
            <th v-if="auth.isAdmin" class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="s in servicosFiltrados" :key="s.id" class="hover:bg-gray-50">
            <td class="px-4 py-3">
              <input type="checkbox" :value="s.id" v-model="selecaoIds" class="accent-rose-600" />
            </td>
            <td class="px-4 py-3 font-medium text-gray-800">{{ s.nome }}</td>
            <td class="px-4 py-3">
              <span v-if="s.secao_id" class="text-xs text-rose-600 bg-rose-50 px-2 py-0.5 rounded-full font-medium">{{ nomeSecao(s.secao_id) }}</span>
              <span v-else class="text-gray-300 text-xs">—</span>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ s.descricao || '-' }}</td>
            <td class="px-4 py-3 text-gray-500">{{ s.duracao_minutos }} min</td>
            <td class="px-4 py-3 text-gray-700">R$ {{ Number(s.preco).toFixed(2) }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">
              <span v-if="s.preco_minimo || s.preco_maximo">
                R$ {{ s.preco_minimo ? Number(s.preco_minimo).toFixed(2) : '—' }} →
                R$ {{ s.preco_maximo ? Number(s.preco_maximo).toFixed(2) : '—' }}
              </span>
              <span v-else class="text-gray-300">—</span>
            </td>
            <td class="px-4 py-3">
              <span :class="s.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs px-2 py-0.5 rounded-full font-medium">
                {{ s.ativo ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td v-if="auth.isAdmin" class="px-4 py-3 text-right space-x-2">
              <button @click="abrirModalEditar(s)" class="text-xs text-blue-600 hover:underline">Editar</button>
              <button @click="confirmarExclusao(s)" class="text-xs text-red-500 hover:underline">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Novo Serviço -->
    <div v-if="modalAberto" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4" @click.self="fecharModal">
      <div class="bg-white w-full sm:max-w-md sm:rounded-xl rounded-t-3xl shadow-xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>
        <div class="flex-1 overflow-y-auto px-6 pt-5 pb-2">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Novo Serviço</h3>
          <form id="form-novo-servico" @submit.prevent="salvar" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
              <input v-model="form.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
              <input v-model="form.descricao" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Duração (min) *</label>
                <input v-model.number="form.duracao_minutos" type="number" min="1" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Preço Base (R$) *</label>
                <input v-model="form.preco" type="number" step="0.01" min="0" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Range de Preço <span class="text-gray-400 font-normal">(opcional)</span></label>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Mínimo (R$)</label>
                <input v-model="form.preco_minimo" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Máximo (R$)</label>
                <input v-model="form.preco_maximo" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>
            </div>
          </div>
          <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Seção <span class="text-gray-400 font-normal">(opcional)</span></label>
              <select v-model="form.secao_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
                <option :value="null">Sem seção</option>
                <option v-for="sec in secoes" :key="sec.id" :value="sec.id">{{ sec.nome }}</option>
              </select>
            </div>
          <p v-if="erro" class="text-sm text-red-600">{{ erro }}</p>
          </form>
        </div>
        <div class="flex gap-2 px-6 py-4 border-t border-gray-100 flex-shrink-0">
          <button type="button" @click="fecharModal" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button type="submit" form="form-novo-servico" :disabled="salvando" class="flex-1 bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Editar Serviço -->
    <div v-if="modalEditar" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4" @click.self="modalEditar = false">
      <div class="bg-white w-full sm:max-w-md sm:rounded-xl rounded-t-3xl shadow-xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>
        <div class="flex-1 overflow-y-auto px-6 pt-5 pb-2">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Editar Serviço</h3>
          <form id="form-editar-servico" @submit.prevent="salvarEdicao" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input v-model="formEditar.nome" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
              <input v-model="formEditar.descricao" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Duração (min)</label>
                <input v-model.number="formEditar.duracao_minutos" type="number" min="1" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço Base (R$)</label>
              <input v-model="formEditar.preco" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Range de Preço <span class="text-gray-400 font-normal">(opcional)</span></label>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Mínimo (R$)</label>
                <input v-model="formEditar.preco_minimo" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Máximo (R$)</label>
                <input v-model="formEditar.preco_maximo" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="formEditar.ativo" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
              <option :value="true">Ativo</option>
              <option :value="false">Inativo</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Seção <span class="text-gray-400 font-normal">(opcional)</span></label>
            <select v-model="formEditar.secao_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
              <option :value="null">Sem seção</option>
              <option v-for="sec in secoes" :key="sec.id" :value="sec.id">{{ sec.nome }}</option>
            </select>
          </div>
          <p v-if="erroEditar" class="text-sm text-red-600">{{ erroEditar }}</p>
          </form>
        </div>
        <div class="flex gap-2 px-6 py-4 border-t border-gray-100 flex-shrink-0">
          <button type="button" @click="modalEditar = false" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button type="submit" form="form-editar-servico" :disabled="salvando" class="flex-1 bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Confirmar Exclusão -->
    <div v-if="servicoParaExcluir" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4">
      <div class="bg-white w-full sm:max-w-xs sm:rounded-xl rounded-t-3xl shadow-xl p-6 text-center">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mb-4"></div>
        <p class="text-sm text-gray-700 mb-1">Excluir serviço</p>
        <p class="font-semibold text-gray-900 mb-6">{{ servicoParaExcluir.nome }}</p>
        <div class="flex gap-2">
          <button @click="servicoParaExcluir = null" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button @click="excluirServico" :disabled="salvando" class="flex-1 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ salvando ? 'Excluindo...' : 'Excluir' }}
          </button>
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
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const servicos = ref([])
const loading = ref(true)
const modalAberto = ref(false)
const modalEditar = ref(false)
const salvando = ref(false)
const erro = ref('')
const erroEditar = ref('')
const editandoId = ref(null)
const servicoParaExcluir = ref(null)
const form = ref({ nome: '', descricao: '', duracao_minutos: null, preco: '', preco_minimo: null, preco_maximo: null, secao_id: null })
const formEditar = ref({ nome: '', descricao: '', duracao_minutos: null, preco: '', preco_minimo: null, preco_maximo: null, ativo: true, secao_id: null })

// ─── Seções ───────────────────────────────────────────────────────────────
const secoes = ref([])
const gerenciandoSecoes = ref(false)
const novaSecao = ref('')
const salvandoSecao = ref(false)
const erroSecao = ref('')

async function fetchSecoes() {
  try {
    const { data } = await api.get('/secoes/')
    secoes.value = data
  } catch {
    // silencioso
  }
}

async function criarSecao() {
  if (!novaSecao.value.trim()) return
  salvandoSecao.value = true
  erroSecao.value = ''
  try {
    await api.post('/secoes/', { nome: novaSecao.value.trim() })
    novaSecao.value = ''
    toastSucesso('Seção criada!')
    await fetchSecoes()
  } catch (e) {
    erroSecao.value = e.response?.data?.detail || 'Erro ao criar seção.'
  } finally {
    salvandoSecao.value = false
  }
}

async function excluirSecao(secao) {
  if (!confirm(`Excluir a seção "${secao.nome}"? Os serviços vinculados ficarão sem seção.`)) return
  try {
    await api.delete(`/secoes/${secao.id}`)
    toastSucesso('Seção excluída.')
    await fetchSecoes()
    await fetchServicos()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir seção.')
  }
}

function nomeSecao(id) {
  return secoes.value.find(s => s.id === id)?.nome ?? '—'
}
// ──────────────────────────────────────────────────────────────────────────

// ─── Seleção + filtro ──────────────────────────────────────────────────────
const filtroSecao = ref(null)   // null = todas, 0 = sem seção, N = id da seção
const filtroStatus = ref('todos') // todos | ativos | inativos
const selecaoIds = ref([])      // IDs dos serviços selecionados
const bulkAtribuirSecaoId = ref(null)
const salvandoBulk = ref(false)

const servicosFiltrados = computed(() => {
  let lista = servicos.value
  if (filtroSecao.value === 0) {
    lista = lista.filter(s => !s.secao_id)
  } else if (filtroSecao.value !== null) {
    lista = lista.filter(s => s.secao_id === filtroSecao.value)
  }

  if (filtroStatus.value === 'ativos') {
    lista = lista.filter(s => s.ativo)
  } else if (filtroStatus.value === 'inativos') {
    lista = lista.filter(s => !s.ativo)
  }

  return lista
})

const todosSelecionados = computed(() => {
  const ids = servicosFiltrados.value.map(s => s.id)
  return ids.length > 0 && ids.every(id => selecaoIds.value.includes(id))
})

function toggleSelecionarTodos() {
  const ids = servicosFiltrados.value.map(s => s.id)
  if (todosSelecionados.value) {
    selecaoIds.value = selecaoIds.value.filter(id => !ids.includes(id))
  } else {
    selecaoIds.value = [...new Set([...selecaoIds.value, ...ids])]
  }
}

async function aplicarBulkSecao() {
  if (bulkAtribuirSecaoId.value === null) return
  salvandoBulk.value = true
  try {
    await Promise.all(
      selecaoIds.value.map(id =>
        api.patch(`/servicos/${id}`, { secao_id: bulkAtribuirSecaoId.value === 0 ? null : bulkAtribuirSecaoId.value })
      )
    )
    toastSucesso('Seção atribuída com sucesso!')
    selecaoIds.value = []
    bulkAtribuirSecaoId.value = null
    await fetchServicos()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao atualizar seções.')
  } finally {
    salvandoBulk.value = false
  }
}

async function inativarBulkServicos() {
  if (!selecaoIds.value.length) return
  if (!confirm(`Inativar ${selecaoIds.value.length} serviço(s) selecionado(s)?`)) return
  salvandoBulk.value = true
  try {
    await Promise.all(
      selecaoIds.value.map(id => api.patch(`/servicos/${id}`, { ativo: false }))
    )
    toastSucesso('Serviços inativados com sucesso!')
    selecaoIds.value = []
    await fetchServicos()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao inativar serviços selecionados.')
  } finally {
    salvandoBulk.value = false
  }
}

async function excluirBulkServicos() {
  if (!selecaoIds.value.length) return
  if (!confirm(`Excluir ${selecaoIds.value.length} serviço(s) selecionado(s)? Esta ação não pode ser desfeita.`)) return
  salvandoBulk.value = true
  try {
    await Promise.all(
      selecaoIds.value.map(id => api.delete(`/servicos/${id}`))
    )
    toastSucesso('Serviços excluídos com sucesso!')
    selecaoIds.value = []
    await fetchServicos()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir serviços selecionados.')
  } finally {
    salvandoBulk.value = false
  }
}
// ──────────────────────────────────────────────────────────────────────────

async function fetchServicos() {
  loading.value = true
  try {
    const { data } = await api.get('/servicos/?apenas_ativos=false')
    servicos.value = data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchServicos()
  fetchSecoes()
})

function abrirModal() {
  form.value = { nome: '', descricao: '', duracao_minutos: null, preco: '', preco_minimo: null, preco_maximo: null, secao_id: null }
  erro.value = ''
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
}

function abrirModalEditar(s) {
  editandoId.value = s.id
  formEditar.value = {
    nome: s.nome,
    descricao: s.descricao || '',
    duracao_minutos: s.duracao_minutos,
    preco: s.preco,
    preco_minimo: s.preco_minimo ?? null,
    preco_maximo: s.preco_maximo ?? null,
    ativo: s.ativo,
    secao_id: s.secao_id ?? null,
  }
  erroEditar.value = ''
  modalEditar.value = true
}

function confirmarExclusao(s) {
  servicoParaExcluir.value = s
}

async function salvar() {
  salvando.value = true
  erro.value = ''
  try {
    await api.post('/servicos/', {
      nome: form.value.nome,
      descricao: form.value.descricao || null,
      duracao_minutos: form.value.duracao_minutos,
      preco: form.value.preco,
      preco_minimo: form.value.preco_minimo || null,
      preco_maximo: form.value.preco_maximo || null,
      secao_id: form.value.secao_id || null,
    })
    fecharModal()
    toastSucesso('Serviço criado com sucesso!')
    await fetchServicos()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao salvar serviço.'
  } finally {
    salvando.value = false
  }
}

async function salvarEdicao() {
  salvando.value = true
  erroEditar.value = ''
  try {
    await api.patch(`/servicos/${editandoId.value}`, formEditar.value)
    modalEditar.value = false
    toastSucesso('Serviço atualizado com sucesso!')
    await fetchServicos()
  } catch (e) {
    erroEditar.value = e.response?.data?.detail || 'Erro ao atualizar serviço.'
  } finally {
    salvando.value = false
  }
}

async function excluirServico() {
  salvando.value = true
  try {
    await api.delete(`/servicos/${servicoParaExcluir.value.id}`)
    servicoParaExcluir.value = null
    await fetchServicos()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir serviço.')
  } finally {
    salvando.value = false
  }
}
</script>
