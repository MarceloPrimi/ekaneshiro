<script setup lang="ts">
// CategoriasManager.vue — Gerenciamento de categorias de agendamento (inline no settings/modal)

import { ref, onMounted } from 'vue'
import { categoriasApi, type CategoriaAgendamento } from '@/api/categoriasApi'

const categorias = ref<CategoriaAgendamento[]>([])
const carregando = ref(false)
const erro = ref<string | null>(null)

// Formulário de nova categoria
const formNova = ref({ nome: '', cor_hex: '#6366f1' })
const salvando = ref(false)

// Edição inline
const editando = ref<number | null>(null)
const formEditar = ref({ nome: '', cor_hex: '' })

async function carregar() {
  carregando.value = true
  try {
    categorias.value = await categoriasApi.listar(false) // todas, incluindo inativas
  } catch {
    erro.value = 'Erro ao carregar categorias.'
  } finally {
    carregando.value = false
  }
}

async function criarCategoria() {
  if (!formNova.value.nome.trim()) return
  salvando.value = true
  try {
    const nova = await categoriasApi.criar(formNova.value)
    categorias.value.push(nova)
    formNova.value = { nome: '', cor_hex: '#6366f1' }
  } catch (e: any) {
    erro.value = e?.response?.data?.detail ?? 'Erro ao criar categoria.'
  } finally {
    salvando.value = false
  }
}

function iniciarEdicao(cat: CategoriaAgendamento) {
  editando.value = cat.id
  formEditar.value = { nome: cat.nome, cor_hex: cat.cor_hex }
}

async function salvarEdicao(cat: CategoriaAgendamento) {
  try {
    const atualizada = await categoriasApi.editar(cat.id, formEditar.value)
    const idx = categorias.value.findIndex(c => c.id === cat.id)
    if (idx >= 0) categorias.value[idx] = atualizada
    editando.value = null
  } catch (e: any) {
    erro.value = e?.response?.data?.detail ?? 'Erro ao salvar.'
  }
}

async function toggleAtivo(cat: CategoriaAgendamento) {
  try {
    const atualizada = await categoriasApi.editar(cat.id, { ativo: !cat.ativo })
    const idx = categorias.value.findIndex(c => c.id === cat.id)
    if (idx >= 0) categorias.value[idx] = atualizada
  } catch {
    erro.value = 'Erro ao alterar status da categoria.'
  }
}

onMounted(carregar)
</script>

<template>
  <div class="space-y-4">
    <h3 class="text-sm font-bold text-gray-700 flex items-center gap-2">
      <span>🎨</span> Categorias de Agendamento
    </h3>

    <!-- Erro -->
    <p v-if="erro" class="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
      {{ erro }}
      <button class="ml-2 underline" @click="erro = null">OK</button>
    </p>

    <!-- Lista -->
    <div v-if="carregando" class="text-sm text-gray-400 italic">Carregando...</div>
    <ul v-else class="space-y-2">
      <li
        v-for="cat in categorias"
        :key="cat.id"
        class="flex items-center gap-3 p-2 rounded-xl border"
        :class="cat.ativo ? 'border-gray-200 bg-white' : 'border-gray-100 bg-gray-50 opacity-60'"
      >
        <!-- Swatch de cor -->
        <span
          class="w-6 h-6 rounded-full border border-white shadow-sm shrink-0"
          :style="{ backgroundColor: cat.cor_hex }"
        />

        <!-- Modo edição inline -->
        <template v-if="editando === cat.id">
          <input
            v-model="formEditar.nome"
            class="flex-1 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
            maxlength="100"
          />
          <input
            v-model="formEditar.cor_hex"
            type="color"
            class="w-9 h-8 rounded cursor-pointer border border-gray-200"
            title="Cor da categoria"
          />
          <button
            class="text-xs text-green-600 font-semibold hover:underline"
            @click="salvarEdicao(cat)"
          >Salvar</button>
          <button
            class="text-xs text-gray-400 hover:underline"
            @click="editando = null"
          >Cancelar</button>
        </template>

        <!-- Modo leitura -->
        <template v-else>
          <span class="flex-1 text-sm font-medium text-gray-700 truncate">{{ cat.nome }}</span>
          <button
            class="text-xs text-indigo-500 hover:underline"
            @click="iniciarEdicao(cat)"
          >Editar</button>
          <button
            class="text-xs hover:underline"
            :class="cat.ativo ? 'text-red-400' : 'text-green-500'"
            @click="toggleAtivo(cat)"
          >{{ cat.ativo ? 'Desativar' : 'Ativar' }}</button>
        </template>
      </li>
    </ul>

    <!-- Formulário nova categoria -->
    <div class="flex items-center gap-2 pt-2 border-t border-gray-100">
      <input
        v-model="formNova.cor_hex"
        type="color"
        class="w-9 h-9 rounded cursor-pointer border border-gray-200 shrink-0"
        title="Cor da nova categoria"
      />
      <input
        v-model="formNova.nome"
        type="text"
        placeholder="Nome da nova categoria..."
        maxlength="100"
        class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
        @keyup.enter="criarCategoria"
      />
      <button
        :disabled="salvando || !formNova.nome.trim()"
        class="bg-indigo-600 text-white text-sm font-semibold px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shrink-0"
        @click="criarCategoria"
      >
        {{ salvando ? '...' : '+ Criar' }}
      </button>
    </div>
  </div>
</template>
