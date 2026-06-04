<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex gap-1 bg-gray-100 p-1 rounded-lg">
        <button
          @click="abaAtiva = 'produtos'"
          :class="['text-sm font-medium px-4 py-1.5 rounded-md transition', abaAtiva === 'produtos' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500 hover:text-gray-700']"
        >Produtos</button>
        <button
          @click="abaAtiva = 'categorias'"
          :class="['text-sm font-medium px-4 py-1.5 rounded-md transition', abaAtiva === 'categorias' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500 hover:text-gray-700']"
        >Categorias</button>
      </div>
      <button
        v-if="(auth.isAdmin || auth.isRecepcionista) && abaAtiva === 'produtos'"
        @click="abrirModalNovo"
        class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
      >
        + Novo Produto
      </button>
      <button
        v-if="(auth.isAdmin || auth.isRecepcionista) && abaAtiva === 'categorias'"
        @click="abrirModalNovaCategoria"
        class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
      >
        + Nova Categoria
      </button>
    </div>

    <!-- Filtros -->
    <div v-if="abaAtiva === 'produtos'" class="flex flex-wrap gap-3 mb-4">
      <input
        v-model="busca"
        placeholder="Buscar produto..."
        class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-56 focus:outline-none focus:ring-2 focus:ring-rose-400"
      />
      <select
        v-model="filtroCategoria"
        class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-rose-400"
      >
        <option value="">Todas as categorias</option>
        <option v-for="c in categorias.filter(c => c.ativo)" :key="c.id" :value="c.nome">{{ c.nome }}</option>
      </select>
      <label class="flex items-center gap-2 text-sm text-gray-600 select-none">
        <input type="checkbox" v-model="apenasAtivos" class="accent-rose-600" />
        Apenas ativos
      </label>
      <label class="flex items-center gap-2 text-sm text-orange-600 font-medium select-none">
        <input type="checkbox" v-model="apenasEstoqueBaixo" class="accent-orange-500" />
        Estoque baixo
      </label>
    </div>

    <!-- Tabela -->
    <div v-if="abaAtiva === 'produtos'" class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <div v-else-if="!produtosFiltrados.length" class="p-8 text-center text-sm text-gray-400">Nenhum produto encontrado.</div>
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Categoria</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Marca</th>
            <th class="text-right px-4 py-3 font-medium text-gray-600">Estoque</th>
            <th class="text-right px-4 py-3 font-medium text-gray-600">Mínimo</th>
            <th class="text-right px-4 py-3 font-medium text-gray-600">Custo</th>
            <th class="text-right px-4 py-3 font-medium text-gray-600">Venda</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Status</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="p in produtosFiltrados" :key="p.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">{{ p.nome }}</td>
            <td class="px-4 py-3 text-gray-500">{{ p.categoria || '—' }}</td>
            <td class="px-4 py-3 text-gray-500">{{ p.marca || '—' }}</td>
            <td class="px-4 py-3 text-right">
              <span :class="estoqueClass(p)" class="font-semibold">{{ Number(p.estoque_atual) }}</span>
            </td>
            <td class="px-4 py-3 text-right text-gray-500">{{ Number(p.estoque_minimo) }}</td>
            <td class="px-4 py-3 text-right text-gray-500">{{ p.preco_custo != null ? 'R$ ' + Number(p.preco_custo).toFixed(2) : '—' }}</td>
            <td class="px-4 py-3 text-right text-gray-700">{{ p.preco_venda != null ? 'R$ ' + Number(p.preco_venda).toFixed(2) : '—' }}</td>
            <td class="px-4 py-3">
              <span
                :class="p.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                class="text-xs px-2 py-0.5 rounded-full font-medium"
              >{{ p.ativo ? 'Ativo' : 'Inativo' }}</span>
            </td>
            <td class="px-4 py-3 text-right space-x-2 whitespace-nowrap">
              <button @click="abrirAjuste(p)" class="text-xs text-emerald-600 hover:underline">Ajuste</button>
              <button @click="abrirModalEditar(p)" class="text-xs text-blue-600 hover:underline">Editar</button>
              <button @click="confirmarExclusao(p)" class="text-xs text-red-500 hover:underline">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Categorias -->
    <div v-if="abaAtiva === 'categorias'">
      <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div v-if="loadingCategorias" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
        <div v-else-if="!categorias.length" class="p-8 text-center text-sm text-gray-400">Nenhuma categoria cadastrada.</div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
              <th class="text-left px-4 py-3 font-medium text-gray-600">Status</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr v-for="c in categorias" :key="c.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-800">{{ c.nome }}</td>
              <td class="px-4 py-3">
                <span :class="c.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs px-2 py-0.5 rounded-full font-medium">
                  {{ c.ativo ? 'Ativa' : 'Inativa' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right space-x-2">
                <template v-if="auth.isAdmin || auth.isRecepcionista">
                  <button @click="abrirEditarCategoria(c)" class="text-xs text-blue-600 hover:underline">Editar</button>
                  <button @click="excluirCategoria(c)" class="text-xs text-red-500 hover:underline">Excluir</button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Novo Produto -->
    <div v-if="modalNovo" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Novo Produto</h3>
        <form @submit.prevent="salvarNovo" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
              <input v-model="formNovo.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
              <select v-model="formNovo.categoria" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
                <option value="">-- Selecionar --</option>
                <option v-for="c in categorias.filter(c => c.ativo)" :key="c.id" :value="c.nome">{{ c.nome }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Marca</label>
              <input v-model="formNovo.marca" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
              <input v-model="formNovo.descricao" placeholder="ex: shampoo 300ml, hidratante kg..." class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Estoque inicial</label>
              <input v-model="formNovo.estoque_atual" type="number" step="1" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Estoque mínimo</label>
              <input v-model="formNovo.estoque_minimo" type="number" step="1" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço de custo (R$)</label>
              <input v-model="formNovo.preco_custo" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço de venda (R$)</label>
              <input v-model="formNovo.preco_venda" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
          </div>
          <p v-if="erroNovo" class="text-sm text-red-600">{{ erroNovo }}</p>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalNovo = false" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
            <button type="submit" :disabled="salvando" class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Editar Produto -->
    <div v-if="modalEditar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Editar Produto</h3>
        <form @submit.prevent="salvarEdicao" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
              <input v-model="formEditar.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Categoria</label>
              <select v-model="formEditar.categoria" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
                <option value="">-- Selecionar --</option>
                <option v-for="c in categorias.filter(c => c.ativo)" :key="c.id" :value="c.nome">{{ c.nome }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Marca</label>
              <input v-model="formEditar.marca" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
              <input v-model="formEditar.descricao" placeholder="ex: shampoo 300ml, hidratante kg..." class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select v-model="formEditar.ativo" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
                <option :value="true">Ativo</option>
                <option :value="false">Inativo</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Estoque mínimo</label>
              <input v-model="formEditar.estoque_minimo" type="number" step="1" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço de custo (R$)</label>
              <input v-model="formEditar.preco_custo" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Preço de venda (R$)</label>
              <input v-model="formEditar.preco_venda" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
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

    <!-- Modal Ajuste de Estoque -->
    <div v-if="modalAjuste" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-1">Ajuste de Estoque</h3>
        <p class="text-sm text-gray-500 mb-4">{{ produtoAjuste?.nome }} — atual: <span class="font-semibold">{{ produtoAjuste?.estoque_atual }} un</span></p>
        <form @submit.prevent="salvarAjuste" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Quantidade *</label>
            <p class="text-xs text-gray-400 mb-1">Positivo = entrada &nbsp;|&nbsp; Negativo = saída</p>
            <input v-model="formAjuste.quantidade" type="number" step="1" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Motivo</label>
            <input v-model="formAjuste.motivo" placeholder="ex: compra, uso no atendimento..." class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <p v-if="erroAjuste" class="text-sm text-red-600">{{ erroAjuste }}</p>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalAjuste = false" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
            <button type="submit" :disabled="salvando" class="bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
              {{ salvando ? 'Salvando...' : 'Confirmar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirmar Exclusão -->
    <div v-if="produtoParaExcluir" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-xs mx-4 p-6 text-center">
        <p class="text-sm text-gray-700 mb-1">Excluir produto</p>
        <p class="font-semibold text-gray-900 mb-6">{{ produtoParaExcluir.nome }}</p>
        <div class="flex justify-center gap-3">
          <button @click="produtoParaExcluir = null" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
          <button @click="excluirProduto" :disabled="salvando" class="bg-red-600 hover:bg-red-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
            {{ salvando ? 'Excluindo...' : 'Excluir' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Categoria (nova / editar) -->
    <div v-if="modalCategoria" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">{{ editandoCategoriaId ? 'Editar Categoria' : 'Nova Categoria' }}</h3>
        <form @submit.prevent="salvarCategoria" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input v-model="formCategoria.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <div v-if="editandoCategoriaId">
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="formCategoria.ativo" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
              <option :value="true">Ativa</option>
              <option :value="false">Inativa</option>
            </select>
          </div>
          <p v-if="erroCategoria" class="text-sm text-red-600">{{ erroCategoria }}</p>
          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="modalCategoria = false" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
            <button type="submit" :disabled="salvando" class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

defineOptions({ name: 'ProdutosView' })
import api from '@/api/client'
import { useToast } from '@/composables/useToast'

const { sucesso: toastSucesso } = useToast()
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const produtos = ref([])
const loading = ref(true)
const salvando = ref(false)

// Filtros
const busca = ref('')
const filtroCategoria = ref('')
const apenasAtivos = ref(true)
const apenasEstoqueBaixo = ref(false)

// Modais
const modalNovo = ref(false)
const modalEditar = ref(false)
const modalAjuste = ref(false)
const produtoParaExcluir = ref(null)
const produtoAjuste = ref(null)
const editandoId = ref(null)

const erroNovo = ref('')
const erroEditar = ref('')
const erroAjuste = ref('')

const formNovo = ref({ nome: '', descricao: '', categoria: '', marca: '', estoque_atual: 0, estoque_minimo: 0, preco_custo: '', preco_venda: '' })
const formEditar = ref({ nome: '', descricao: '', categoria: '', marca: '', estoque_minimo: 0, preco_custo: '', preco_venda: '', ativo: true })
const formAjuste = ref({ quantidade: '', motivo: '' })

// Categorias
const abaAtiva = ref('produtos')
const categorias = ref([])
const loadingCategorias = ref(false)
const modalCategoria = ref(false)
const editandoCategoriaId = ref(null)
const erroCategoria = ref('')
const formCategoria = ref({ nome: '', ativo: true })

const produtosFiltrados = computed(() => {
  const q = busca.value.trim().toLowerCase()
  const cat = filtroCategoria.value.trim().toLowerCase()
  return produtos.value.filter(p => {
    if (apenasAtivos.value && !p.ativo) return false
    if (q && !p.nome.toLowerCase().includes(q) && !(p.marca ?? '').toLowerCase().includes(q)) return false
    if (cat && !(p.categoria ?? '').toLowerCase().includes(cat)) return false
    if (apenasEstoqueBaixo.value && Number(p.estoque_atual) > Number(p.estoque_minimo)) return false
    return true
  })
})

function estoqueClass(p) {
  const atual = Number(p.estoque_atual)
  const min = Number(p.estoque_minimo)
  if (atual <= 0) return 'text-red-600'
  if (min > 0 && atual <= min) return 'text-orange-500'
  return 'text-green-700'
}

async function fetchProdutos() {
  loading.value = true
  try {
    const { data } = await api.get('/produtos/?apenas_ativos=false')
    produtos.value = data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProdutos()
  fetchCategorias()
})

function abrirModalNovo() {
  formNovo.value = { nome: '', descricao: '', categoria: '', marca: '', estoque_atual: 0, estoque_minimo: 0, preco_custo: '', preco_venda: '' }
  erroNovo.value = ''
  modalNovo.value = true
}

function abrirModalEditar(p) {
  editandoId.value = p.id
  formEditar.value = {
    nome: p.nome,
    descricao: p.descricao || '',
    categoria: p.categoria || '',
    marca: p.marca || '',
    estoque_minimo: p.estoque_minimo,
    preco_custo: p.preco_custo != null ? Number(p.preco_custo) : '',
    preco_venda: p.preco_venda != null ? Number(p.preco_venda) : '',
    ativo: p.ativo,
  }
  erroEditar.value = ''
  modalEditar.value = true
}

function abrirAjuste(p) {
  produtoAjuste.value = p
  formAjuste.value = { quantidade: '', motivo: '' }
  erroAjuste.value = ''
  modalAjuste.value = true
}

function confirmarExclusao(p) {
  produtoParaExcluir.value = p
}

async function salvarNovo() {
  salvando.value = true
  erroNovo.value = ''
  try {
    const payload = {
      nome: formNovo.value.nome,
      descricao: formNovo.value.descricao || null,
      categoria: formNovo.value.categoria || null,
      marca: formNovo.value.marca || null,
      estoque_atual: formNovo.value.estoque_atual || 0,
      estoque_minimo: formNovo.value.estoque_minimo || 0,
      preco_custo: formNovo.value.preco_custo !== '' ? formNovo.value.preco_custo : null,
      preco_venda: formNovo.value.preco_venda !== '' ? formNovo.value.preco_venda : null,
    }
    await api.post('/produtos/', payload)
    modalNovo.value = false
    toastSucesso('Produto criado com sucesso!')
    await fetchProdutos()
  } finally {
    salvando.value = false
  }
}

async function salvarEdicao() {
  salvando.value = true
  erroEditar.value = ''
  try {
    const payload = {
      nome: formEditar.value.nome,
      descricao: formEditar.value.descricao || null,
      categoria: formEditar.value.categoria || null,
      marca: formEditar.value.marca || null,
      estoque_minimo: formEditar.value.estoque_minimo,
      preco_custo: formEditar.value.preco_custo !== '' ? formEditar.value.preco_custo : null,
      preco_venda: formEditar.value.preco_venda !== '' ? formEditar.value.preco_venda : null,
      ativo: formEditar.value.ativo,
    }
    await api.patch(`/produtos/${editandoId.value}`, payload)
    modalEditar.value = false
    toastSucesso('Produto atualizado com sucesso!')
    await fetchProdutos()
  } finally {
    salvando.value = false
  }
}

async function salvarAjuste() {
  salvando.value = true
  erroAjuste.value = ''
  try {
    await api.post(`/produtos/${produtoAjuste.value.id}/ajuste`, {
      quantidade: Number(formAjuste.value.quantidade),
      motivo: formAjuste.value.motivo || null,
    })
    modalAjuste.value = false
    toastSucesso('Estoque ajustado com sucesso!')
    await fetchProdutos()
  } finally {
    salvando.value = false
  }
}

async function excluirProduto() {
  salvando.value = true
  try {
    await api.delete(`/produtos/${produtoParaExcluir.value.id}`)
    produtoParaExcluir.value = null
    await fetchProdutos()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir produto.')
  } finally {
    salvando.value = false
  }
}

async function fetchCategorias() {
  loadingCategorias.value = true
  try {
    const { data } = await api.get('/produtos/categorias/')
    categorias.value = data
  } finally {
    loadingCategorias.value = false
  }
}

function abrirModalNovaCategoria() {
  editandoCategoriaId.value = null
  formCategoria.value = { nome: '', ativo: true }
  erroCategoria.value = ''
  modalCategoria.value = true
}

function abrirEditarCategoria(c) {
  editandoCategoriaId.value = c.id
  formCategoria.value = { nome: c.nome, ativo: c.ativo }
  erroCategoria.value = ''
  modalCategoria.value = true
}

async function salvarCategoria() {
  salvando.value = true
  erroCategoria.value = ''
  try {
    if (editandoCategoriaId.value) {
      await api.patch(`/produtos/categorias/${editandoCategoriaId.value}`, formCategoria.value)
    } else {
      await api.post('/produtos/categorias/', { nome: formCategoria.value.nome })
    }
    modalCategoria.value = false
    toastSucesso('Categoria salva com sucesso!')
    await fetchCategorias()
  } catch (e) {
    erroCategoria.value = e.response?.data?.detail || 'Erro ao salvar categoria.'
  } finally {
    salvando.value = false
  }
}

async function excluirCategoria(c) {
  if (!confirm(`Excluir categoria "${c.nome}"?`)) return
  try {
    await api.delete(`/produtos/categorias/${c.id}`)
    await fetchCategorias()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir categoria.')
  }
}
</script>
