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
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Descrição</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Duração</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Valor</th>
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
    <div v-if="modalAberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Novo Serviço</h3>
        <form @submit.prevent="salvar" class="space-y-4">
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço (R$) *</label>
              <input v-model="form.preco" type="number" step="0.01" min="0" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
          </div>
          <p v-if="erro" class="text-sm text-red-600">{{ erro }}</p>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="fecharModal" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
            <button type="submit" :disabled="salvando" class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Editar Serviço -->
    <div v-if="modalEditar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Editar Serviço</h3>
        <form @submit.prevent="salvarEdicao" class="space-y-4">
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
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço (R$)</label>
              <input v-model="formEditar.preco" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
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
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalEditar = false" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
            <button type="submit" :disabled="salvando" class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmar Exclusão -->
    <div v-if="servicoParaExcluir" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-xs mx-4 p-6 text-center">
        <p class="text-sm text-gray-700 mb-1">Excluir serviço</p>
        <p class="font-semibold text-gray-900 mb-6">{{ servicoParaExcluir.nome }}</p>
        <div class="flex justify-center gap-3">
          <button @click="servicoParaExcluir = null" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
          <button @click="excluirServico" :disabled="salvando" class="bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
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
const form = ref({ nome: '', descricao: '', duracao_minutos: null, preco: '' })
const formEditar = ref({ nome: '', descricao: '', duracao_minutos: null, preco: '', ativo: true })

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
  form.value = { nome: '', descricao: '', duracao_minutos: null, preco: '' }
  erro.value = ''
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
}

function abrirModalEditar(s) {
  editandoId.value = s.id
  formEditar.value = { nome: s.nome, descricao: s.descricao || '', duracao_minutos: s.duracao_minutos, preco: s.preco, ativo: s.ativo }
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
    })
    fecharModal()
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
