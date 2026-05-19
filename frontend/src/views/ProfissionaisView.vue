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

      <!-- Mobile: cards -->
      <div v-else class="sm:hidden divide-y divide-gray-100">
        <div v-for="p in profissionais" :key="p.id" class="p-4 space-y-2">
          <div class="flex items-start justify-between gap-2">
            <div class="min-w-0">
              <p class="font-medium text-gray-800 text-sm">
                {{ p.nome }}
                <span v-if="ehMeuPerfil(p)" class="ml-1.5 text-xs text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded-full font-medium">Você</span>
              </p>
              <div class="flex items-center gap-2 mt-1">
                <span :class="p.ativo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ p.ativo ? 'Ativo' : 'Inativo' }}</span>
                <span v-if="nomeUsuarioVinculado(p.usuario_id)" class="text-xs text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full font-medium">{{ nomeUsuarioVinculado(p.usuario_id) }}</span>
              </div>
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <button @click="abrirDetalhes(p)" class="flex-1 min-w-0 text-xs font-medium text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-lg py-2 px-3">Detalhes</button>
            <template v-if="auth.isAdmin">
              <button @click="abrirModalEditar(p)" class="flex-1 min-w-0 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg py-2 px-3">Editar</button>
              <button @click="abrirModalPrecos(p)" class="flex-1 min-w-0 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg py-2 px-3">Preços</button>
              <button @click="confirmarExclusao(p)" class="text-xs font-medium text-red-500 bg-red-50 hover:bg-red-100 rounded-lg py-2 px-3">Excluir</button>
            </template>
            <button v-else-if="ehMeuPerfil(p)" @click="abrirModalPrecos(p)" class="flex-1 min-w-0 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg py-2 px-3">Meus Preços</button>
          </div>
        </div>
      </div>

      <!-- Desktop: tabela -->
      <table v-if="!loading && profissionais.length" class="hidden sm:table w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Usuário vinculado</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Ativo</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="p in profissionais" :key="p.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-800">
              {{ p.nome }}
              <span v-if="ehMeuPerfil(p)" class="ml-1.5 text-xs text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded-full font-medium">Você</span>
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
            <td class="px-4 py-3 text-right space-x-2">
              <button @click="abrirDetalhes(p)" class="text-xs text-rose-600 hover:underline font-medium">Detalhes</button>
              <template v-if="auth.isAdmin">
                <button @click="abrirModalEditar(p)" class="text-xs text-blue-600 hover:underline">Editar</button>
                <button @click="abrirModalPrecos(p)" class="text-xs text-indigo-600 hover:underline font-medium">Preços</button>
                <button @click="confirmarExclusao(p)" class="text-xs text-red-500 hover:underline">Excluir</button>
              </template>
              <button
                v-else-if="ehMeuPerfil(p)"
                @click="abrirModalPrecos(p)"
                class="text-xs text-indigo-600 hover:underline font-medium"
              >Meus Preços</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Drawer Detalhes do Profissional -->
    <div v-if="drawerDetalhes" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 sm:p-4" @click.self="drawerDetalhes = false">
      <div class="bg-white w-full sm:max-w-3xl sm:rounded-2xl rounded-t-3xl shadow-2xl flex flex-col overflow-hidden max-h-[92vh]">

        <!-- Drag handle (mobile only) -->
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>

        <!-- Cabeçalho -->
        <div class="flex items-start justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div>
            <h3 class="text-lg font-bold text-gray-800">{{ profSelecionado?.nome }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">
              <span :class="profSelecionado?.ativo ? 'text-green-600' : 'text-gray-400'" class="font-medium">
                {{ profSelecionado?.ativo ? 'Ativo' : 'Inativo' }}
              </span>
              <span v-if="nomeUsuarioVinculado(profSelecionado?.usuario_id)" class="ml-2 text-indigo-600">
                · {{ nomeUsuarioVinculado(profSelecionado?.usuario_id) }}
              </span>
            </p>
          </div>
          <button @click="drawerDetalhes = false" class="w-10 h-10 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Tabs (mobile only) -->
        <div class="sm:hidden flex border-b border-gray-100 flex-shrink-0">
          <button
            @click="drawerTab = 'contato'"
            :class="drawerTab === 'contato' ? 'border-b-2 border-rose-600 text-rose-700 font-semibold' : 'text-gray-500'"
            class="flex-1 py-3 text-sm transition-colors"
          >Contato</button>
          <button
            @click="drawerTab = 'servicos'"
            :class="drawerTab === 'servicos' ? 'border-b-2 border-rose-600 text-rose-700 font-semibold' : 'text-gray-500'"
            class="flex-1 py-3 text-sm transition-colors"
          >Serviços</button>
        </div>

        <!-- Corpo: dois painéis -->
        <div class="flex flex-1 overflow-hidden">

          <!-- Esquerda: contato + pix (somente leitura) -->
          <div :class="['sm:w-72 w-full flex-shrink-0 overflow-y-auto border-r border-gray-100 p-5 space-y-5', drawerTab !== 'contato' ? 'hidden sm:block' : '']">
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Telefone</p>
              <p v-if="profSelecionado?.telefone" class="text-sm text-gray-800">
                <span class="text-gray-400 mr-1">+55</span>{{ profSelecionado.telefone }}
              </p>
              <p v-else class="text-sm text-gray-400 italic">Não informado</p>
            </div>
            <div>
              <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Chave PIX</p>
              <p v-if="profSelecionado?.chave_pix" class="text-sm text-gray-800 break-all">{{ profSelecionado.chave_pix }}</p>
              <p v-else class="text-sm text-gray-400 italic">Não informada</p>
            </div>
            <button type="button" class="w-full border border-gray-200 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50" @click="drawerDetalhes = false">Fechar</button>
          </div>

          <!-- Direita: serviços e preços -->
          <div :class="['flex-1 overflow-y-auto p-5', drawerTab !== 'servicos' ? 'hidden sm:block' : '']">
            <h4 class="text-sm font-semibold text-gray-700 mb-4">Serviços habilitados</h4>

            <div v-if="!profSelecionado?.servicos?.length" class="text-sm text-gray-400 italic">Nenhum serviço habilitado.</div>

            <div
              v-for="s in profSelecionado?.servicos"
              :key="s.id"
              class="mb-3 bg-gray-50 rounded-xl p-3.5 border border-gray-100 flex items-center justify-between gap-3"
            >
              <div class="min-w-0">
                <p class="text-sm font-semibold text-gray-800">{{ s.nome }}</p>
                <p class="text-xs text-gray-400 mt-0.5">{{ s.duracao_minutos }} min</p>
              </div>
              <div class="text-right flex-shrink-0">
                <p class="text-sm font-semibold" :class="s.preco_proprio != null ? 'text-rose-600' : 'text-gray-700'">
                  R$ {{ Number(s.preco_proprio ?? s.preco).toFixed(2) }}
                </p>
                <p v-if="s.preco_proprio != null" class="text-xs text-gray-400 line-through">
                  R$ {{ Number(s.preco).toFixed(2) }}
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Modal Novo Profissional -->
    <div v-if="modalAberto" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4" @click.self="fecharModal">
      <div class="bg-white w-full sm:max-w-sm sm:rounded-xl rounded-t-3xl shadow-xl max-h-[90vh] flex flex-col overflow-hidden">
        <!-- Drag handle mobile -->
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>
        <div class="flex-1 overflow-y-auto px-6 pt-5 pb-2">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">Novo Profissional</h3>
          <form id="form-novo-prof" @submit.prevent="salvar" class="space-y-4">
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
          </form>
        </div>
        <div class="flex gap-2 px-6 py-4 border-t border-gray-100 flex-shrink-0">
          <button type="button" @click="fecharModal" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button type="submit" form="form-novo-prof" :disabled="salvando" class="flex-1 bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Editar Profissional (admin only) -->
    <div v-if="modalEditar" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm max-h-[90vh] flex flex-col overflow-hidden">
        <div class="flex items-center justify-between px-6 pt-5 pb-4 border-b border-gray-100 flex-shrink-0">
          <h3 class="text-lg font-semibold text-gray-800">Editar Profissional</h3>
          <button type="button" @click="modalEditar = false" class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400">✕</button>
        </div>
        <form id="form-editar-prof" @submit.prevent="salvarEdicao" class="flex-1 overflow-y-auto px-6 py-4 space-y-4">
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
            <label class="block text-sm font-medium text-gray-700 mb-2">Serviços habilitados</label>
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
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
            <div class="flex items-center border border-gray-300 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-rose-400">
              <span class="px-3 py-2 bg-gray-50 text-sm text-gray-500 border-r border-gray-300 select-none whitespace-nowrap">+55</span>
              <input v-model="formEditar.telefone" class="flex-1 px-3 py-2 text-sm focus:outline-none" placeholder="(11) 99999-9999" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Chave PIX</label>
            <input v-model="formEditar.chave_pix" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" placeholder="CPF, e-mail, telefone ou chave aleatória" />
          </div>
          <p v-if="erroEditar" class="text-sm text-red-600">{{ erroEditar }}</p>
        </form>
        <div class="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 flex-shrink-0">
          <button type="button" @click="modalEditar = false" class="text-sm text-gray-500 hover:text-gray-700 px-4 py-2">Cancelar</button>
          <button type="submit" form="form-editar-prof" :disabled="salvando" class="bg-rose-600 hover:bg-rose-700 text-white text-sm font-medium px-5 py-2 rounded-lg disabled:opacity-60">
            {{ salvando ? 'Salvando...' : 'Salvar' }}
          </button>
        </div>
      </div>
    </div>

    <!--
      MODAL DE PREÇOS POR SERVIÇO
      Acessível por:
        - Admin: para qualquer profissional via botão "Preços"
        - Profissional: para si mesmo via "Meus Preços"

      LÓGICA DE PREÇO:
        O campo mostra o preco_proprio atual (se houver) ou fica vazio (placeholder = preço padrão).
        Se o usuário deixar vazio e salvar, envia null → volta para o preço padrão do serviço.
        Se preencher, envia o valor numérico → sobrescreve para este profissional especificamente.

      Desta forma, um mesmo serviço (ex: "Corte Masculino R$ 40,00") pode custar
      R$ 45,00 com o Profissional A e R$ 35,00 com o Profissional B, sem alterar
      o preço padrão do catálogo.
    -->
    <div v-if="modalPrecos" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] flex flex-col overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div>
            <h3 class="text-lg font-semibold text-gray-800">Preços de {{ editandoPrecosNome }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">Deixe vazio para usar o preço padrão do serviço</p>
          </div>
          <button @click="modalPrecos = false" class="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-400">✕</button>
        </div>
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <div v-if="!formPrecos.length" class="text-sm text-gray-400 italic py-4 text-center">
            Este profissional não tem serviços habilitados.
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="s in formPrecos"
              :key="s.servico_id"
              class="flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-3 border border-gray-100"
            >
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800">{{ s.nome }}</p>
                <p class="text-xs text-gray-400 mt-0.5">Padrão: R$ {{ Number(s.preco_padrao).toFixed(2) }}</p>
              </div>
              <div class="relative flex-shrink-0">
                <span class="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 font-medium select-none">R$</span>
                <input
                  v-model="s.preco_proprio"
                  type="number"
                  step="0.01"
                  min="0"
                  :placeholder="Number(s.preco_padrao).toFixed(2)"
                  class="w-28 border border-gray-200 rounded-lg pl-8 pr-2 py-2 text-sm text-right focus:outline-none focus:ring-2 focus:ring-indigo-400"
                />
              </div>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex-shrink-0 flex gap-2">
          <button type="button" @click="modalPrecos = false" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button
            :disabled="salvandoPrecos || !formPrecos.length"
            @click="salvarPrecos"
            class="flex-1 bg-indigo-600 text-white rounded-lg py-2.5 text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50"
          >
            {{ salvandoPrecos ? 'Salvando...' : 'Salvar preços' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Confirmar Exclusão -->
    <div v-if="profissionalParaExcluir" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4">
      <div class="bg-white w-full sm:max-w-xs sm:rounded-xl rounded-t-3xl shadow-xl p-6 text-center">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mb-4"></div>
        <p class="text-sm text-gray-700 mb-1">Excluir profissional</p>
        <p class="font-semibold text-gray-900 mb-6">{{ profissionalParaExcluir.nome }}</p>
        <div class="flex gap-2">
          <button @click="profissionalParaExcluir = null" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button @click="excluirProfissional" :disabled="salvando" class="flex-1 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
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
const profissionais = ref([])
const usuariosProfissionais = ref([])
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
const formEditar = ref({ nome: '', ativo: true, servico_ids: [], usuario_id: null, telefone: '', chave_pix: '' })

// ─── Preços por profissional ───────────────────────────────────────────────
const modalPrecos = ref(false)
const editandoPrecosProfId = ref(null)
const editandoPrecosNome = ref('')
const formPrecos = ref([]) // [{servico_id, nome, preco_padrao, preco_proprio}]
const salvandoPrecos = ref(false)

// ─── Drawer Detalhes ──────────────────────────────────────────────────────
const drawerDetalhes = ref(false)
const drawerTab = ref('contato')
const profSelecionado = ref(null)

function abrirDetalhes(p) {
  profSelecionado.value = p
  drawerTab.value = 'contato'
  drawerDetalhes.value = true
}

/**
 * Retorna true se o profissional `p` corresponde ao usuário logado.
 * Usado para mostrar o botão "Meus Preços" para o profissional logado.
 */
function ehMeuPerfil(p) {
  return p.usuario_id != null && p.usuario_id === auth.user?.id
}

function abrirModalPrecos(p) {
  editandoPrecosProfId.value = p.id
  editandoPrecosNome.value = p.nome
  formPrecos.value = (p.servicos || []).map(s => ({
    servico_id: s.id,
    nome: s.nome,
    preco_padrao: s.preco,
    // preco_proprio: string no input (vazio = null ao salvar)
    preco_proprio: s.preco_proprio != null ? String(s.preco_proprio) : '',
  }))
  modalPrecos.value = true
}

async function salvarPrecos() {
  salvandoPrecos.value = true
  try {
    await Promise.all(
      formPrecos.value.map(s =>
        api.patch(
          `/profissionais/${editandoPrecosProfId.value}/servicos/${s.servico_id}/preco`,
          {
            // Vazio ou só espaços → null (volta ao preço padrão do catálogo)
            preco_proprio: s.preco_proprio.trim() !== '' ? parseFloat(s.preco_proprio) : null,
          }
        )
      )
    )
    modalPrecos.value = false
    toastSucesso('Preços salvos com sucesso!')
    await fetchProfissionais()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar preços.')
  } finally {
    salvandoPrecos.value = false
  }
}

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
  formEditar.value = { nome: p.nome, ativo: p.ativo, servico_ids: [...idsAtuais], usuario_id: p.usuario_id ?? null, telefone: p.telefone || '', chave_pix: p.chave_pix || '' }
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
    toastSucesso('Profissional criado com sucesso!')
    await fetchProfissionais()
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
      telefone: formEditar.value.telefone || null,
      chave_pix: formEditar.value.chave_pix || null,
    })
    const originais = new Set(editandoServicosOriginais.value)
    const novos = new Set(formEditar.value.servico_ids)
    const adicionar = [...novos].filter(id => !originais.has(id))
    const remover = [...originais].filter(id => !novos.has(id))
    await Promise.all([
      ...adicionar.map(sid => api.post(`/profissionais/${editandoId.value}/servicos/${sid}`)),
      ...remover.map(sid => api.delete(`/profissionais/${editandoId.value}/servicos/${sid}`)),
    ])
    modalEditar.value = false
    toastSucesso('Profissional atualizado com sucesso!')
    await fetchProfissionais()
    // Se o drawer estava aberto para este profissional, atualiza o objeto exibido
    if (profSelecionado.value?.id === editandoId.value) {
      profSelecionado.value = profissionais.value.find(p => p.id === editandoId.value) ?? profSelecionado.value
    }
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
