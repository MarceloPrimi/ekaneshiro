<template>
  <div class="flex flex-col lg:flex-row gap-5 lg:gap-6 min-h-0">
    <!-- Desktop: submenu lateral (estilo Horizon sidebar pills) -->
    <aside class="hidden lg:flex w-60 flex-shrink-0 flex-col">
      <p class="px-3 text-xs font-bold uppercase tracking-wider text-gray-400 mb-3">Financeiro</p>
      <nav class="flex flex-col gap-1">
        <button
          v-for="sec in secoes"
          :key="sec.id"
          type="button"
          class="flex items-center gap-3 rounded-[14px] px-3 py-3 text-left text-sm font-medium transition-all"
          :class="secao === sec.id
            ? 'bg-rose-50 text-rose-700 shadow-sm'
            : 'text-gray-600 hover:bg-white hover:shadow-sm'"
          @click="secao = sec.id"
        >
          <span
            class="flex h-9 w-9 items-center justify-center rounded-full"
            :class="secao === sec.id ? 'bg-rose-100 text-rose-600' : 'bg-gray-100 text-gray-500'"
          >
            <Wallet v-if="sec.id === 'contas-pagar'" class="h-4 w-4" />
            <CircleDollarSign v-else class="h-4 w-4" />
          </span>
          <span class="min-w-0">
            <span class="block truncate">{{ sec.label }}</span>
            <span v-if="sec.emBreve" class="block text-[11px] font-normal text-amber-600">Em breve</span>
          </span>
        </button>
      </nav>
    </aside>

    <div class="flex-1 min-w-0">
      <!-- Mobile hub -->
      <div v-if="!secao" class="lg:hidden space-y-4">
        <div>
          <h2 class="text-2xl font-bold text-gray-900">Financeiro</h2>
          <p class="text-sm text-gray-500 mt-1">Escolha uma área para continuar</p>
        </div>
        <button
          v-for="sec in secoes"
          :key="'m-' + sec.id"
          type="button"
          class="w-full flex items-center gap-4 rounded-[20px] bg-white p-5 shadow-sm shadow-gray-200 active:scale-[0.99] transition"
          @click="secao = sec.id"
        >
          <span class="flex h-12 w-12 items-center justify-center rounded-full bg-rose-50 text-rose-600">
            <Wallet v-if="sec.id === 'contas-pagar'" class="h-5 w-5" />
            <CircleDollarSign v-else class="h-5 w-5" />
          </span>
          <span class="text-left min-w-0">
            <span class="block text-base font-bold text-gray-900">{{ sec.label }}</span>
            <span class="block text-sm text-gray-500 mt-0.5">{{ sec.descricao }}</span>
            <span v-if="sec.emBreve" class="block text-xs font-medium text-amber-600 mt-2">Em breve</span>
          </span>
        </button>
      </div>

      <!-- Contas a pagar -->
      <div v-else-if="secao === 'contas-pagar'" class="space-y-5">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div class="flex items-start gap-2 min-w-0">
            <button
              type="button"
              class="lg:hidden mt-1 text-sm text-rose-600 font-medium"
              @click="secao = null"
            >
              ← Voltar
            </button>
            <div>
              <h2 class="text-2xl font-bold text-gray-900">Contas a pagar</h2>
              <p class="text-sm text-gray-500 mt-0.5">Despesas e custos do salão</p>
            </div>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <input
              v-model="mes"
              type="month"
              class="rounded-2xl border border-gray-200 bg-white px-3 py-2.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
              @change="carregar"
            />
            <div class="relative" ref="menuRef" @click.stop>
              <button
                type="button"
                class="inline-flex items-center gap-2 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white text-sm font-semibold px-4 py-2.5 shadow-sm shadow-rose-200 transition"
                @click="menuAberto = !menuAberto"
              >
                <Plus class="h-4 w-4" />
                Despesas
              </button>
              <div
                v-if="menuAberto"
                class="absolute right-0 mt-2 w-52 overflow-hidden rounded-2xl bg-white shadow-xl shadow-gray-200 ring-1 ring-gray-100 z-20 py-1"
              >
                <button
                  type="button"
                  class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-rose-50 hover:text-rose-700"
                  @click="menuAberto = false; abrirModalNovo()"
                >
                  Nova despesa
                </button>
                <button
                  type="button"
                  class="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-rose-50 hover:text-rose-700"
                  @click="menuAberto = false; abrirModalTipo()"
                >
                  Novo tipo de despesa
                </button>
                <label
                  class="block w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-rose-50 hover:text-rose-700 cursor-pointer"
                  :class="{ 'opacity-50 pointer-events-none': importando }"
                >
                  {{ importando ? 'Importando...' : 'Importar Excel' }}
                  <input type="file" accept=".xlsx,.xlsm" class="hidden" @change="onImportFile" />
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Widgets KPI (padrão Horizon + paleta Sanshin) -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div class="flex items-center gap-4 rounded-[20px] bg-white p-4 shadow-sm shadow-gray-200">
            <div class="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-full bg-rose-50 text-rose-600">
              <BarChart3 class="h-7 w-7" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium text-gray-500">Total</p>
              <p class="mt-1 text-xl font-bold text-gray-900 truncate">{{ formatCurrency(resumo?.total) }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ resumo?.quantidade || 0 }} lançamentos</p>
            </div>
          </div>
          <div class="flex items-center gap-4 rounded-[20px] bg-white p-4 shadow-sm shadow-gray-200">
            <div class="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
              <CheckCircle2 class="h-7 w-7" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium text-emerald-600">Pago</p>
              <p class="mt-1 text-xl font-bold text-emerald-700 truncate">{{ formatCurrency(resumo?.total_pago) }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4 rounded-[20px] bg-white p-4 shadow-sm shadow-gray-200">
            <div class="flex h-14 w-14 flex-shrink-0 items-center justify-center rounded-full bg-amber-50 text-amber-600">
              <Clock3 class="h-7 w-7" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium text-amber-600">Pendente</p>
              <p class="mt-1 text-xl font-bold text-amber-700 truncate">{{ formatCurrency(resumo?.total_pendente) }}</p>
            </div>
          </div>
        </div>

        <!-- Filtros -->
        <div class="flex flex-wrap gap-3">
          <select
            v-model="filtroStatus"
            class="rounded-2xl border border-gray-200 bg-white px-3 py-2.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            @change="carregarDespesas"
          >
            <option value="">Todos os status</option>
            <option value="pago">Pago</option>
            <option value="pendente">Pendente</option>
          </select>
          <select
            v-model="filtroCategoria"
            class="rounded-2xl border border-gray-200 bg-white px-3 py-2.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            @change="carregarDespesas"
          >
            <option value="">Todas as categorias</option>
            <option v-for="c in categorias" :key="c.id" :value="String(c.id)">{{ c.nome }}</option>
          </select>
        </div>

        <!-- Tabela (Complex Table style) -->
        <div class="rounded-[20px] bg-white px-4 pb-5 pt-5 shadow-sm shadow-gray-200 sm:px-6">
          <div class="mb-4 flex items-center justify-between gap-2">
            <h3 class="text-lg font-bold text-gray-900">Lançamentos</h3>
            <span class="rounded-full bg-rose-50 px-3 py-1 text-xs font-semibold text-rose-700">
              {{ despesas.length }} itens
            </span>
          </div>

          <div v-if="loading" class="py-10 text-center text-sm text-gray-400">Carregando...</div>
          <div v-else-if="!despesas.length" class="py-10 text-center text-sm text-gray-400">
            Nenhuma despesa neste período.
          </div>
          <template v-else>
            <div class="overflow-x-auto">
              <table class="w-full min-w-[720px] text-sm hidden sm:table">
                <thead>
                  <tr class="border-b border-gray-100">
                    <th class="pb-3 pr-3 text-left text-xs font-bold uppercase tracking-wide text-gray-400">Status</th>
                    <th class="pb-3 pr-3 text-left text-xs font-bold uppercase tracking-wide text-gray-400">Vencimento</th>
                    <th class="pb-3 pr-3 text-left text-xs font-bold uppercase tracking-wide text-gray-400">Pagamento</th>
                    <th class="pb-3 pr-3 text-left text-xs font-bold uppercase tracking-wide text-gray-400">Descrição</th>
                    <th class="pb-3 pr-3 text-left text-xs font-bold uppercase tracking-wide text-gray-400">Tipo</th>
                    <th class="pb-3 pr-3 text-right text-xs font-bold uppercase tracking-wide text-gray-400">Valor</th>
                    <th class="pb-3 text-right text-xs font-bold uppercase tracking-wide text-gray-400"></th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="d in despesas"
                    :key="rowKey(d)"
                    class="border-b border-gray-50 last:border-0 hover:bg-gray-50/70"
                  >
                    <td class="py-3.5 pr-3">
                      <label class="inline-flex items-center gap-2 cursor-pointer select-none">
                        <input
                          type="checkbox"
                          class="h-4 w-4 accent-emerald-600"
                          :checked="d.status === 'pago'"
                          :disabled="statusSaving[rowKey(d)]"
                          @change="toggleStatus(d, $event)"
                        />
                        <span
                          class="inline-flex items-center gap-1 text-xs font-bold"
                          :class="d.status === 'pago' ? 'text-emerald-600' : 'text-amber-600'"
                        >
                          <CheckCircle2 v-if="d.status === 'pago'" class="h-3.5 w-3.5" />
                          <Clock3 v-else class="h-3.5 w-3.5" />
                          {{ d.status === 'pago' ? 'Pago' : 'Pendente' }}
                        </span>
                      </label>
                    </td>
                    <td
                      class="py-3.5 pr-3 font-semibold whitespace-nowrap"
                      :class="estaEmAtraso(d) ? 'text-red-600' : 'text-gray-700'"
                    >
                      {{ formatDate(d.data_vencimento) }}
                    </td>
                    <td class="py-3.5 pr-3 font-semibold text-gray-700 whitespace-nowrap">
                      {{ d.status === 'pago' ? formatDate(d.data_pagamento) : '—' }}
                    </td>
                    <td class="py-3.5 pr-3">
                      <p class="font-bold text-gray-900">{{ d.descricao }}</p>
                      <p v-if="d.recorrencia !== 'avulsa'" class="text-[11px] text-gray-400 mt-0.5">
                        {{ labelRecorrencia(d) }}
                      </p>
                    </td>
                    <td class="py-3.5 pr-3">
                      <span class="inline-flex rounded-full bg-rose-50 px-2.5 py-1 text-xs font-semibold text-rose-700">
                        {{ d.categoria_nome }}
                      </span>
                    </td>
                    <td class="py-3.5 pr-3 text-right font-bold text-gray-900 whitespace-nowrap">
                      {{ formatCurrency(d.valor) }}
                    </td>
                    <td class="py-3.5 text-right space-x-2 whitespace-nowrap">
                      <button class="text-xs font-semibold text-rose-600 hover:underline" @click="abrirModalEditar(d)">Editar</button>
                      <button class="text-xs font-semibold text-red-500 hover:underline" @click="confirmarExclusao(d)">Excluir</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="sm:hidden divide-y divide-gray-100">
              <div v-for="d in despesas" :key="'m-' + rowKey(d)" class="py-4 space-y-2">
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0">
                    <p class="font-bold text-gray-900">{{ d.descricao }}</p>
                    <p class="text-xs mt-0.5">
                      <span :class="estaEmAtraso(d) ? 'font-semibold text-red-600' : 'text-gray-500'">
                        Venc. {{ formatDate(d.data_vencimento) }}
                      </span>
                      <span class="text-gray-500">
                        · {{ d.status === 'pago' ? formatDate(d.data_pagamento) : 'Sem pagamento' }}
                        · {{ d.categoria_nome }}
                      </span>
                    </p>
                    <p v-if="d.recorrencia !== 'avulsa'" class="text-[11px] text-gray-400 mt-0.5">
                      {{ labelRecorrencia(d) }}
                    </p>
                  </div>
                  <p class="font-bold text-gray-900 flex-shrink-0">{{ formatCurrency(d.valor) }}</p>
                </div>
                <label class="inline-flex items-center gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    class="h-4 w-4 accent-emerald-600"
                    :checked="d.status === 'pago'"
                    :disabled="statusSaving[rowKey(d)]"
                    @change="toggleStatus(d, $event)"
                  />
                  <span
                    class="text-sm font-bold"
                    :class="d.status === 'pago' ? 'text-emerald-600' : 'text-amber-600'"
                  >
                    {{ d.status === 'pago' ? 'Pago' : 'Pendente' }}
                  </span>
                </label>
                <div class="flex gap-3 pt-1">
                  <button class="text-sm font-semibold text-rose-600 py-2" @click="abrirModalEditar(d)">Editar</button>
                  <button class="text-sm font-semibold text-red-500 py-2" @click="confirmarExclusao(d)">Excluir</button>
                </div>
              </div>
            </div>
          </template>
        </div>

        <!-- Distribuição por tipo (progress style Horizon) -->
        <div
          v-if="resumo?.por_categoria?.length"
          class="rounded-[20px] bg-white p-5 shadow-sm shadow-gray-200 sm:p-6"
        >
          <h3 class="text-lg font-bold text-gray-900 mb-5">Por tipo de despesa</h3>
          <div class="space-y-4">
            <div v-for="c in resumo.por_categoria" :key="c.categoria_id">
              <div class="mb-1.5 flex items-center justify-between text-sm">
                <span class="font-semibold text-gray-700">{{ c.categoria_nome }}</span>
                <span class="font-bold text-gray-900">
                  {{ formatCurrency(c.total) }}
                  <span class="ml-1 text-xs font-medium text-gray-400">{{ c.percentual }}%</span>
                </span>
              </div>
              <div class="h-2.5 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  class="h-2.5 rounded-full bg-gradient-to-r from-rose-400 to-rose-600 transition-all"
                  :style="{ width: Math.min(c.percentual, 100) + '%' }"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contas a receber -->
      <div v-else-if="secao === 'contas-receber'" class="space-y-5">
        <div class="flex items-start gap-2">
          <button type="button" class="lg:hidden mt-1 text-sm text-rose-600 font-medium" @click="secao = null">
            ← Voltar
          </button>
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Contas a receber</h2>
            <p class="text-sm text-gray-500 mt-0.5">Recebimentos do salão</p>
          </div>
        </div>
        <div class="rounded-[20px] border border-dashed border-rose-200 bg-white p-10 text-center shadow-sm shadow-gray-100">
          <div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-rose-50 text-rose-500">
            <CircleDollarSign class="h-7 w-7" />
          </div>
          <p class="text-base font-bold text-gray-800">Em breve</p>
          <p class="text-sm text-gray-500 mt-2 max-w-md mx-auto">
            Esta área será liberada quando o fluxo de pagamentos/recebimentos estiver consolidado.
          </p>
        </div>
      </div>
    </div>

    <!-- Modal novo tipo -->
    <div
      v-if="modalTipoAberto"
      class="fixed inset-0 z-[60] flex items-center justify-center bg-black/40 p-4"
      @click.self="modalTipoAberto = false"
    >
      <div class="w-full max-w-sm rounded-[20px] bg-white p-6 shadow-xl">
        <h3 class="text-lg font-bold text-gray-900 mb-4">Novo tipo de despesa</h3>
        <form class="space-y-3" @submit.prevent="salvarTipo">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input
              v-model="formTipo.nome"
              type="text"
              required
              maxlength="100"
              placeholder="Ex: Impostos e Taxas"
              class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
          </div>
          <p v-if="erroTipo" class="text-sm text-red-600">{{ erroTipo }}</p>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="rounded-2xl px-4 py-2 text-sm text-gray-600 hover:bg-gray-100" @click="modalTipoAberto = false">
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="salvandoTipo"
              class="rounded-2xl bg-rose-600 hover:bg-rose-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
            >
              {{ salvandoTipo ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal criar/editar -->
    <div
      v-if="modalAberto"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      @click.self="modalAberto = false"
    >
      <div class="w-full max-w-md rounded-[20px] bg-white p-6 shadow-xl max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-gray-900 mb-4">
          {{ editando ? 'Editar Despesa' : 'Nova Despesa' }}
        </h3>
        <form class="space-y-3" @submit.prevent="salvar">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
            <input
              v-model="form.descricao"
              type="text"
              required
              maxlength="300"
              class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
          </div>
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="block text-sm font-medium text-gray-700">Tipo de despesa</label>
              <button type="button" class="text-xs text-rose-600 hover:underline font-medium" @click="abrirModalTipo()">
                + Novo tipo
              </button>
            </div>
            <select
              v-model="form.categoria_id"
              required
              class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
              @change="onCategoriaChange"
            >
              <option disabled value="">Selecione...</option>
              <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Valor (R$)</label>
            <input
              v-model="form.valor"
              type="number"
              step="0.01"
              min="0.01"
              required
              class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Custo</label>
            <div class="space-y-2">
              <label class="flex items-start gap-2 cursor-pointer rounded-2xl border border-gray-100 px-3 py-2 hover:bg-rose-50/40">
                <input v-model="form.recorrencia" type="radio" value="avulsa" class="mt-1 accent-rose-600" />
                <span class="text-sm text-gray-700">
                  Único
                  <span class="block text-xs text-gray-400">Não se repete</span>
                </span>
              </label>
              <label class="flex items-start gap-2 cursor-pointer rounded-2xl border border-gray-100 px-3 py-2 hover:bg-rose-50/40">
                <input v-model="form.recorrencia" type="radio" value="mensal" class="mt-1 accent-rose-600" />
                <span class="text-sm text-gray-700">
                  Recorrente
                  <span class="block text-xs text-gray-400">Aparece automaticamente em todos os meses</span>
                </span>
              </label>
              <label class="flex items-start gap-2 cursor-pointer rounded-2xl border border-gray-100 px-3 py-2 hover:bg-rose-50/40">
                <input v-model="form.recorrencia" type="radio" value="temporaria" class="mt-1 accent-rose-600" />
                <span class="text-sm text-gray-700">
                  Temporário
                  <span class="block text-xs text-gray-400">Com data de início e fim</span>
                </span>
              </label>
            </div>
          </div>

          <div v-if="form.recorrencia === 'mensal' || form.recorrencia === 'temporaria'">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Data de vencimento <span class="text-rose-600">*</span>
            </label>
            <input
              v-model="form.data_vencimento"
              type="date"
              required
              class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
            <p v-if="form.recorrencia === 'mensal'" class="text-xs text-gray-400 mt-1">
              Nos custos recorrentes, o dia desta data se repete todo mês.
            </p>
          </div>

          <div v-if="form.recorrencia === 'mensal'">
            <label class="block text-sm font-medium text-gray-700 mb-1">Início da vigência</label>
            <input
              v-model="form.vigencia_inicio"
              type="date"
              required
              class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
          </div>

          <div v-if="form.recorrencia === 'temporaria'" class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Início</label>
              <input
                v-model="form.vigencia_inicio"
                type="date"
                required
                class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Fim</label>
              <input
                v-model="form.vigencia_fim"
                type="date"
                required
                class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
              />
            </div>
          </div>

          <label
            v-if="form.recorrencia === 'avulsa' || !editando"
            class="inline-flex items-center gap-2 cursor-pointer select-none"
          >
            <input v-model="form.pago" type="checkbox" class="h-4 w-4 accent-emerald-600" />
            <span class="text-sm text-gray-700">
              {{ form.recorrencia === 'avulsa' ? 'Já pago' : 'Já pago neste mês' }}
            </span>
          </label>

          <div v-if="form.pago && (form.recorrencia === 'avulsa' || !editando)">
            <label class="block text-sm font-medium text-gray-700 mb-1">Data do pagamento</label>
            <input
              v-model="form.data_pagamento"
              type="date"
              required
              class="w-full rounded-2xl border border-gray-200 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
            />
          </div>
          <p v-else-if="form.recorrencia === 'avulsa'" class="text-xs text-gray-400">
            Conta pendente — a data do pagamento só é preenchida quando marcar como pago.
          </p>

          <p v-if="erroForm" class="text-sm text-red-600">{{ erroForm }}</p>
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="rounded-2xl px-4 py-2 text-sm text-gray-600 hover:bg-gray-100" @click="modalAberto = false">
              Cancelar
            </button>
            <button
              type="submit"
              :disabled="salvando"
              class="rounded-2xl bg-rose-600 hover:bg-rose-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
            >
              {{ salvando ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import {
  BarChart3,
  CheckCircle2,
  CircleDollarSign,
  Clock3,
  Plus,
  Wallet,
} from '@lucide/vue'
import api from '@/api/client'
import { useToast } from '@/composables/useToast'

defineOptions({ name: 'FinanceiroView' })

const { sucesso: toastSucesso, erro: toastErro } = useToast()

const secoes = [
  {
    id: 'contas-pagar',
    label: 'Contas a pagar',
    descricao: 'Controle de despesas e custos operacionais',
    emBreve: false,
  },
  {
    id: 'contas-receber',
    label: 'Contas a receber',
    descricao: 'Recebimentos — disponível quando pagamentos estiverem prontos',
    emBreve: true,
  },
]

const secao = ref(typeof window !== 'undefined' && window.innerWidth >= 1024 ? 'contas-pagar' : null)

function mesAtual() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const mes = ref(mesAtual())
const loading = ref(false)
const importando = ref(false)
const despesas = ref([])
const resumo = ref(null)
const categorias = ref([])
const filtroStatus = ref('')
const filtroCategoria = ref('')
const statusSaving = reactive({})
const menuAberto = ref(false)
const menuRef = ref(null)

const modalAberto = ref(false)
const editando = ref(null)
const salvando = ref(false)
const erroForm = ref('')
const form = ref(formVazio())

const modalTipoAberto = ref(false)
const salvandoTipo = ref(false)
const erroTipo = ref('')
const formTipo = ref({ nome: '' })

function primeiroDiaMesAtual() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`
}

function formVazio() {
  return {
    data_pagamento: new Date().toISOString().slice(0, 10),
    data_vencimento: new Date().toISOString().slice(0, 10),
    descricao: '',
    categoria_id: '',
    valor: '',
    pago: false,
    recorrencia: 'avulsa',
    vigencia_inicio: primeiroDiaMesAtual(),
    vigencia_fim: '',
  }
}

function rowKey(d) {
  return `${d.id}-${d.competencia || 'avulsa'}`
}

function labelRecorrencia(d) {
  if (d.recorrencia === 'mensal') return 'Recorrente · todo mês'
  if (d.recorrencia === 'temporaria') {
    return `Temporário · ${formatDate(d.vigencia_inicio)} a ${formatDate(d.vigencia_fim)}`
  }
  return 'Único'
}

function formatCurrency(v) {
  if (v == null || v === '') return 'R$ 0,00'
  return Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

function formatDate(iso) {
  if (!iso) return '—'
  const [y, m, d] = String(iso).slice(0, 10).split('-')
  return `${d}/${m}/${y}`
}

function hojeISO() {
  return new Date().toISOString().slice(0, 10)
}

/** Pendente com vencimento anterior a hoje → em atraso */
function estaEmAtraso(d) {
  if (!d?.data_vencimento || d.status === 'pago') return false
  return String(d.data_vencimento).slice(0, 10) < hojeISO()
}

function onCategoriaChange() {
  const cat = categorias.value.find((c) => c.id === Number(form.value.categoria_id))
  if (cat && cat.nome.trim().toLowerCase() === 'custos fixos' && form.value.recorrencia === 'avulsa') {
    form.value.recorrencia = 'mensal'
    if (!form.value.vigencia_inicio) form.value.vigencia_inicio = primeiroDiaMesAtual()
  }
}

function onClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    menuAberto.value = false
  }
}

async function carregarCategorias() {
  const { data } = await api.get('/financeiro/categorias-despesa')
  categorias.value = data
}

/** Atualiza KPIs sem nova request (pago ↔ pendente). */
function aplicarDeltaStatusResumo(valor, deStatus, paraStatus) {
  if (!resumo.value || deStatus === paraStatus) return
  const v = Number(valor || 0)
  if (deStatus === 'pago') resumo.value.total_pago = Number(resumo.value.total_pago) - v
  if (deStatus === 'pendente') resumo.value.total_pendente = Number(resumo.value.total_pendente) - v
  if (paraStatus === 'pago') resumo.value.total_pago = Number(resumo.value.total_pago) + v
  if (paraStatus === 'pendente') resumo.value.total_pendente = Number(resumo.value.total_pendente) + v
}

function aplicarDeltaItemResumo(valor, status, sinal) {
  if (!resumo.value) return
  const v = Number(valor || 0) * sinal
  resumo.value.total = Number(resumo.value.total || 0) + v
  resumo.value.quantidade = Number(resumo.value.quantidade || 0) + sinal
  if (status === 'pago') resumo.value.total_pago = Number(resumo.value.total_pago || 0) + v
  else resumo.value.total_pendente = Number(resumo.value.total_pendente || 0) + v
}

function passaFiltrosLista(row) {
  if (filtroStatus.value && row.status !== filtroStatus.value) return false
  if (filtroCategoria.value && Number(row.categoria_id) !== Number(filtroCategoria.value)) return false
  return true
}

function vencimentoNoMes(dataVenc, competencia) {
  if (!dataVenc || !competencia) return dataVenc || null
  const day = Number(String(dataVenc).slice(8, 10))
  const [y, m] = competencia.split('-').map(Number)
  const last = new Date(y, m, 0).getDate()
  return `${competencia}-${String(Math.min(day, last)).padStart(2, '0')}`
}

function normalizarLinhaResposta(data, anterior = null) {
  const cat = categorias.value.find((c) => c.id === Number(data.categoria_id))
  const row = {
    ...data,
    categoria_nome: data.categoria_nome || cat?.nome || anterior?.categoria_nome || '—',
  }
  // Recorrente: resposta do PATCH não traz ocorrência do mês — preserva contexto da linha
  if (row.recorrencia !== 'avulsa') {
    const competencia = anterior?.competencia || data.competencia || mes.value
    row.competencia = competencia
    row.ocorrencia_id = data.ocorrencia_id ?? anterior?.ocorrencia_id ?? null
    if (anterior) {
      row.status = anterior.status
      row.data_pagamento = anterior.data_pagamento
    } else if (!row.status) {
      row.status = 'pendente'
    }
    row.data_vencimento = vencimentoNoMes(data.data_vencimento || anterior?.data_vencimento, competencia)
  }
  return row
}

function upsertDespesaLocal(row, anterior = null) {
  const key = anterior ? rowKey(anterior) : rowKey(row)
  const idx = despesas.value.findIndex((d) => rowKey(d) === key)
  if (passaFiltrosLista(row)) {
    if (idx >= 0) despesas.value[idx] = row
    else despesas.value.unshift(row)
  } else if (idx >= 0) {
    despesas.value.splice(idx, 1)
  }
}

async function carregar() {
  loading.value = true
  try {
    const params = { mes: mes.value || undefined }
    if (filtroStatus.value) params.status = filtroStatus.value
    if (filtroCategoria.value) params.categoria_id = Number(filtroCategoria.value)
    const { data } = await api.get('/financeiro/despesas/painel', { params })
    despesas.value = data.despesas
    // Com filtro ativo o backend já devolve KPIs do mês completo
    resumo.value = data.resumo
  } catch (e) {
    toastErro(e.response?.data?.detail || 'Erro ao carregar financeiro.')
  } finally {
    loading.value = false
  }
}

async function carregarDespesas() {
  await carregar()
}

async function toggleStatus(despesa, event) {
  const key = rowKey(despesa)
  const novoStatus = event.target.checked ? 'pago' : 'pendente'
  const anterior = despesa.status
  const dataAnterior = despesa.data_pagamento
  despesa.status = novoStatus
  if (novoStatus === 'pendente') despesa.data_pagamento = null
  else if (!despesa.data_pagamento) {
    despesa.data_pagamento = new Date().toISOString().slice(0, 10)
  }
  aplicarDeltaStatusResumo(despesa.valor, anterior, novoStatus)
  statusSaving[key] = true
  try {
    const { data } = await api.patch(`/financeiro/despesas/${despesa.id}/status`, {
      status: novoStatus,
      data_pagamento: novoStatus === 'pago' ? despesa.data_pagamento : null,
      mes: despesa.recorrencia !== 'avulsa' ? (despesa.competencia || mes.value) : null,
    })
    despesa.data_pagamento = data.data_pagamento
    despesa.ocorrencia_id = data.ocorrencia_id
  } catch (e) {
    despesa.status = anterior
    despesa.data_pagamento = dataAnterior
    event.target.checked = anterior === 'pago'
    aplicarDeltaStatusResumo(despesa.valor, novoStatus, anterior)
    toastErro(e.response?.data?.detail || 'Não foi possível atualizar o status.')
  } finally {
    statusSaving[key] = false
  }
}

function abrirModalNovo() {
  editando.value = null
  form.value = formVazio()
  erroForm.value = ''
  modalAberto.value = true
}

function abrirModalTipo() {
  formTipo.value = { nome: '' }
  erroTipo.value = ''
  modalTipoAberto.value = true
}

async function salvarTipo() {
  erroTipo.value = ''
  const nome = formTipo.value.nome.trim()
  if (!nome) {
    erroTipo.value = 'Informe o nome do tipo.'
    return
  }
  salvandoTipo.value = true
  try {
    const { data } = await api.post('/financeiro/categorias-despesa', { nome })
    toastSucesso('Tipo de despesa criado.')
    await carregarCategorias()
    form.value.categoria_id = data.id
    modalTipoAberto.value = false
  } catch (e) {
    const detail = e.response?.data?.detail
    erroTipo.value = typeof detail === 'string' ? detail : 'Erro ao criar tipo.'
  } finally {
    salvandoTipo.value = false
  }
}

function abrirModalEditar(d) {
  editando.value = d
  form.value = {
    data_pagamento: d.data_pagamento ? String(d.data_pagamento).slice(0, 10) : new Date().toISOString().slice(0, 10),
    data_vencimento: d.data_vencimento
      ? String(d.data_vencimento).slice(0, 10)
      : new Date().toISOString().slice(0, 10),
    descricao: d.descricao,
    categoria_id: d.categoria_id,
    valor: Number(d.valor),
    pago: d.status === 'pago',
    recorrencia: d.recorrencia || 'avulsa',
    vigencia_inicio: d.vigencia_inicio
      ? String(d.vigencia_inicio).slice(0, 10)
      : primeiroDiaMesAtual(),
    vigencia_fim: d.vigencia_fim ? String(d.vigencia_fim).slice(0, 10) : '',
  }
  erroForm.value = ''
  modalAberto.value = true
}

async function salvar() {
  erroForm.value = ''
  if (form.value.recorrencia === 'mensal' || form.value.recorrencia === 'temporaria') {
    if (!form.value.data_vencimento) {
      erroForm.value = 'Informe a data de vencimento.'
      return
    }
  }
  if (form.value.recorrencia === 'temporaria') {
    if (!form.value.vigencia_inicio || !form.value.vigencia_fim) {
      erroForm.value = 'Informe início e fim do custo temporário.'
      return
    }
    if (form.value.vigencia_fim < form.value.vigencia_inicio) {
      erroForm.value = 'A data fim deve ser maior ou igual à data início.'
      return
    }
  }
  if (form.value.pago && !form.value.data_pagamento) {
    erroForm.value = 'Informe a data do pagamento.'
    return
  }
  salvando.value = true
  const payload = {
    data_pagamento: form.value.pago ? form.value.data_pagamento : null,
    data_vencimento:
      form.value.recorrencia === 'avulsa' ? null : (form.value.data_vencimento || null),
    descricao: form.value.descricao,
    categoria_id: Number(form.value.categoria_id),
    valor: Number(form.value.valor),
    status: form.value.pago ? 'pago' : 'pendente',
    recorrencia: form.value.recorrencia,
    vigencia_inicio:
      form.value.recorrencia === 'avulsa' ? null : (form.value.vigencia_inicio || null),
    vigencia_fim:
      form.value.recorrencia === 'temporaria' ? (form.value.vigencia_fim || null) : null,
  }
  try {
    if (editando.value) {
      const anterior = editando.value
      const { data } = await api.patch(`/financeiro/despesas/${anterior.id}`, payload)
      const row = normalizarLinhaResposta(data, anterior)
      // Ajuste de KPI: remove antigo, adiciona novo (só se ambos no mês atual)
      aplicarDeltaItemResumo(anterior.valor, anterior.status, -1)
      aplicarDeltaItemResumo(row.valor, row.status, +1)
      upsertDespesaLocal(row, anterior)
      toastSucesso('Despesa atualizada.')
    } else {
      const { data } = await api.post('/financeiro/despesas', payload)
      const row = normalizarLinhaResposta(data)
      aplicarDeltaItemResumo(row.valor, row.status, +1)
      upsertDespesaLocal(row)
      toastSucesso('Despesa criada.')
    }
    modalAberto.value = false
  } catch (e) {
    const detail = e.response?.data?.detail
    erroForm.value = typeof detail === 'string' ? detail : (detail?.[0]?.msg || 'Erro ao salvar.')
  } finally {
    salvando.value = false
  }
}

async function confirmarExclusao(d) {
  const msg = d.recorrencia !== 'avulsa'
    ? `Excluir "${d.descricao}"? Isso remove o custo de todos os meses.`
    : `Excluir "${d.descricao}"?`
  if (!confirm(msg)) return
  try {
    await api.delete(`/financeiro/despesas/${d.id}`)
    const key = rowKey(d)
    const idx = despesas.value.findIndex((x) => rowKey(x) === key)
    if (idx >= 0) despesas.value.splice(idx, 1)
    // Remove todas as linhas do mesmo template recorrente na lista atual
    if (d.recorrencia !== 'avulsa') {
      despesas.value = despesas.value.filter((x) => x.id !== d.id)
    }
    aplicarDeltaItemResumo(d.valor, d.status, -1)
    toastSucesso('Despesa excluída.')
  } catch (e) {
    toastErro(e.response?.data?.detail || 'Erro ao excluir.')
  }
}

async function onImportFile(event) {
  const file = event.target.files?.[0]
  event.target.value = ''
  menuAberto.value = false
  if (!file) return
  importando.value = true
  try {
    const body = new FormData()
    body.append('arquivo', file)
    const { data } = await api.post('/financeiro/despesas/importar', body, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    toastSucesso(`Importação: ${data.inseridas} inseridas, ${data.ignoradas_duplicadas} duplicadas ignoradas.`)
    if (data.erros?.length) toastErro(`${data.erros.length} linha(s) com problema.`)
    await carregar()
  } catch (e) {
    toastErro(e.response?.data?.detail || 'Falha na importação.')
  } finally {
    importando.value = false
  }
}

watch(secao, (val) => {
  if (val === 'contas-pagar' && !categorias.value.length) {
    carregarCategorias().then(carregar).catch(() => {})
  } else if (val === 'contas-pagar') {
    carregar()
  }
})

onMounted(async () => {
  document.addEventListener('click', onClickOutside)
  if (secao.value === 'contas-pagar') {
    try {
      await carregarCategorias()
      await carregar()
    } catch (e) {
      toastErro(e.response?.data?.detail || 'Erro ao carregar financeiro.')
    }
  }
})

onUnmounted(() => {
  document.removeEventListener('click', onClickOutside)
})
</script>
