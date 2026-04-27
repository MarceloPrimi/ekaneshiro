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
      <table v-else class="w-full text-sm">
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
    <div v-if="modalCriar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Novo Usuário</h3>
        <form @submit.prevent="criarUsuario" class="space-y-4">
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
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalCriar = false" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
            <button type="submit" :disabled="salvando" class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
              {{ salvando ? 'Salvando...' : 'Criar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Editar -->
    <div v-if="modalEditar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Editar Usuário</h3>
        <form @submit.prevent="salvarEdicao" class="space-y-4">
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
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalEditar = false" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
            <button type="submit" :disabled="salvando" class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Confirmar Exclusão -->
    <div v-if="usuarioParaExcluir" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-xs mx-4 p-6 text-center">
        <p class="text-sm text-gray-700 mb-1">Excluir usuário</p>
        <p class="font-semibold text-gray-900 mb-4">{{ usuarioParaExcluir.nome }}</p>
        <p class="text-xs text-gray-500 mb-6">Esta ação não pode ser desfeita.</p>
        <div class="flex justify-center gap-3">
          <button @click="usuarioParaExcluir = null" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
          <button @click="excluirUsuario" :disabled="salvando" class="bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
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
