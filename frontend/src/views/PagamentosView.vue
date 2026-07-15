<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-6 flex-wrap gap-3">
      <h2 class="text-xl font-bold text-gray-800">Pagamentos</h2>
      <button
        @click="novaComandaVazia"
        class="flex items-center gap-2 text-sm bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Nova comanda
      </button>
    </div>

    <!-- Card Total -->
    <div class="flex items-center gap-3 mb-5 bg-white border border-gray-200 rounded-xl px-5 py-3 w-fit shadow-sm">
      <div>
        <p class="text-xs text-gray-400 font-medium uppercase tracking-wide">Total recebido (filtro atual)</p>
        <p class="text-2xl font-bold text-gray-800 mt-0.5">
          <span v-if="mostrarTotal">R$ {{ totalRecebido }}</span>
          <span v-else class="tracking-[0.25em] text-gray-400 text-xl select-none">••••••</span>
        </p>
      </div>
      <button
        @click="mostrarTotal = !mostrarTotal"
        class="ml-2 p-2 rounded-full hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
        type="button"
      >
        <svg v-if="mostrarTotal" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.477 0 8.268 2.943 9.542 7-1.274 4.057-5.065 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.477 0-8.268-2.943-9.542-7a9.97 9.97 0 012.163-3.592m3.08-2.634A9.954 9.954 0 0112 5c4.477 0 8.268 2.943 9.542 7a9.966 9.966 0 01-1.357 2.716M3 3l18 18"/>
        </svg>
      </button>
    </div>

    <!-- Filtros -->
    <div class="flex flex-wrap gap-3 mb-4">
      <select v-model="filtroStatus" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400">
        <option value="">Todos os status</option>
        <option value="pendente">Pendente</option>
        <option value="confirmado">Confirmado</option>
        <option value="concluido">Concluído</option>
        <option value="pre_agendamento">Pré-agendamento</option>
      </select>
      <div class="flex items-center gap-2">
        <label class="text-xs text-gray-500 font-medium">De</label>
        <input v-model="filtroDe" type="date" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"/>
      </div>
      <div class="flex items-center gap-2">
        <label class="text-xs text-gray-500 font-medium">Até</label>
        <input v-model="filtroAte" type="date" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"/>
      </div>
      <button
        @click="filtroPendentePag = !filtroPendentePag; filtroStatus = ''"
        :class="[
          'text-xs font-medium px-3 py-2 rounded-lg border transition-colors',
          filtroPendentePag ? 'bg-yellow-500 text-white border-yellow-500' : 'border-yellow-300 text-yellow-700 hover:bg-yellow-50',
        ]"
      >Pendentes de pagamento</button>
      <button
        v-if="filtroStatus || filtroDe !== hoje || filtroAte !== hoje || filtroPendentePag"
        @click="filtroStatus = ''; filtroDe = hoje; filtroAte = hoje; filtroPendentePag = false"
        class="text-xs text-gray-400 hover:text-gray-600 px-2 py-1 rounded"
      >✕ Limpar</button>
    </div>

    <!-- Tabela de agendamentos -->
    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
      <div v-else-if="listaFiltrada.length === 0" class="p-8 text-center text-sm text-gray-400">
        Nenhum agendamento encontrado.
      </div>
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Cliente</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Serviços</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Total</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Status</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Pagamento</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Ações</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr
            v-for="ag in listaFiltrada"
            :key="ag.id"
            :class="['hover:bg-gray-50 align-top', ag.status === 'concluido' && !ag.pagamento ? 'bg-red-50' : '']"
          >
            <td class="px-4 py-3 font-medium text-gray-800">{{ ag.cliente?.nome || '-' }}</td>
            <td class="px-4 py-3 text-gray-600">
              <div v-for="item in ag.itens" :key="item.id" class="text-xs leading-5">
                {{ item.servico?.nome }}
                <span class="text-gray-400">· {{ item.profissional?.nome }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-sm font-semibold text-gray-700">
              R$ {{ totalAgendamento(ag) }}
            </td>
            <td class="px-4 py-3">
              <span :class="statusBadgeClass(ag.status)" class="text-xs font-semibold px-2.5 py-0.5 rounded-full">
                {{ statusLabel(ag.status) }}
              </span>
            </td>
            <td class="px-4 py-3">
              <!-- Pagamento legado (sistema antigo) -->
              <div v-if="ag.pagamento" class="text-xs space-y-0.5">
                <div class="flex items-center gap-1.5 flex-wrap">
                  <span class="font-semibold text-green-700">R$ {{ Number(ag.pagamento.valor).toFixed(2) }}</span>
                  <span
                    v-if="Number(ag.pagamento.credito_utilizado) > 0"
                    class="text-indigo-700 bg-indigo-100 px-1.5 py-0.5 rounded font-medium"
                  >Crédito: R$ {{ Number(ag.pagamento.credito_utilizado).toFixed(2) }}</span>
                </div>
                <div class="text-gray-400">{{ metodoPagLabel(ag.pagamento.metodo) }}</div>
                <div class="text-gray-400">{{ formatDate(ag.pagamento.pago_em) }}</div>
              </div>
              <!-- Sem pagamento -->
              <span v-else class="text-xs text-gray-300 italic">Não pago</span>
              <span
                v-if="ag.status === 'concluido' && !ag.pagamento"
                class="inline-block mt-1 text-xs font-semibold text-red-600 bg-red-100 px-2 py-0.5 rounded-full"
              >Inadimplente</span>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-col gap-1.5">
                <!-- Botão principal: abrir comanda para este agendamento -->
                <button
                  v-if="!ag.pagamento && ag.status !== 'cancelado' && ag.status !== 'pre_agendamento'"
                  @click="abrirComandaParaAgendamento(ag)"
                  :disabled="abrindoComanda === ag.id"
                  class="text-xs bg-rose-600 hover:bg-rose-700 text-white px-3 py-1.5 rounded-md font-medium disabled:opacity-50 flex items-center gap-1"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                  </svg>
                  {{ abrindoComanda === ag.id ? 'Abrindo...' : 'Abrir comanda' }}
                </button>
                <!-- Editar pagamento legado -->
                <button
                  v-if="ag.pagamento"
                  @click="abrirModalEditar(ag)"
                  class="text-xs bg-amber-500 hover:bg-amber-600 text-white px-3 py-1.5 rounded-md font-medium"
                >
                  Editar pagamento
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════
         MODAL COMANDA
    ════════════════════════════════════════════════════════════════ -->
    <div v-if="comanda" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-3 sm:p-6">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[92vh] flex flex-col">

        <!-- Header da comanda -->
        <div class="px-6 py-4 border-b border-gray-100 flex items-start justify-between gap-4 shrink-0">
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-lg font-bold text-gray-800">Comanda <span class="text-rose-600">#{{ String(comanda.id).padStart(4, '0') }}</span></h3>
              <span :class="['text-xs font-semibold px-2.5 py-0.5 rounded-full', comanda.status === 'aberta' ? 'bg-green-100 text-green-700' : comanda.status === 'fechada' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500']">
                {{ comanda.status === 'aberta' ? 'Aberta' : comanda.status === 'fechada' ? 'Fechada' : 'Cancelada' }}
              </span>
            </div>
            <p class="text-xs text-gray-400 mt-0.5">Aberta às {{ formatDate(comanda.aberta_em) }}</p>
          </div>
          <button @click="fecharModalComanda" class="text-gray-400 hover:text-gray-600 p-1 mt-0.5 shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <!-- Corpo scrollável -->
        <div class="flex-1 overflow-y-auto px-6 py-5 space-y-6">

          <!-- ── ITENS ─────────────────────────────────────────────── -->
          <section>
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider">Itens da comanda</h4>
              <div v-if="comanda.status === 'aberta'" class="flex gap-2">
                <button
                  @click="painelAdicionarAg = !painelAdicionarAg; painelAvulso = false"
                  :class="['text-xs px-2.5 py-1 rounded-md font-medium border transition-colors', painelAdicionarAg ? 'bg-rose-600 text-white border-rose-600' : 'border-gray-300 text-gray-600 hover:bg-gray-50']"
                >+ Agendamento</button>
                <button
                  @click="painelAvulso = !painelAvulso; painelAdicionarAg = false"
                  :class="['text-xs px-2.5 py-1 rounded-md font-medium border transition-colors', painelAvulso ? 'bg-rose-600 text-white border-rose-600' : 'border-gray-300 text-gray-600 hover:bg-gray-50']"
                >+ Avulso</button>
              </div>
            </div>

            <!-- Lista de itens -->
            <div v-if="comanda.itens.length === 0" class="text-sm text-gray-400 italic text-center py-4">
              Nenhum item adicionado ainda.
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="item in comanda.itens"
                :key="item.id"
                class="flex items-center justify-between bg-gray-50 rounded-lg px-3 py-2.5 gap-3"
              >
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-800 truncate">
                    {{ item.servico?.nome || item.descricao }}
                    <span v-if="item.tipo !== 'agendamento'" class="ml-1 text-xs text-gray-400 font-normal">(avulso)</span>
                  </p>
                  <p class="text-xs text-gray-400 truncate">
                    {{ item.cliente?.nome }}
                    <span v-if="item.profissional"> · {{ item.profissional.nome }}</span>
                    <span v-if="item.quantidade > 1"> · {{ item.quantidade }}×</span>
                    <span v-if="Number(item.desconto) > 0"> · -R$ {{ Number(item.desconto).toFixed(2) }}</span>
                  </p>
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <span class="text-sm font-semibold text-gray-700">
                    R$ {{ subtotalItem(item) }}
                  </span>
                  <button
                    v-if="comanda.status === 'aberta'"
                    @click="removerItemComanda(item.id)"
                    class="text-gray-300 hover:text-red-500 transition-colors"
                    title="Remover item"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Painel: adicionar agendamento -->
            <div v-if="painelAdicionarAg" class="mt-3 border border-dashed border-rose-200 rounded-xl p-4 bg-rose-50/30">
              <p class="text-xs font-semibold text-rose-700 mb-2">Adicionar agendamento à comanda</p>
              <input
                v-model="buscaAgComanda"
                type="text"
                placeholder="Buscar por cliente..."
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-rose-300"
              />
              <div class="space-y-1.5 max-h-44 overflow-y-auto">
                <div
                  v-for="ag in agendamentosParaAdicionar"
                  :key="ag.id"
                  class="flex items-center justify-between bg-white rounded-lg px-3 py-2 border border-gray-200 cursor-pointer hover:border-rose-300 hover:bg-rose-50 transition-colors"
                  @click="adicionarAgendamentoComanda(ag)"
                >
                  <div>
                    <p class="text-sm font-medium text-gray-800">{{ ag.cliente?.nome }}</p>
                    <p class="text-xs text-gray-400">
                      {{ ag.itens?.map(i => i.servico?.nome).join(', ') }} · R$ {{ totalAgendamento(ag) }}
                    </p>
                  </div>
                  <span class="text-xs text-rose-600 font-semibold">Adicionar</span>
                </div>
                <div v-if="agendamentosParaAdicionar.length === 0" class="text-xs text-gray-400 text-center py-2">
                  Nenhum agendamento disponível.
                </div>
              </div>
            </div>

            <!-- Painel: item avulso -->
            <div v-if="painelAvulso" class="mt-3 border border-dashed border-gray-200 rounded-xl p-4">
              <p class="text-xs font-semibold text-gray-600 mb-3">Adicionar serviço ou produto avulso</p>
              <div class="space-y-3">
                <div class="flex gap-3">
                  <div class="flex-1">
                    <label class="block text-xs text-gray-500 mb-1">Tipo</label>
                    <select v-model="formAvulso.tipo" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300">
                      <option value="servico_avulso">Serviço avulso</option>
                      <option value="produto">Produto</option>
                    </select>
                  </div>
                  <div class="flex-1">
                    <label class="block text-xs text-gray-500 mb-1">Cliente *</label>
                    <select v-model="formAvulso.cliente_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300">
                      <option value="">Selecione...</option>
                      <option v-for="c in clientesDaComanda" :key="c.id" :value="c.id">{{ c.nome }}</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Descrição *</label>
                  <input
                    v-model="formAvulso.descricao"
                    type="text"
                    placeholder="Ex: Hidratação capilar, Shampoo Kerastase..."
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300"
                  />
                </div>
                <div class="flex gap-3">
                  <div class="flex-1">
                    <label class="block text-xs text-gray-500 mb-1">Valor (R$) *</label>
                    <input
                      v-model="formAvulso.valor_unitario"
                      type="number"
                      step="0.01"
                      min="0.01"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300"
                    />
                  </div>
                  <div class="flex-1">
                    <label class="block text-xs text-gray-500 mb-1">Qtd</label>
                    <input
                      v-model="formAvulso.quantidade"
                      type="number"
                      min="1"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300"
                    />
                  </div>
                  <div class="flex-1">
                    <label class="block text-xs text-gray-500 mb-1">Desconto</label>
                    <input
                      v-model="formAvulso.desconto"
                      type="number"
                      step="0.01"
                      min="0"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300"
                    />
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

          <!-- ── RESUMO FINANCEIRO ─────────────────────────────────── -->
          <section class="bg-gray-50 rounded-xl p-4 space-y-1.5">
            <div class="flex justify-between text-sm text-gray-600">
              <span>Total dos itens</span>
              <span class="font-semibold">R$ {{ fmt(comanda.total_itens) }}</span>
            </div>
            <div v-if="Number(comanda.total_pago) > 0" class="flex justify-between text-sm text-green-700">
              <span>Já pago</span>
              <span class="font-semibold">- R$ {{ fmt(comanda.total_pago) }}</span>
            </div>
            <div class="flex justify-between text-base font-bold border-t border-gray-200 pt-2 mt-1"
                 :class="Number(comanda.saldo_restante) > 0 ? 'text-gray-800' : 'text-green-700'">
              <span>{{ Number(comanda.saldo_restante) > 0 ? 'Restante' : 'Saldo quitado ✓' }}</span>
              <span>R$ {{ fmt(comanda.saldo_restante) }}</span>
            </div>
          </section>

          <!-- ── PAGAMENTOS JÁ REGISTRADOS ────────────────────────── -->
          <section v-if="comanda.pagamentos.length > 0">
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Pagamentos registrados</h4>
            <div class="space-y-2">
              <div
                v-for="p in comanda.pagamentos"
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

          <!-- ── FORMULÁRIO DE PAGAMENTO ───────────────────────────── -->
          <section v-if="comanda.status === 'aberta' && comanda.itens.length > 0">
            <h4 class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">
              {{ comanda.pagamentos.length === 0 ? 'Registrar pagamento' : 'Adicionar pagamento (split)' }}
            </h4>
            <div class="space-y-3">
              <!-- Saldo de crédito disponível -->
              <div v-if="creditoDisponivel > 0" class="bg-indigo-50 border border-indigo-100 rounded-lg p-3">
                <div class="flex justify-between items-center mb-2">
                  <label class="text-sm font-semibold text-indigo-800">
                    Usar crédito do cliente (saldo: R$ {{ fmt(creditoDisponivel) }})
                  </label>
                </div>
                <input
                  v-model="formPag.credito_utilizado"
                  type="number"
                  step="0.01"
                  min="0"
                  :max="creditoDisponivel"
                  class="w-full border border-indigo-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-white"
                  placeholder="0.00"
                />
              </div>

              <div class="flex gap-3">
                <div class="flex-1">
                  <label class="block text-xs text-gray-500 mb-1">Valor (R$) *</label>
                  <input
                    v-model="formPag.valor"
                    type="number"
                    step="0.01"
                    min="0.01"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                  />
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

              <!-- Quem está pagando (só mostra se houver múltiplos clientes) -->
              <div v-if="clientesDaComanda.length > 1">
                <label class="block text-xs text-gray-500 mb-1">Quem está pagando</label>
                <select v-model="formPag.pagador_cliente_id" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400">
                  <option :value="null">{{ clientesDaComanda[0]?.nome }} (principal)</option>
                  <option v-for="c in clientesDaComanda" :key="c.id" :value="c.id">{{ c.nome }}</option>
                </select>
              </div>

              <!-- Preview troco como crédito -->
              <div v-if="formPag.metodo === 'dinheiro' && trocoComoCreditoPrev > 0" class="bg-green-50 text-green-800 px-3 py-2 rounded-lg text-xs font-semibold">
                R$ {{ trocoComoCreditoPrev.toFixed(2) }} será adicionado como crédito ao cliente.
              </div>

              <!-- Atalho: valor exato restante -->
              <button
                v-if="Number(comanda.saldo_restante) > 0"
                type="button"
                @click="formPag.valor = fmt(comanda.saldo_restante)"
                class="text-xs text-rose-600 hover:underline"
              >Usar valor exato restante (R$ {{ fmt(comanda.saldo_restante) }})</button>

              <p v-if="erroPag" class="text-sm text-red-600">{{ erroPag }}</p>

              <button
                @click="registrarPagamentoComanda"
                :disabled="salvandoPag"
                class="w-full bg-green-600 hover:bg-green-700 text-white text-sm font-semibold py-2.5 rounded-lg disabled:opacity-50 transition-colors"
              >{{ salvandoPag ? 'Registrando...' : 'Registrar pagamento' }}</button>
            </div>
          </section>

          <p v-if="erroComanda" class="text-sm text-red-600 text-center">{{ erroComanda }}</p>
        </div>

        <!-- Footer da comanda -->
        <div class="px-6 py-4 border-t border-gray-100 flex gap-3 shrink-0">
          <button
            v-if="comanda.status === 'aberta'"
            @click="cancelarComandaAction"
            :disabled="salvandoFechar"
            class="border border-gray-300 text-gray-600 rounded-lg px-4 py-2 text-sm hover:bg-gray-50 disabled:opacity-50 transition-colors"
          >Cancelar comanda</button>
          <button
            v-if="comanda.status === 'aberta'"
            @click="fecharComandaAction"
            :disabled="salvandoFechar || Number(comanda.saldo_restante) > 0 || comanda.itens.length === 0"
            class="flex-1 bg-rose-600 hover:bg-rose-700 text-white rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-50 transition-colors"
            :title="Number(comanda.saldo_restante) > 0 ? 'Quitar o saldo restante antes de fechar' : ''"
          >
            {{ salvandoFechar ? 'Fechando...' : Number(comanda.saldo_restante) > 0 ? `Falta R$ ${fmt(comanda.saldo_restante)}` : 'Fechar comanda ✓' }}
          </button>
          <button
            v-if="comanda.status !== 'aberta'"
            @click="fecharModalComanda"
            class="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 text-sm font-semibold"
          >Fechar</button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════════
         MODAL EDITAR PAGAMENTO (legado)
    ════════════════════════════════════════════════════════════════ -->
    <div v-if="modalEditarAberto" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-1">Editar Pagamento</h3>
        <p class="text-sm text-gray-500 mb-4">
          Agendamento <strong>#{{ agEditarSelecionado?.id }}</strong> · {{ agEditarSelecionado?.cliente?.nome }}
        </p>
        <p class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 mb-4">
          Atenção: esta operação corrige o registro sem recalcular o saldo de crédito do cliente.
        </p>
        <form @submit.prevent="confirmarEdicaoPagamento" class="space-y-4">
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Valor cobrado (R$) *</label>
              <input v-model="formEditar.valor" type="number" step="0.01" min="0.01" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"/>
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-700 mb-1">Crédito utilizado (R$)</label>
              <input v-model="formEditar.credito_utilizado" type="number" step="0.01" min="0" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400"/>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Método *</label>
            <select v-model="formEditar.metodo" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400">
              <option value="">Selecione...</option>
              <option value="dinheiro">Dinheiro</option>
              <option value="pix">PIX</option>
              <option value="cartao_credito">Cartão de Crédito</option>
              <option value="cartao_debito">Cartão de Débito</option>
            </select>
          </div>
          <p v-if="erroEditar" class="text-sm text-red-600">{{ erroEditar }}</p>
          <div class="flex gap-3 pt-1">
            <button type="button" @click="modalEditarAberto = false" class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-2 text-sm hover:bg-gray-50">Cancelar</button>
            <button type="submit" :disabled="savingEditar" class="flex-1 bg-amber-500 hover:bg-amber-600 text-white rounded-lg py-2 text-sm font-semibold disabled:opacity-50">
              {{ savingEditar ? 'Salvando...' : 'Salvar correção' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated } from 'vue'
import api from '@/api/client'
import { useToast } from '@/composables/useToast'

defineOptions({ name: 'PagamentosView' })

const { sucesso: toastSucesso } = useToast()

// ── Agendamentos (lista principal) ──────────────────────────────────────────
const agendamentos = ref([])
const loading = ref(true)
const filtroStatus = ref('')
const filtroPendentePag = ref(false)
const hoje = new Date().toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' })
const filtroDe = ref(hoje)
const filtroAte = ref(hoje)
const mostrarTotal = ref(false)
const abrindoComanda = ref(null) // id do agendamento sendo processado

// ── Comanda (modal principal) ────────────────────────────────────────────────
const comanda = ref(null)
const erroComanda = ref('')
const painelAdicionarAg = ref(false)
const painelAvulso = ref(false)
const buscaAgComanda = ref('')
const salvandoFechar = ref(false)

// Formulário de pagamento dentro da comanda
const formPag = ref({ valor: '', metodo: '', credito_utilizado: '0.00', pagador_cliente_id: null })
const salvandoPag = ref(false)
const erroPag = ref('')

// Formulário de item avulso
const formAvulso = ref({ tipo: 'servico_avulso', cliente_id: '', descricao: '', valor_unitario: '', quantidade: 1, desconto: '0.00' })
const salvandoAvulso = ref(false)
const erroAvulso = ref('')

// ── Modal editar pagamento legado ────────────────────────────────────────────
const modalEditarAberto = ref(false)
const agEditarSelecionado = ref(null)
const savingEditar = ref(false)
const erroEditar = ref('')
const formEditar = ref({ valor: '', credito_utilizado: '0.00', metodo: '' })

// ── Computed ─────────────────────────────────────────────────────────────────

const totalRecebido = computed(() =>
  listaFiltrada.value
    .filter(ag => ag.pagamento)
    .reduce((sum, ag) => sum + Number(ag.pagamento?.valor || 0), 0)
    .toFixed(2)
)

const listaFiltrada = computed(() =>
  agendamentos.value.filter(ag => {
    if (filtroPendentePag.value && ag.pagamento) return false
    if (filtroStatus.value && ag.status !== filtroStatus.value) return false
    if (filtroDe.value || filtroAte.value) {
      const dataRef = ag.itens?.[0]?.data_hora_inicio ?? ag.criado_em
      const d = new Date(dataRef)
      const dSemHora = new Date(d.getFullYear(), d.getMonth(), d.getDate())
      if (filtroDe.value && dSemHora < new Date(filtroDe.value + 'T00:00:00')) return false
      if (filtroAte.value && dSemHora > new Date(filtroAte.value + 'T23:59:59')) return false
    }
    return true
  })
)

/** Clientes únicos que já têm itens na comanda aberta (para o select de pagador e avulso). */
const clientesDaComanda = computed(() => {
  if (!comanda.value) return []
  const mapa = new Map()
  for (const item of comanda.value.itens) {
    if (item.cliente && !mapa.has(item.cliente.id)) {
      mapa.set(item.cliente.id, item.cliente)
    }
  }
  return [...mapa.values()]
})

/** Saldo de crédito do primeiro cliente da comanda. */
const creditoDisponivel = computed(() => {
  if (!clientesDaComanda.value.length) return 0
  return Number(clientesDaComanda.value[0].saldo_credito || 0)
})

/** Agendamentos do intervalo que NÃO estão na comanda atual e podem ser adicionados. */
const agIdsNaComanda = computed(() => new Set(
  (comanda.value?.itens ?? [])
    .filter(i => i.agendamento_id)
    .map(i => i.agendamento_id)
))

const agendamentosParaAdicionar = computed(() => {
  const busca = buscaAgComanda.value.toLowerCase()
  return agendamentos.value.filter(ag => {
    if (ag.status === 'cancelado' || ag.status === 'pre_agendamento') return false
    if (agIdsNaComanda.value.has(ag.id)) return false
    if (busca && !ag.cliente?.nome?.toLowerCase().includes(busca)) return false
    return true
  })
})

/** Preview do troco que virará crédito no pagamento em dinheiro. */
const trocoComoCreditoPrev = computed(() => {
  if (formPag.value.metodo !== 'dinheiro') return 0
  const saldoRestante = Number(comanda.value?.saldo_restante ?? 0)
  const credito = Number(formPag.value.credito_utilizado || 0)
  const valorDevido = Math.max(0, saldoRestante - credito)
  return Math.max(0, Number(formPag.value.valor || 0) - valorDevido)
})

// ── Fetch agendamentos ────────────────────────────────────────────────────────

async function fetchAgendamentos() {
  loading.value = true
  const params = {}
  if (filtroDe.value) params.data_inicio = filtroDe.value
  if (filtroAte.value) params.data_fim = filtroAte.value
  try {
    const { data } = await api.get('/agendamentos/', { params })
    agendamentos.value = data
  } finally {
    loading.value = false
  }
}

let _debounceFetch
watch([filtroDe, filtroAte], () => {
  clearTimeout(_debounceFetch)
  _debounceFetch = setTimeout(fetchAgendamentos, 250)
})

// ── Comanda — abrir ───────────────────────────────────────────────────────────

/** Abre uma comanda nova do zero (sem agendamento pré-vinculado). */
async function novaComandaVazia() {
  try {
    const { data } = await api.post('/comandas/', {})
    comanda.value = data
    erroComanda.value = ''
    painelAdicionarAg.value = true
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao abrir comanda.'
  }
}

/** Abre comanda a partir de um agendamento da tabela — adiciona itens automaticamente. */
async function abrirComandaParaAgendamento(ag) {
  abrindoComanda.value = ag.id
  erroComanda.value = ''
  try {
    // 1. Cria a comanda
    const { data: novaComanda } = await api.post('/comandas/', {})

    // 2. Adiciona automaticamente os itens do agendamento
    await api.post(`/comandas/${novaComanda.id}/itens/agendamento`, {
      agendamento_id: ag.id,
      cliente_id: ag.cliente_id,
    })

    // 3. Recarrega comanda com totais calculados
    await recarregarComanda(novaComanda.id)
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao abrir comanda.'
    comanda.value = null
  } finally {
    abrindoComanda.value = null
  }
}

async function recarregarComanda(id) {
  const { data } = await api.get(`/comandas/${id ?? comanda.value.id}`)
  comanda.value = data
}

function fecharModalComanda() {
  comanda.value = null
  painelAdicionarAg.value = false
  painelAvulso.value = false
  buscaAgComanda.value = ''
  formPag.value = { valor: '', metodo: '', credito_utilizado: '0.00', pagador_cliente_id: null }
  formAvulso.value = { tipo: 'servico_avulso', cliente_id: '', descricao: '', valor_unitario: '', quantidade: 1, desconto: '0.00' }
  erroPag.value = ''
  erroAvulso.value = ''
  erroComanda.value = ''
}

// ── Comanda — itens ───────────────────────────────────────────────────────────

async function adicionarAgendamentoComanda(ag) {
  try {
    await api.post(`/comandas/${comanda.value.id}/itens/agendamento`, {
      agendamento_id: ag.id,
      cliente_id: ag.cliente_id,
    })
    await recarregarComanda()
    buscaAgComanda.value = ''
    painelAdicionarAg.value = false
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao adicionar agendamento.'
  }
}

async function removerItemComanda(itemId) {
  try {
    await api.delete(`/comandas/${comanda.value.id}/itens/${itemId}`)
    await recarregarComanda()
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao remover item.'
  }
}

async function confirmarItemAvulso() {
  erroAvulso.value = ''
  if (!formAvulso.value.cliente_id) { erroAvulso.value = 'Selecione o cliente.'; return }
  if (!formAvulso.value.descricao && !formAvulso.value.servico_id) { erroAvulso.value = 'Informe a descrição.'; return }
  if (!formAvulso.value.valor_unitario || Number(formAvulso.value.valor_unitario) <= 0) { erroAvulso.value = 'Informe o valor.'; return }

  salvandoAvulso.value = true
  try {
    await api.post(`/comandas/${comanda.value.id}/itens/avulso`, {
      tipo: formAvulso.value.tipo,
      cliente_id: Number(formAvulso.value.cliente_id),
      descricao: formAvulso.value.descricao || null,
      valor_unitario: Number(formAvulso.value.valor_unitario),
      quantidade: Number(formAvulso.value.quantidade) || 1,
      desconto: Number(formAvulso.value.desconto) || 0,
    })
    await recarregarComanda()
    formAvulso.value = { tipo: 'servico_avulso', cliente_id: '', descricao: '', valor_unitario: '', quantidade: 1, desconto: '0.00' }
    painelAvulso.value = false
  } catch (e) {
    erroAvulso.value = e.response?.data?.detail || 'Erro ao adicionar item.'
  } finally {
    salvandoAvulso.value = false
  }
}

// ── Comanda — pagamento ───────────────────────────────────────────────────────

async function registrarPagamentoComanda() {
  erroPag.value = ''
  if (!formPag.value.valor || Number(formPag.value.valor) <= 0) { erroPag.value = 'Informe o valor.'; return }
  if (!formPag.value.metodo) { erroPag.value = 'Selecione o método.'; return }

  salvandoPag.value = true
  try {
    await api.post(`/comandas/${comanda.value.id}/pagamentos`, {
      valor: Number(formPag.value.valor),
      metodo: formPag.value.metodo,
      credito_utilizado: Number(formPag.value.credito_utilizado) || 0,
      pagador_cliente_id: formPag.value.pagador_cliente_id || null,
    })
    await recarregarComanda()
    formPag.value = { valor: '', metodo: '', credito_utilizado: '0.00', pagador_cliente_id: null }
  } catch (e) {
    erroPag.value = e.response?.data?.detail || 'Erro ao registrar pagamento.'
  } finally {
    salvandoPag.value = false
  }
}

// ── Comanda — fechar / cancelar ───────────────────────────────────────────────

async function fecharComandaAction() {
  salvandoFechar.value = true
  erroComanda.value = ''
  try {
    await api.post(`/comandas/${comanda.value.id}/fechar`)
    await recarregarComanda()
    toastSucesso('Comanda fechada com sucesso!')
    await fetchAgendamentos()
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao fechar comanda.'
  } finally {
    salvandoFechar.value = false
  }
}

async function cancelarComandaAction() {
  if (!confirm('Cancelar a comanda? Os pagamentos registrados serão estornados.')) return
  salvandoFechar.value = true
  erroComanda.value = ''
  try {
    await api.post(`/comandas/${comanda.value.id}/cancelar`)
    await recarregarComanda()
    toastSucesso('Comanda cancelada.')
    await fetchAgendamentos()
  } catch (e) {
    erroComanda.value = e.response?.data?.detail || 'Erro ao cancelar comanda.'
  } finally {
    salvandoFechar.value = false
  }
}

// ── Modal editar pagamento legado ─────────────────────────────────────────────

function abrirModalEditar(ag) {
  agEditarSelecionado.value = ag
  formEditar.value = {
    valor: ag.pagamento?.valor ?? '',
    credito_utilizado: ag.pagamento?.credito_utilizado ?? '0.00',
    metodo: ag.pagamento?.metodo ?? '',
  }
  erroEditar.value = ''
  modalEditarAberto.value = true
}

async function confirmarEdicaoPagamento() {
  savingEditar.value = true
  erroEditar.value = ''
  try {
    await api.put(`/agendamentos/${agEditarSelecionado.value.id}/pagamento`, {
      valor: formEditar.value.valor,
      metodo: formEditar.value.metodo,
      credito_utilizado: formEditar.value.credito_utilizado || 0,
    })
    modalEditarAberto.value = false
    toastSucesso('Pagamento corrigido com sucesso!')
    await fetchAgendamentos()
  } catch (e) {
    erroEditar.value = e.response?.data?.detail || 'Erro ao editar pagamento.'
  } finally {
    savingEditar.value = false
  }
}

// ── Utilitários ───────────────────────────────────────────────────────────────

function subtotalItem(item) {
  return (Number(item.valor_unitario) * Number(item.quantidade) - Number(item.desconto)).toFixed(2)
}

function fmt(v) {
  return Number(v || 0).toFixed(2)
}

function totalAgendamento(ag) {
  if (!ag?.itens) return '0.00'
  return ag.itens.reduce((sum, item) => sum + Number(item.servico?.preco || 0), 0).toFixed(2)
}

function statusLabel(s) {
  return { pendente: 'Pendente', confirmado: 'Confirmado', concluido: 'Concluído', pre_agendamento: 'Pré-agendamento', cancelado: 'Cancelado' }[s] ?? s
}

function statusBadgeClass(s) {
  return {
    pendente:        'bg-gray-600 text-gray-100',
    confirmado:      'bg-green-700 text-white',
    concluido:       'bg-blue-700 text-white',
    pre_agendamento: 'bg-red-700 text-white',
    cancelado:       'bg-red-700 text-white',
  }[s] ?? 'bg-gray-500 text-white'
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

// ── Lifecycle ─────────────────────────────────────────────────────────────────

const lastFetchAt = ref(0)
const STALE_MS = 5 * 60 * 1000

onMounted(() => {
  fetchAgendamentos()
  lastFetchAt.value = Date.now()
})

onActivated(() => {
  if (!lastFetchAt.value) return
  if (Date.now() - lastFetchAt.value > STALE_MS) {
    fetchAgendamentos()
    lastFetchAt.value = Date.now()
  }
})
</script>
