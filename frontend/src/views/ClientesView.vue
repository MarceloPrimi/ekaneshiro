<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-xl font-bold text-gray-800">Clientes</h2>
      <button
        class="bg-rose-600 text-white text-sm font-semibold px-4 py-2 rounded-lg hover:bg-rose-700 transition-colors"
        @click="openModal()"
      >
        + Novo
      </button>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Email</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Telefone</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="c in clientes" :key="c.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ c.nome }}</td>
            <td class="px-4 py-3 text-gray-500">{{ c.email || '-' }}</td>
            <td class="px-4 py-3 text-gray-500">{{ c.telefone || '-' }}</td>
            <td class="px-4 py-3">
              <button class="text-xs text-blue-600 hover:underline mr-3" @click="openModal(c)">Editar</button>
              <button class="text-xs text-red-500 hover:underline" @click="remover(c.id)">Remover</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">{{ editando ? 'Editar' : 'Novo' }} Cliente</h3>
        <form @submit.prevent="salvar" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input v-model="form.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input v-model="form.email" type="email" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
            <input v-model="form.telefone" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <p v-if="modalError" class="text-sm text-red-500">{{ modalError }}</p>
          <div class="flex gap-2 pt-2">
            <button type="button" class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50" @click="showModal = false">Cancelar</button>
            <button type="submit" :disabled="saving" class="flex-1 bg-rose-600 text-white rounded-lg py-2 text-sm font-semibold hover:bg-rose-700 disabled:opacity-50">
              {{ saving ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/client'

const clientes = ref([])
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const modalError = ref('')
const editando = ref(null)
const form = ref({ nome: '', email: '', telefone: '' })

async function fetch() {
  loading.value = true
  const { data } = await api.get('/clientes/')
  clientes.value = data
  loading.value = false
}

function openModal(cliente = null) {
  editando.value = cliente?.id || null
  form.value = { nome: cliente?.nome || '', email: cliente?.email || '', telefone: cliente?.telefone || '' }
  modalError.value = ''
  showModal.value = true
}

async function salvar() {
  modalError.value = ''
  saving.value = true
  try {
    if (editando.value) {
      await api.patch(`/clientes/${editando.value}`, form.value)
    } else {
      await api.post('/clientes/', form.value)
    }
    showModal.value = false
    await fetch()
  } catch (e) {
    modalError.value = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    saving.value = false
  }
}

async function remover(id) {
  if (!confirm('Remover este cliente?')) return
  await api.delete(`/clientes/${id}`)
  await fetch()
}

onMounted(fetch)
</script>
