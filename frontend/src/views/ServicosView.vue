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

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <div v-else-if="!servicos.length" class="p-8 text-center text-sm text-gray-400">Nenhum serviço cadastrado.</div>

      <!-- Mobile: cards -->
      <div v-else class="sm:hidden divide-y divide-gray-100">
        <div v-for="s in servicos" :key="s.id" class="p-4">
          <div class="flex items-start justify-between gap-2 mb-1">
            <p class="font-medium text-gray-800 text-sm">{{ s.nome }}</p>
            <span :class="s.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0">{{ s.ativo ? 'Ativo' : 'Inativo' }}</span>
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
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Descrição</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Duração</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Valor Base</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Range de Preço</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Ativo</th>
            <th v-if="auth.isAdmin" class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="s in servicos" :key="s.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ s.nome }}</td>
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
import { ref, onMounted } from 'vue'
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
const form = ref({ nome: '', descricao: '', duracao_minutos: null, preco: '', preco_minimo: null, preco_maximo: null })
const formEditar = ref({ nome: '', descricao: '', duracao_minutos: null, preco: '', preco_minimo: null, preco_maximo: null, ativo: true })

async function fetchServicos() {
  loading.value = true
  try {
    const { data } = await api.get('/servicos/?apenas_ativos=false')
    servicos.value = data
  } finally {
    loading.value = false
  }
}

onMounted(fetchServicos)

function abrirModal() {
  form.value = { nome: '', descricao: '', duracao_minutos: null, preco: '', preco_minimo: null, preco_maximo: null }
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
