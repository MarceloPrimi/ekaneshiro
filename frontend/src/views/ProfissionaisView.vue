<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-800">Profissionais</h2>
      <button
        v-if="auth.isAdmin"
        @click="abrirModal"
        class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
      >
        + Novo Profissional
      </button>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <div v-else-if="!profissionais.length" class="p-8 text-center text-sm text-gray-400">Nenhum profissional cadastrado.</div>
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Serviços</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Usuário vinculado</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Ativo</th>
            <th v-if="auth.isAdmin" class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="p in profissionais" :key="p.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ p.nome }}</td>
            <td class="px-4 py-3 text-gray-500">
              <span
                v-for="s in p.servicos"
                :key="s.id"
                class="inline-block bg-rose-50 text-rose-600 text-xs px-2 py-0.5 rounded-full mr-1"
              >
                {{ s.nome }}
              </span>
              <span v-if="!p.servicos?.length" class="text-gray-400">-</span>
            </td>
            <td class="px-4 py-3">
              <span v-if="nomeUsuarioVinculado(p.usuario_id)" class="text-xs text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full font-medium">
                {{ nomeUsuarioVinculado(p.usuario_id) }}
              </span>
              <span v-else class="text-gray-400 text-xs">-</span>
            </td>
            <td class="px-4 py-3">
              <span :class="p.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs px-2 py-0.5 rounded-full font-medium">
                {{ p.ativo ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td v-if="auth.isAdmin" class="px-4 py-3 text-right space-x-2">
              <button @click="abrirModalEditar(p)" class="text-xs text-blue-600 hover:underline">Editar</button>
              <button @click="confirmarExclusao(p)" class="text-xs text-red-500 hover:underline">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Novo Profissional -->
    <div v-if="modalAberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Novo Profissional</h3>
        <form @submit.prevent="salvar" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input v-model="form.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Serviços</label>
            <div v-if="!servicosDisponiveis.length" class="text-xs text-gray-400">Nenhum serviço cadastrado.</div>
            <div v-else class="space-y-1 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-2">
              <label
                v-for="s in servicosDisponiveis"
                :key="s.id"
                class="flex items-center gap-2 px-1 py-1 rounded hover:bg-gray-50 cursor-pointer"
              >
                <input type="checkbox" :value="s.id" v-model="form.servico_ids" class="accent-rose-600" />
                <span class="text-sm text-gray-700">{{ s.nome }}</span>
                <span class="text-xs text-gray-400 ml-auto">{{ s.duracao_minutos }}min · R$ {{ Number(s.preco).toFixed(2) }}</span>
              </label>
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

    <!-- Modal Editar Profissional -->
    <div v-if="modalEditar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Editar Profissional</h3>
        <form @submit.prevent="salvarEdicao" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input v-model="formEditar.nome" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="formEditar.ativo" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
              <option :value="true">Ativo</option>
              <option :value="false">Inativo</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Usuário vinculado (login)</label>
            <select v-model="formEditar.usuario_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
              <option :value="null">Nenhum</option>
              <option
                v-for="u in usuariosProfissionais"
                :key="u.id"
                :value="u.id"
                :disabled="profissionais.some(p => p.usuario_id === u.id && p.id !== editandoId)"
              >
                {{ u.nome }} ({{ u.email }})
              </option>
            </select>
            <p class="text-xs text-gray-400 mt-1">Vincule um usuário com perfil 'profissional' para que ele veja apenas seus próprios agendamentos ao logar.</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Serviços</label>
            <div v-if="!servicosDisponiveis.length" class="text-xs text-gray-400">Nenhum serviço cadastrado.</div>
            <div v-else class="space-y-1 max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-2">
              <label
                v-for="s in servicosDisponiveis"
                :key="s.id"
                class="flex items-center gap-2 px-1 py-1 rounded hover:bg-gray-50 cursor-pointer"
              >
                <input type="checkbox" :value="s.id" v-model="formEditar.servico_ids" class="accent-rose-600" />
                <span class="text-sm text-gray-700">{{ s.nome }}</span>
                <span class="text-xs text-gray-400 ml-auto">{{ s.duracao_minutos }}min · R$ {{ Number(s.preco).toFixed(2) }}</span>
              </label>
            </div>
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
    <div v-if="profissionalParaExcluir" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-xs mx-4 p-6 text-center">
        <p class="text-sm text-gray-700 mb-1">Excluir profissional</p>
        <p class="font-semibold text-gray-900 mb-6">{{ profissionalParaExcluir.nome }}</p>
        <div class="flex justify-center gap-3">
          <button @click="profissionalParaExcluir = null" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
          <button @click="excluirProfissional" :disabled="salvando" class="bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
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
const profissionais = ref([])
const usuariosProfissionais = ref([])  // usuários com role=profissional para o dropdown
const servicosDisponiveis = ref([])
const loading = ref(true)
const modalAberto = ref(false)
const modalEditar = ref(false)
const salvando = ref(false)
const erro = ref('')
const erroEditar = ref('')
const editandoId = ref(null)
const editandoServicosOriginais = ref([])
const profissionalParaExcluir = ref(null)
const form = ref({ nome: '', servico_ids: [] })
const formEditar = ref({ nome: '', ativo: true, servico_ids: [], usuario_id: null })

function nomeUsuarioVinculado(usuario_id) {
  const u = usuariosProfissionais.value.find(u => u.id === usuario_id)
  return u ? u.nome : null
}

async function fetchProfissionais() {
  loading.value = true
  try {
    const { data } = await api.get('/profissionais/')
    profissionais.value = data
  } finally {
    loading.value = false
  }
}

async function fetchServicos() {
  try {
    const { data } = await api.get('/servicos/?apenas_ativos=false')
    servicosDisponiveis.value = data
  } catch {
    // silencioso
  }
}

async function fetchUsuariosProfissionais() {
  if (!auth.isAdmin) return
  try {
    const { data } = await api.get('/usuarios/')
    usuariosProfissionais.value = data.filter(u => u.role === 'profissional' && u.ativo)
  } catch {
    // silencioso
  }
}

onMounted(() => {
  fetchProfissionais()
  fetchServicos()
  fetchUsuariosProfissionais()
})

function abrirModal() {
  form.value = { nome: '', servico_ids: [] }
  erro.value = ''
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
}

function abrirModalEditar(p) {
  editandoId.value = p.id
  const idsAtuais = (p.servicos || []).map(s => s.id)
  editandoServicosOriginais.value = [...idsAtuais]
  formEditar.value = { nome: p.nome, ativo: p.ativo, servico_ids: [...idsAtuais], usuario_id: p.usuario_id ?? null }
  erroEditar.value = ''
  modalEditar.value = true
}

function confirmarExclusao(p) {
  profissionalParaExcluir.value = p
}

async function salvar() {
  salvando.value = true
  erro.value = ''
  try {
    const { data: novo } = await api.post('/profissionais/', { nome: form.value.nome })
    await Promise.all(
      form.value.servico_ids.map(sid =>
        api.post(`/profissionais/${novo.id}/servicos/${sid}`)
      )
    )
    fecharModal()
    await fetchProfissionais()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao salvar profissional.'
  } finally {
    salvando.value = false
  }
}

async function salvarEdicao() {
  salvando.value = true
  erroEditar.value = ''
  try {
    await api.patch(`/profissionais/${editandoId.value}`, {
      nome: formEditar.value.nome,
      ativo: formEditar.value.ativo,
      usuario_id: formEditar.value.usuario_id,
    })
    // calcular diffs de serviços
    const originais = new Set(editandoServicosOriginais.value)
    const novos = new Set(formEditar.value.servico_ids)
    const adicionar = [...novos].filter(id => !originais.has(id))
    const remover = [...originais].filter(id => !novos.has(id))
    await Promise.all([
      ...adicionar.map(sid => api.post(`/profissionais/${editandoId.value}/servicos/${sid}`)),
      ...remover.map(sid => api.delete(`/profissionais/${editandoId.value}/servicos/${sid}`)),
    ])
    modalEditar.value = false
    await fetchProfissionais()
  } catch (e) {
    erroEditar.value = e.response?.data?.detail || 'Erro ao atualizar profissional.'
  } finally {
    salvando.value = false
  }
}

async function excluirProfissional() {
  salvando.value = true
  try {
    await api.delete(`/profissionais/${profissionalParaExcluir.value.id}`)
    profissionalParaExcluir.value = null
    await fetchProfissionais()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir profissional.')
  } finally {
    salvando.value = false
  }
}
</script>
