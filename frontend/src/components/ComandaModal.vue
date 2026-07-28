<template>
  <Teleport to="body">
    <div v-if="modelValue" class="fixed inset-0 bg-black/50 flex items-center justify-center z-[60] p-3 sm:p-6">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[92vh] flex flex-col">

        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-100 flex items-start justify-between gap-4 shrink-0">
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-bold text-gray-800">
                Comanda <span class="text-rose-600">#{{ String(modelValue.id).padStart(4, '0') }}</span>
              </h3>
              <span :class="['text-xs font-semibold px-2.5 py-0.5 rounded-full', statusComandaClass]">
                {{ modelValue.status === 'aberta' ? 'Aberta' : modelValue.status === 'fechada' ? 'Fechada' : 'Cancelada' }}
              </span>
            </div>
            <p class="text-xs text-gray-400 mt-0.5">Aberta {{ formatDate(modelValue.aberta_em) }}</p>
          </div>
          <button @click="$emit('update:modelValue', null)" class="text-gray-400 hover:text-gray-600 p-1 mt-0.5 shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Corpo scrollável -->
        <div class="flex-1 overflow-y-auto px-6 py-5 space-y-6">

          <!-- ── ITENS ──────────────────────────────────────────── -->
          <section>
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider">Itens</h4>
              <div v-if="modelValue.status === 'aberta'" class="flex gap-2">
                <button
                  @click="togglePainel('ag')"
                  :class="btnPainelClass(painelAtivo === 'ag')"
                >+ Agendamento</button>
                <button
                  @click="togglePainel('avulso')"
                  :class="btnPainelClass(painelAtivo === 'avulso')"
                >+ Avulso</button>
              </div>
            </div>

            <!-- Loading inicial de itens (após criar comanda mas antes de adicionar itens) -->
            <div v-if="modelValue._carregando" class="flex items-center gap-2 text-sm text-gray-400 py-4 justify-center">
              <svg class="animate-spin w-4 h-4 text-rose-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              Carregando itens...
            </div>

            <!-- Lista de itens -->
            <div v-else-if="modelValue.itens.length === 0 && !painelAtivo" class="text-sm text-gray-400 italic text-center py-4">
              Nenhum item ainda. Use os botões acima para adicionar.
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="item in modelValue.itens"
                :key="item.id"
                class="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2.5 gap-3"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-800 truncate">
                    {{ item.servico?.nome || item.descricao }}
                    <span v-if="item.tipo !== 'agendamento'" class="ml-1 text-xs text-gray-400 font-normal italic">
                      {{ item.tipo === 'produto' ? '(produto)' : '(avulso)' }}
                    </span>
                  </p>
                  <p class="text-xs text-gray-400 truncate">
                    {{ item.cliente?.nome }}
                    <span v-if="item.profissional"> · {{ item.profissional.nome }}</span>
                    <span v-if="item.quantidade > 1"> · {{ item.quantidade }}×</span>
                    <span v-if="Number(item.desconto) > 0"> · -R${{ fmt(item.desconto) }}</span>
                  </p>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <span class="text-sm font-semibold text-gray-700">R$ {{ subtotalItem(item) }}</span>
                  <button
                    v-if="modelValue.status === 'aberta'"
                    @click="removerItem(item.id)"
                    class="text-gray-300 hover:text-red-500 transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Painel: adicionar agendamento -->
            <div v-if="painelAtivo === 'ag'" class="mt-3 border border-dashed border-rose-200 rounded-xl p-4 bg-rose-50/30">
              <p class="text-xs font-semibold text-rose-700 mb-2">Vincular agendamento à comanda</p>
              <input
                v-model="buscaAg"
                type="text"
                placeholder="Buscar por nome do cliente..."
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-rose-300"
              />
              <div class="space-y-1.5 max-h-44 overflow-y-auto">
                <div v-if="agendamentosDisponiveis.length === 0" class="text-xs text-gray-400 text-center py-2 italic">
                  Nenhum agendamento disponível para adicionar.
                </div>
                <div
                  v-for="ag in agendamentosDisponiveis"
                  :key="ag.id"
                  class="flex items-center justify-between bg-white rounded-lg px-3 py-2 border border-gray-200 cursor-pointer hover:border-rose-300 hover:bg-rose-50 transition-colors"
                  @click="adicionarAgendamento(ag)"
                >
                  <div>
                    <p class="text-sm font-medium text-gray-800">{{ ag.cliente?.nome }}</p>
                    <p class="text-xs text-gray-400">{{ ag.itens?.map(i => i.servico?.nome).join(', ') }} · R$ {{ totalAgendamento(ag) }}</p>
                  </div>
                  <span class="text-xs text-rose-600 font-semibold shrink-0 ml-2">+ Adicionar</span>
                </div>
              </div>
            </div>

            <!-- Painel: item avulso -->
            <div v-if="painelAtivo === 'avulso'" class="mt-3 border border-dashed border-gray-200 rounded-xl p-4">
              <p class="text-xs font-semibold text-gray-600 mb-3">Adicionar item avulso</p>

              <!-- Tabs de modo -->
              <div class="flex gap-1 bg-gray-100 rounded-lg p-1 mb-4">
                <button
                  v-for="m in modos"
                  :key="m.value"
                  @click="modoAvulso = m.value; resetAvulso()"
                  :class="['flex-1 text-xs font-semibold py-1.5 rounded-md transition-colors', modoAvulso === m.value ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700']"
                >{{ m.label }}</button>
              </div>

              <div v-if="loadingCatalog" class="text-xs text-gray-400 text-center py-4">Carregando catálogo...</div>
              <div v-else class="space-y-3">

                <!-- Modo: Serviço do catálogo -->
                <template v-if="modoAvulso === 'servico'">
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Serviço *</label>
                    <select v-model="formAvulso.servico_id" @change="onServicoChange" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300">
                      <option value="">Selecione um serviço...</option>
                      <option v-for="s in servicos" :key="s.id" :value="s.id">
                        {{ s.nome }} — R$ {{ Number(s.preco).toFixed(2) }}
                      </option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Profissional *</label>
                    <select v-model="formAvulso.profissional_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300">
                      <option value="">Selecione o profissional...</option>
                      <option v-for="p in profissionais" :key="p.id" :value="p.id">{{ p.nome }}</option>
                    </select>
                  </div>
                </template>

                <!-- Modo: Produto do estoque -->
                <template v-else-if="modoAvulso === 'produto'">
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Produto *</label>
                    <select v-model="formAvulso.produto_id" @change="onProdutoChange" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300">
                      <option value="">Selecione um produto...</option>
                      <option v-for="p in produtos" :key="p.id" :value="p.id">
                        {{ p.nome }}{{ p.marca ? ` (${p.marca})` : '' }} — R$ {{ Number(p.preco_venda || 0).toFixed(2) }}
                      </option>
                    </select>
                  </div>
                </template>

                <!-- Modo: Manual (texto livre) -->
                <template v-else>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Descrição *</label>
                    <input
                      v-model="formAvulso.descricao"
                      type="text"
                      placeholder="Ex: Hidratação capilar, Taxa de visita..."
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300"
                    />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">Profissional (opcional)</label>
                    <select v-model="formAvulso.profissional_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300">
                      <option value="">Nenhum</option>
                      <option v-for="p in profissionais" :key="p.id" :value="p.id">{{ p.nome }}</option>
                    </select>
                  </div>
                </template>

                <!-- Campos comuns -->
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Para o cliente *</label>
                  <select v-model="formAvulso.cliente_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300">
                    <option value="">Selecione o cliente...</option>
                    <option v-for="c in clientesDaComanda" :key="c.id" :value="c.id">{{ c.nome }}</option>
                  </select>
                </div>

                <div class="flex gap-3">
                  <div class="flex-1">
                    <label class="block text-xs text-gray-500 mb-1">Valor (R$) *</label>
                    <input v-model="formAvulso.valor_unitario" type="number" step="0.01" min="0.01"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300" />
                  </div>
                  <div class="w-20">
                    <label class="block text-xs text-gray-500 mb-1">Qtd</label>
                    <input v-model="formAvulso.quantidade" type="number" min="1"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300" />
                  </div>
                  <div class="flex-1">
                    <label class="block text-xs text-gray-500 mb-1">Desconto</label>
                    <input v-model="formAvulso.desconto" type="number" step="0.01" min="0"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300" />
                  </div>
                </div>

                <p v-if="erroAvulso" class="text-xs text-red-600">{{ erroAvulso }}</p>

                <button
                  @click="confirmarItemAvulso"
                  :disabled="salvandoAvulso"
                  class="w-full bg-gray-800 hover:bg-gray-900 text-white text-sm font-semibold py-2 rounded-lg disabled:opacity-50 transition-colors"
                >{{ salvandoAvulso ? 'Adicionando...' : 'Adicionar item' }}</button>
              </div>
            </div>
          </section>

          <!-- ── RESUMO FINANCEIRO ──────────────────────────────── -->
          <section class="bg-gray-50 rounded-xl p-4 space-y-1.5">
            <div class="flex justify-between text-sm text-gray-600">
              <span>Total dos itens</span>
              <span class="font-semibold">R$ {{ fmt(modelValue.total_itens) }}</span>
            </div>
            <div v-if="Number(modelValue.total_pago) > 0" class="flex justify-between text-sm text-green-700">
              <span>Já pago</span>
              <span class="font-semibold">- R$ {{ fmt(modelValue.total_pago) }}</span>
            </div>
            <div class="flex justify-between text-base font-bold border-t border-gray-200 pt-2 mt-1"
                 :class="Number(modelValue.saldo_restante) > 0 ? 'text-gray-800' : 'text-green-700'">
              <span>{{ Number(modelValue.saldo_restante) > 0 ? 'Restante' : 'Saldo quitado ✓' }}</span>
              <span>R$ {{ fmt(modelValue.saldo_restante) }}</span>
            </div>
          </section>

          <!-- ── PAGAMENTOS REGISTRADOS ─────────────────────────── -->
          <section v-if="modelValue.pagamentos?.length > 0">
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Pagamentos registrados</h4>
            <div class="space-y-2">
              <div
                v-for="p in modelValue.pagamentos"
                :key="p.id"
                class="flex items-center justify-between bg-green-50 rounded-lg px-3 py-2 text-sm"
              >
                <div>
                  <span class="font-semibold text-green-800">R$ {{ fmt(p.valor) }}</span>
                  <span class="text-green-600 ml-2">{{ metodoPagLabel(p.metodo) }}</span>
                  <span v-if="Number(p.credito_utilizado) > 0" class="ml-2 text-xs text-indigo-600">
                    (crédito: R$ {{ fmt(p.credito_utilizado) }})
                  </span>
                </div>
                <span class="text-xs text-gray-400">{{ formatDate(p.pago_em) }}</span>
              </div>
            </div>
          </section>

          <!-- ── FORMULÁRIO DE PAGAMENTO ────────────────────────── -->
          <section v-if="modelValue.status === 'aberta' && modelValue.itens?.length > 0 && !modelValue._carregando">
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
              {{ modelValue.pagamentos?.length ? 'Adicionar pagamento (split)' : 'Registrar pagamento' }}
            </h4>
            <div class="space-y-3">
              <!-- Crédito disponível -->
              <div v-if="creditoDisponivel > 0" class="bg-indigo-50 border border-indigo-100 rounded-lg p-3">
                <label class="text-sm font-semibold text-indigo-800 block mb-2">
                  Usar crédito (saldo: R$ {{ fmt(creditoDisponivel) }})
                </label>
                <input v-model="formPag.credito_utilizado" type="number" step="0.01" min="0" :max="creditoDisponivel"
                  class="w-full border border-indigo-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white"
                  placeholder="0.00"/>
              </div>

              <div class="flex gap-3">
                <div class="flex-1">
                  <label class="block text-xs text-gray-500 mb-1">Valor (R$) *</label>
                  <input v-model="formPag.valor" type="number" step="0.01" min="0.01"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"/>
                </div>
                <div class="flex-1">
                  <label class="block text-xs text-gray-500 mb-1">Método *</label>
                  <select v-model="formPag.metodo" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400">
                    <option value="">Selecione...</option>
                    <option value="dinheiro">Dinheiro</option>
                    <option value="pix">PIX</option>
                    <option value="cartao_credito">Cartão de Crédito</option>
                    <option value="cartao_debito">Cartão de Débito</option>
                  </select>
                </div>
              </div>

              <!-- Quem paga (apenas quando há múltiplos clientes) -->
              <div v-if="clientesDaComanda.length > 1">
                <label class="block text-xs text-gray-500 mb-1">Quem está pagando</label>
                <select v-model="formPag.pagador_cliente_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400">
                  <option :value="null">{{ clientesDaComanda[0]?.nome }} (principal)</option>
                  <option v-for="c in clientesDaComanda" :key="c.id" :value="c.id">{{ c.nome }}</option>
                </select>
              </div>

              <!-- Troco vira crédito -->
              <div v-if="trocoPreview > 0" class="bg-green-50 text-green-800 px-3 py-2 rounded-lg text-xs font-semibold">
                R$ {{ trocoPreview.toFixed(2) }} será adicionado como crédito ao cliente.
              </div>

              <!-- Atalho: valor exato -->
              <button v-if="Number(modelValue.saldo_restante) > 0" type="button"
                @click="formPag.valor = fmt(modelValue.saldo_restante)"
                class="text-xs text-rose-600 hover:underline">
                Usar valor exato restante (R$ {{ fmt(modelValue.saldo_restante) }})
              </button>

              <p v-if="erroPag" class="text-sm text-red-600">{{ erroPag }}</p>

              <button @click="registrarPagamento" :disabled="salvandoPag"
                class="w-full bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-2.5 rounded-lg disabled:opacity-50 transition-colors">
                {{ salvandoPag ? 'Registrando...' : 'Registrar pagamento' }}
              </button>
            </div>
          </section>

          <p v-if="erroComanda" class="text-sm text-red-600 text-center bg-red-50 rounded-lg px-3 py-2">{{ erroComanda }}</p>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 border-t border-gray-100 flex gap-3 shrink-0">
          <template v-if="modelValue.status === 'aberta'">
            <button @click="cancelarComanda" :disabled="salvandoFechar"
              class="border border-gray-300 text-gray-600 rounded-lg px-4 py-2 text-sm hover:bg-gray-50 disabled:opacity-50 transition-colors">
              Cancelar comanda
            </button>
            <button @click="fecharComanda"
              :disabled="salvandoFechar || Number(modelValue.saldo_restante) > 0 || !modelValue.itens?.length || modelValue._carregando"
              class="flex-1 bg-rose-600 hover:bg-rose-700 text-white rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-50 transition-colors"
              :title="Number(modelValue.saldo_restante) > 0 ? 'Quitar saldo antes de fechar' : ''">
              {{ salvandoFechar ? 'Fechando...' : Number(modelValue.saldo_restante) > 0 ? `Falta R$ ${fmt(modelValue.saldo_restante)}` : 'Fechar comanda ✓' }}
            </button>
          </template>
          <button v-else @click="$emit('update:modelValue', null)"
            class="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 text-sm font-semibold">
            Fechar
          </button>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import api from '@/api/client'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  /** Objeto da comanda (null = modal fechado). Suporta v-model. */
  modelValue: { type: Object, default: null },
  /** Lista de agendamentos do intervalo atual (para o painel "+ Agendamento"). */
  agendamentos: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'fechada', 'cancelada'])

const { sucesso: toastSucesso } = useToast()

// ── Painéis ───────────────────────────────────────────────────────────────────
const painelAtivo = ref(null) // 'ag' | 'avulso' | null
const buscaAg = ref('')

function togglePainel(nome) {
  painelAtivo.value = painelAtivo.value === nome ? null : nome
}

function btnPainelClass(ativo) {
  return [
    'text-xs px-2.5 py-1 rounded-md font-medium border transition-colors',
    ativo
      ? 'bg-rose-600 text-white border-rose-600'
      : 'border-gray-300 text-gray-600 hover:bg-gray-50',
  ]
}

// ── Catálogo (carregado lazily quando avulso é aberto) ────────────────────────
const modos = [
  { value: 'servico', label: 'Serviço' },
  { value: 'produto', label: 'Produto' },
  { value: 'manual', label: 'Manual' },
]
const modoAvulso = ref('servico')
const servicos = ref([])
const profissionais = ref([])
const produtos = ref([])
const loadingCatalog = ref(false)

watch(painelAtivo, async (val) => {
  if (val !== 'avulso') return
  if (servicos.value.length && profissionais.value.length) return
  loadingCatalog.value = true
  try {
    const [sRes, pRes] = await Promise.all([
      api.get('/servicos/'),
      api.get('/profissionais/'),
    ])
    servicos.value = (sRes.data || []).filter(s => s.ativo)
    profissionais.value = (pRes.data || []).filter(p => p.ativo)
  } finally {
    loadingCatalog.value = false
  }
})

watch(modoAvulso, async (modo) => {
  if (modo !== 'produto' || produtos.value.length) return
  try {
    const { data } = await api.get('/produtos/')
    produtos.value = (data || []).filter(p => p.ativo)
  } catch { /* produtos opcionais */ }
})

// ── Formulário avulso ─────────────────────────────────────────────────────────
const formAvulso = ref({
  servico_id: '', profissional_id: '', produto_id: '',
  descricao: '', cliente_id: '',
  valor_unitario: '', quantidade: 1, desconto: '0.00',
})
const salvandoAvulso = ref(false)
const erroAvulso = ref('')

function resetAvulso() {
  formAvulso.value = {
    servico_id: '', profissional_id: '', produto_id: '',
    descricao: '', cliente_id: formAvulso.value.cliente_id,
    valor_unitario: '', quantidade: 1, desconto: '0.00',
  }
  erroAvulso.value = ''
}

function onServicoChange() {
  const s = servicos.value.find(s => s.id == formAvulso.value.servico_id)
  if (s) formAvulso.value.valor_unitario = Number(s.preco).toFixed(2)
}

function onProdutoChange() {
  const p = produtos.value.find(p => p.id == formAvulso.value.produto_id)
  if (p) {
    formAvulso.value.valor_unitario = Number(p.preco_venda || 0).toFixed(2)
    formAvulso.value.descricao = p.nome
  }
}

// ── Formulário de pagamento ───────────────────────────────────────────────────
const formPag = ref({ valor: '', metodo: '', credito_utilizado: '0.00', pagador_cliente_id: null })
const salvandoPag = ref(false)
const erroPag = ref('')

// ── Fechar / Cancelar ─────────────────────────────────────────────────────────
const salvandoFechar = ref(false)
const erroComanda = ref('')

// ── Reset quando modal fecha ──────────────────────────────────────────────────
watch(() => props.modelValue, (val) => {
  if (val) return
  painelAtivo.value = null
  buscaAg.value = ''
  modoAvulso.value = 'servico'
  formPag.value = { valor: '', metodo: '', credito_utilizado: '0.00', pagador_cliente_id: null }
  formAvulso.value = { servico_id: '', profissional_id: '', produto_id: '', descricao: '', cliente_id: '', valor_unitario: '', quantidade: 1, desconto: '0.00' }
  erroPag.value = ''
  erroAvulso.value = ''
  erroComanda.value = ''
})

// ── Computed ──────────────────────────────────────────────────────────────────

const statusComandaClass = computed(() => ({
  aberta:    'bg-green-100 text-green-700',
  fechada:   'bg-blue-100 text-blue-700',
  cancelada: 'bg-gray-100 text-gray-500',
}[props.modelValue?.status] ?? ''))

const clientesDaComanda = computed(() => {
  const mapa = new Map()
  for (const item of props.modelValue?.itens ?? []) {
    if (item.cliente && !mapa.has(item.cliente.id)) mapa.set(item.cliente.id, item.cliente)
  }
  return [...mapa.values()]
})

const creditoDisponivel = computed(() =>
  Number(clientesDaComanda.value[0]?.saldo_credito || 0)
)

const agIdsNaComanda = computed(() =>
  new Set((props.modelValue?.itens ?? []).filter(i => i.agendamento_id).map(i => i.agendamento_id))
)

const agendamentosDisponiveis = computed(() => {
  const busca = buscaAg.value.toLowerCase()
  return props.agendamentos.filter(ag => {
    if (ag.status === 'cancelado' || ag.status === 'pre_agendamento') return false
    if (agIdsNaComanda.value.has(ag.id)) return false
    if (busca && !ag.cliente?.nome?.toLowerCase().includes(busca)) return false
    return true
  })
})

const trocoPreview = computed(() => {
  if (formPag.value.metodo !== 'dinheiro') return 0
  const saldo = Number(props.modelValue?.saldo_restante ?? 0)
  const cred = Number(formPag.value.credito_utilizado || 0)
  const devido = Math.max(0, saldo - cred)
  return Math.max(0, Number(formPag.value.valor || 0) - devido)
})

// ── Helpers API ───────────────────────────────────────────────────────────────

async function recarregar() {
  const { data } = await api.get(`/comandas/${props.modelValue.id}`)
  emit('update:modelValue', data)
}

// ── Operações de itens ────────────────────────────────────────────────────────

async function adicionarAgendamento(ag) {
  erroComanda.value = ''
  try {
    await api.post(`/comandas/${props.modelValue.id}/itens/agendamento`, {
      agendamento_id: ag.id,
      cliente_id: ag.cliente_id,
    })
    await recarregar()
    buscaAg.value = ''
    painelAtivo.value = null
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao adicionar agendamento.'
  }
}

async function removerItem(itemId) {
  erroComanda.value = ''
  try {
    await api.delete(`/comandas/${props.modelValue.id}/itens/${itemId}`)
    await recarregar()
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao remover item.'
  }
}

async function confirmarItemAvulso() {
  erroAvulso.value = ''
  const f = formAvulso.value

  if (!f.cliente_id) { erroAvulso.value = 'Selecione o cliente.'; return }
  if (!f.valor_unitario || Number(f.valor_unitario) <= 0) { erroAvulso.value = 'Informe o valor.'; return }

  let body = {
    tipo: modoAvulso.value === 'produto' ? 'produto' : 'servico_avulso',
    cliente_id: Number(f.cliente_id),
    profissional_id: f.profissional_id ? Number(f.profissional_id) : null,
    valor_unitario: Number(f.valor_unitario),
    quantidade: Number(f.quantidade) || 1,
    desconto: Number(f.desconto) || 0,
  }

  if (modoAvulso.value === 'servico') {
    if (!f.servico_id) { erroAvulso.value = 'Selecione o serviço.'; return }
    if (!f.profissional_id) { erroAvulso.value = 'Selecione o profissional.'; return }
    body.servico_id = Number(f.servico_id)
    body.descricao = null
  } else if (modoAvulso.value === 'produto') {
    if (!f.produto_id) { erroAvulso.value = 'Selecione o produto.'; return }
    const prod = produtos.value.find(p => p.id == f.produto_id)
    body.servico_id = null
    body.descricao = prod?.nome || 'Produto'
  } else {
    if (!f.descricao?.trim()) { erroAvulso.value = 'Informe a descrição.'; return }
    body.servico_id = null
    body.descricao = f.descricao.trim()
  }

  salvandoAvulso.value = true
  try {
    await api.post(`/comandas/${props.modelValue.id}/itens/avulso`, body)
    await recarregar()
    resetAvulso()
    painelAtivo.value = null
  } catch (e) {
    erroAvulso.value = e.response?.data?.detail || 'Erro ao adicionar item.'
  } finally {
    salvandoAvulso.value = false
  }
}

// ── Pagamento ─────────────────────────────────────────────────────────────────

async function registrarPagamento() {
  erroPag.value = ''
  if (!formPag.value.valor || Number(formPag.value.valor) <= 0) { erroPag.value = 'Informe o valor.'; return }
  if (!formPag.value.metodo) { erroPag.value = 'Selecione o método.'; return }

  salvandoPag.value = true
  try {
    await api.post(`/comandas/${props.modelValue.id}/pagamentos`, {
      valor: Number(formPag.value.valor),
      metodo: formPag.value.metodo,
      credito_utilizado: Number(formPag.value.credito_utilizado) || 0,
      pagador_cliente_id: formPag.value.pagador_cliente_id || null,
    })
    await recarregar()
    formPag.value = { valor: '', metodo: '', credito_utilizado: '0.00', pagador_cliente_id: null }
  } catch (e) {
    erroPag.value = e.response?.data?.detail || 'Erro ao registrar pagamento.'
  } finally {
    salvandoPag.value = false
  }
}

// ── Fechar / Cancelar ─────────────────────────────────────────────────────────

async function fecharComanda() {
  salvandoFechar.value = true
  erroComanda.value = ''
  try {
    await api.post(`/comandas/${props.modelValue.id}/fechar`)
    await recarregar()
    toastSucesso('Comanda fechada com sucesso!')
    emit('fechada')
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao fechar comanda.'
  } finally {
    salvandoFechar.value = false
  }
}

async function cancelarComanda() {
  if (!confirm('Cancelar a comanda? Os pagamentos registrados serão estornados.')) return
  salvandoFechar.value = true
  erroComanda.value = ''
  try {
    await api.post(`/comandas/${props.modelValue.id}/cancelar`)
    toastSucesso('Comanda cancelada.')
    emit('cancelada')
    emit('update:modelValue', null)  // Fecha o modal automaticamente
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao cancelar comanda.'
  } finally {
    salvandoFechar.value = false
  }
}

// ── Utilitários ───────────────────────────────────────────────────────────────

function subtotalItem(item) {
  return (Number(item.valor_unitario) * Number(item.quantidade) - Number(item.desconto)).toFixed(2)
}

function fmt(v) { return Number(v || 0).toFixed(2) }

function totalAgendamento(ag) {
  return (ag?.itens ?? []).reduce((s, i) => s + Number(i.servico?.preco || 0), 0).toFixed(2)
}

function metodoPagLabel(m) {
  return { dinheiro: 'Dinheiro', pix: 'PIX', cartao_credito: 'Cartão Crédito', cartao_debito: 'Cartão Débito' }[m] ?? m
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: '2-digit',
    hour: '2-digit', minute: '2-digit',
    timeZone: 'America/Sao_Paulo',
  })
}
</script>
