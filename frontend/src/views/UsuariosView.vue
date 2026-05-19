<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-800">Gerenciamento de Usuários</h2>
      <button @click="abrirModalCriar" class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
        + Novo Usuário
      </button>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <div v-else-if="!usuarios.length" class="p-8 text-center text-sm text-gray-400">Nenhum usuário encontrado.</div>

      <!-- Mobile: cards -->
      <div v-else class="sm:hidden divide-y divide-gray-100">
        <div v-for="u in usuarios" :key="u.id" class="p-4">
          <div class="flex items-start justify-between gap-2 mb-1">
            <div class="min-w-0">
              <p class="font-medium text-gray-800 text-sm">{{ u.nome }}</p>
              <p class="text-xs text-gray-400 truncate mt-0.5">{{ u.email }}</p>
            </div>
            <div class="flex gap-1.5 flex-shrink-0">
              <span :class="roleBadge(u.role)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ roleLabel(u.role) }}</span>
              <span :class="u.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ u.ativo ? 'Ativo' : 'Inativo' }}</span>
            </div>
          </div>
          <div class="flex gap-2 mt-3">
            <button @click="abrirModalEditar(u)" class="flex-1 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg py-2 px-3">Editar</button>
            <button v-if="u.id !== auth.user?.id" @click="confirmarExclusao(u)" class="text-xs font-medium text-red-500 bg-red-50 hover:bg-red-100 rounded-lg py-2 px-3">Excluir</button>
          </div>
        </div>
      </div>

      <!-- Desktop: tabela -->
      <table v-if="!loading && usuarios.length" class="hidden sm:table w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Email</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Perfil</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Status</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="u in usuarios" :key="u.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ u.nome }}</td>
            <td class="px-4 py-3 text-gray-500">{{ u.email }}</td>
            <td class="px-4 py-3">
              <span :class="roleBadge(u.role)" class="text-xs px-2 py-0.5 rounded-full font-medium">
                {{ roleLabel(u.role) }}
              </span>
            </td>
            <td class="px-4 py-3">
              <span :class="u.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs px-2 py-0.5 rounded-full font-medium">
                {{ u.ativo ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right space-x-2">
              <button @click="abrirModalEditar(u)" class="text-xs text-blue-600 hover:underline">Editar</button>
              <button
                v-if="u.id !== auth.user?.id"
                @click="confirmarExclusao(u)"
                class="text-xs text-red-500 hover:underline"
              >Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Criar -->
    <div v-if="modalCriar" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4" @click.self="modalCriar = false">
      <div class="bg-white w-full sm:max-w-sm sm:rounded-xl rounded-t-3xl shadow-xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>
        <div class="flex-1 overflow-y-auto px-6 pt-5 pb-2">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Novo Usuário</h3>
          <form id="form-criar-usuario" @submit.prevent="criarUsuario" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
              <input v-model="formCriar.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
              <input v-model="formCriar.email" type="email" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Senha *</label>
              <input v-model="formCriar.password" type="password" required minlength="6" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Perfil *</label>
              <select v-model="formCriar.role" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
                <option value="admin">Admin</option>
                <option value="recepcionista">Recepcionista</option>
                <option value="profissional">Profissional</option>
              </select>
            </div>
            <p v-if="erroCriar" class="text-sm text-red-600">{{ erroCriar }}</p>
          </form>
        </div>
        <div class="flex gap-2 px-6 py-4 border-t border-gray-100 flex-shrink-0">
          <button type="button" @click="modalCriar = false" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button type="submit" form="form-criar-usuario" :disabled="salvando" class="flex-1 bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ salvando ? 'Salvando...' : 'Criar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Editar -->
    <div v-if="modalEditar" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4" @click.self="modalEditar = false">
      <div class="bg-white w-full sm:max-w-sm sm:rounded-xl rounded-t-3xl shadow-xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>
        <div class="flex-1 overflow-y-auto px-6 pt-5 pb-2">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Editar Usuário</h3>
          <form id="form-editar-usuario" @submit.prevent="salvarEdicao" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
              <input v-model="formEditar.nome" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Perfil</label>
              <select v-model="formEditar.role" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
                <option value="admin">Admin</option>
                <option value="recepcionista">Recepcionista</option>
                <option value="profissional">Profissional</option>
              </select>
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
          <button type="submit" form="form-editar-usuario" :disabled="salvando" class="flex-1 bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Confirmar Exclusão -->
    <div v-if="usuarioParaExcluir" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4">
      <div class="bg-white w-full sm:max-w-xs sm:rounded-xl rounded-t-3xl shadow-xl p-6 text-center">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mb-4"></div>
        <p class="text-sm text-gray-700 mb-1">Excluir usuário</p>
        <p class="font-semibold text-gray-900 mb-4">{{ usuarioParaExcluir.nome }}</p>
        <p class="text-xs text-gray-500 mb-6">Esta ação não pode ser desfeita.</p>
        <div class="flex gap-2">
          <button @click="usuarioParaExcluir = null" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button @click="excluirUsuario" :disabled="salvando" class="flex-1 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
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
const usuarios = ref([])
const loading = ref(true)
const salvando = ref(false)
const modalCriar = ref(false)
const modalEditar = ref(false)
const usuarioParaExcluir = ref(null)
const editandoId = ref(null)
const erroCriar = ref('')
const erroEditar = ref('')

const formCriar = ref({ nome: '', email: '', password: '', role: 'recepcionista' })
const formEditar = ref({ nome: '', role: 'recepcionista', ativo: true })

const roleLabel = (role) => ({ admin: 'Admin', recepcionista: 'Recepcionista', profissional: 'Profissional' }[role] ?? role)
const roleBadge = (role) => ({
  admin: 'bg-purple-100 text-purple-700',
  recepcionista: 'bg-blue-100 text-blue-700',
  profissional: 'bg-rose-100 text-rose-700',
}[role] ?? 'bg-gray-100 text-gray-600')

async function fetchUsuarios() {
  loading.value = true
  try {
    const { data } = await api.get('/usuarios/')
    usuarios.value = data
  } finally {
    loading.value = false
  }
}

onMounted(fetchUsuarios)

function abrirModalCriar() {
  formCriar.value = { nome: '', email: '', password: '', role: 'recepcionista' }
  erroCriar.value = ''
  modalCriar.value = true
}

function abrirModalEditar(u) {
  editandoId.value = u.id
  formEditar.value = { nome: u.nome, role: u.role, ativo: u.ativo }
  erroEditar.value = ''
  modalEditar.value = true
}

function confirmarExclusao(u) {
  usuarioParaExcluir.value = u
}

async function criarUsuario() {
  salvando.value = true
  erroCriar.value = ''
  try {
    await api.post('/usuarios/', formCriar.value)
    modalCriar.value = false
    toastSucesso('Usuário criado com sucesso!')
    await fetchUsuarios()
  } catch (e) {
    erroCriar.value = e.response?.data?.detail || 'Erro ao criar usuário.'
  } finally {
    salvando.value = false
  }
}

async function salvarEdicao() {
  salvando.value = true
  erroEditar.value = ''
  try {
    await api.patch(`/usuarios/${editandoId.value}`, formEditar.value)
    modalEditar.value = false
    toastSucesso('Usuário atualizado com sucesso!')
    await fetchUsuarios()
  } catch (e) {
    erroEditar.value = e.response?.data?.detail || 'Erro ao atualizar usuário.'
  } finally {
    salvando.value = false
  }
}

async function excluirUsuario() {
  salvando.value = true
  try {
    await api.delete(`/usuarios/${usuarioParaExcluir.value.id}`)
    usuarioParaExcluir.value = null
    await fetchUsuarios()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir usuário.')
  } finally {
    salvando.value = false
  }
}
</script>
