<template>
  <div class="flex flex-col h-full">

    <!-- Header -->
    <!-- Header compacto: busca + menu de ações unificado + botão Novo -->
    <div class="flex items-center justify-between mb-3 flex-shrink-0 gap-2">
      <h2 class="text-xl font-bold text-gray-800 shrink-0">Agendamentos</h2>
      <div class="flex items-center gap-2">

        <!-- Busca por cliente (sempre visível) -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/>
          </svg>
          <input
            v-model="buscaCalendario"
            type="search"
            placeholder="Buscar..."
            class="border border-gray-200 text-gray-600 text-sm pl-9 pr-8 py-2 rounded-lg w-36 h-11 focus:outline-none focus:ring-2 focus:ring-rose-300"
          />
          <button
            v-if="buscaCalendario"
            @click="buscaCalendario = ''"
            class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 w-6 h-6 flex items-center justify-center text-base leading-none"
            aria-label="Limpar busca"
          >×</button>
        </div>

        <!-- Menu de ações (apenas mobile) -->
        <div v-if="isMobile" class="relative">
          <button
            @click="showMobileMenu = !showMobileMenu"
            :class="[
              'w-11 h-11 flex items-center justify-center border rounded-lg transition-colors',
              showMobileMenu
                ? 'bg-gray-100 border-gray-300 text-gray-800'
                : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            ]"
            aria-label="Mais ações"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="5" r="1" fill="currentColor" stroke="none"/>
              <circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/>
              <circle cx="12" cy="19" r="1" fill="currentColor" stroke="none"/>
            </svg>
          </button>
          <div v-if="showMobileMenu" class="fixed inset-0 z-10" @click="showMobileMenu = false"></div>
          <div
            v-if="showMobileMenu"
            class="absolute right-0 top-full mt-1 bg-white border border-gray-100 rounded-2xl shadow-2xl z-20 min-w-[220px] py-1.5 overflow-hidden"
          >
            <button
              class="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-rose-50 active:bg-rose-100 flex items-center gap-3"
              @click="showClientesPanel = true; showMobileMenu = false"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <span>Clientes</span>
            </button>

            <div class="h-px bg-gray-100 mx-3 my-1"></div>

            <button
              class="w-full text-left px-4 py-3 text-sm flex items-center gap-3"
              :class="filtroPendentesProximos ? 'text-amber-700 bg-amber-50/60 font-medium' : 'text-gray-600 hover:bg-gray-50'"
              @click="filtroPendentesProximos = !filtroPendentesProximos; showMobileMenu = false"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" :class="filtroPendentesProximos ? 'text-amber-500' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              <span class="flex-1">Pendentes próximos</span>
              <span v-if="agendamentosPendentesProximos.length" class="bg-amber-100 text-amber-700 text-xs font-bold px-1.5 py-0.5 rounded-full">{{ agendamentosPendentesProximos.length }}</span>
              <svg v-if="filtroPendentesProximos" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-amber-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
            </button>

            <button
              class="w-full text-left px-4 py-3 text-sm flex items-center gap-3"
              :class="mostrarTarefas ? 'text-indigo-700 bg-indigo-50/60 font-medium' : 'text-gray-600 hover:bg-gray-50'"
              @click="mostrarTarefas = !mostrarTarefas; showMobileMenu = false"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" :class="mostrarTarefas ? 'text-indigo-500' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
              <span class="flex-1">Tarefas no calendário</span>
              <svg v-if="mostrarTarefas" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-indigo-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
            </button>

            <template v-if="isRecepcionistaOuAdmin">
              <div class="h-px bg-gray-100 mx-3 my-1"></div>
              <button
                class="w-full text-left px-4 py-3 text-sm flex items-center gap-3"
                :class="colunaPorProfissional ? 'text-rose-700 bg-rose-50/60 font-medium' : 'text-gray-600 hover:bg-gray-50'"
                @click="toggleColunaPorProfissional(); showMobileMenu = false"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" :class="colunaPorProfissional ? 'text-rose-500' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="18" rx="1"/><rect x="14" y="3" width="7" height="18" rx="1"/></svg>
                <span class="flex-1">Visão Diária</span>
                <svg v-if="colunaPorProfissional" xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 text-rose-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              </button>
              <div class="px-3 pb-2.5 pt-1">
                <select
                  v-model="filtroProfissional"
                  class="w-full border border-gray-200 text-gray-600 text-sm px-3 py-2.5 rounded-xl focus:outline-none focus:ring-2 focus:ring-rose-300"
                >
                  <option :value="null">Todos os profissionais</option>
                  <option v-for="p in profissionais" :key="p.id" :value="p.id">{{ p.nome }}</option>
                </select>
              </div>
            </template>
          </div>
        </div>

        <!-- Ações em botões diretos (desktop) -->
        <div v-else class="flex items-center gap-2">
          <button
            class="h-11 px-3 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50"
            @click="showClientesPanel = true"
          >Clientes</button>

          <button
            class="h-11 px-3 border rounded-lg text-sm flex items-center gap-1.5"
            :class="filtroPendentesProximos ? 'border-amber-300 bg-amber-50 text-amber-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
            @click="filtroPendentesProximos = !filtroPendentesProximos"
          >
            Pendentes próximos
            <span v-if="agendamentosPendentesProximos.length" class="bg-amber-100 text-amber-700 text-xs font-bold px-1.5 py-0.5 rounded-full">{{ agendamentosPendentesProximos.length }}</span>
          </button>

          <button
            class="h-11 px-3 border rounded-lg text-sm"
            :class="mostrarTarefas ? 'border-indigo-300 bg-indigo-50 text-indigo-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
            @click="mostrarTarefas = !mostrarTarefas"
          >Tarefas no calendário</button>

          <template v-if="isRecepcionistaOuAdmin">
            <button
              class="h-11 px-3 border rounded-lg text-sm"
              :class="colunaPorProfissional ? 'border-rose-300 bg-rose-50 text-rose-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'"
              @click="toggleColunaPorProfissional()"
            >Visão Diária</button>
            <select
              v-model="filtroProfissional"
              class="h-11 min-w-[220px] border border-gray-200 text-gray-600 text-sm px-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-rose-300"
            >
              <option :value="null">Todos os profissionais</option>
              <option v-for="p in profissionais" :key="p.id" :value="p.id">{{ p.nome }}</option>
            </select>
          </template>
        </div>

        <!-- Botão principal: sempre visível com touch target mínimo de 44px -->
        <div class="relative">
          <button
            class="bg-rose-600 text-white text-sm font-semibold px-4 h-11 rounded-lg hover:bg-rose-700 transition-colors whitespace-nowrap flex items-center gap-1"
            @click="showNovoMenu = !showNovoMenu"
          >
            + Novo <ChevronDown class="w-3.5 h-3.5 opacity-75" />
          </button>
          <div v-if="showNovoMenu" class="fixed inset-0 z-10" @click="showNovoMenu = false"></div>
          <div
            v-if="showNovoMenu"
            class="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg z-20 min-w-[200px] p-1.5"
          >
            <button
              class="w-full text-left flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-rose-50 hover:text-rose-600 transition-colors"
              @click="abrirModalNovo(); showNovoMenu = false"
            >
              <Calendar class="w-4 h-4 flex-shrink-0" />
              Novo Agendamento
            </button>
            <button
              class="w-full text-left flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:bg-rose-50 hover:text-rose-600 transition-colors"
              @click="abrirModalTarefa(); showNovoMenu = false"
            >
              <ClipboardList class="w-4 h-4 flex-shrink-0" />
              Nova Tarefa
            </button>
          </div>
        </div>

      </div>
    </div>

    <!-- PAINEL: Pendentes Próximos (próximos 4 dias úteis não confirmados) -->
    <div v-if="filtroPendentesProximos" class="flex-shrink-0 bg-amber-50 border border-amber-200 rounded-xl mb-3 overflow-hidden">
      <div class="flex items-center justify-between px-4 py-3 border-b border-amber-200">
        <div class="flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <span class="text-sm font-semibold text-amber-800">Pendentes não confirmados — próximos 4 dias úteis</span>
          <span class="bg-amber-200 text-amber-900 text-xs font-bold px-2 py-0.5 rounded-full">{{ agendamentosPendentesProximos.length }}</span>
        </div>
        <button @click="filtroPendentesProximos = false" class="text-amber-500 hover:text-amber-700 text-lg leading-none">×</button>
      </div>
      <div v-if="agendamentosPendentesProximos.length === 0" class="px-4 py-5 text-sm text-amber-700 italic text-center">
        Nenhum agendamento pendente nos próximos 4 dias úteis. 🎉
      </div>
      <div v-else class="divide-y divide-amber-100 max-h-72 overflow-y-auto">
        <div
          v-for="ag in agendamentosPendentesProximos"
          :key="ag.id"
          class="flex items-start justify-between gap-3 px-4 py-3 hover:bg-amber-100/60 transition-colors"
        >
          <!-- Info -->
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-sm font-semibold text-gray-800">{{ ag.cliente?.nome || '—' }}</span>
              <span v-if="ag.cliente?.telefone" class="text-xs text-gray-500">{{ ag.cliente.telefone }}</span>
            </div>
            <div class="mt-0.5 space-y-0.5">
              <div v-for="item in ag.itens" :key="item.id" class="text-xs text-gray-600">
                <span class="font-medium">{{ item.servico?.nome }}</span>
                <span class="text-gray-400"> · {{ item.profissional?.nome }}</span>
                <span class="text-gray-500"> · {{ formatDate(item.data_hora_inicio) }}</span>
              </div>
            </div>
          </div>
          <!-- Ações -->
          <div class="flex items-center gap-1.5 flex-shrink-0">
            <button
              class="text-xs px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium transition-colors"
              @click="alterarStatus(ag.id, 'confirmado'); ag.status = 'confirmado'"
            >Confirmar</button>
            <button
              class="text-xs px-3 py-1.5 border border-gray-200 text-gray-600 rounded-lg hover:bg-white font-medium transition-colors"
              @click="detalheAg = ag"
            >Ver</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Calendário FullCalendar (visão padrão) -->
    <div v-if="!colunaPorProfissional" class="flex-1 bg-white border border-gray-200 rounded-xl overflow-hidden fc-wrapper">
      <!--
        :key="isMobile ? 'fc-m' : 'fc-d'" — padrão avançado de Vue.
        FullCalendar tem estado interno (view atual, scroll position) que
        não é controlado por props. Mudar o key força o Vue a destruir o
        componente antigo e criar um novo, aplicando a initialView correta.
        Isso é mais limpo do que manipular a API imperativa do FullCalendar.
      -->
      <FullCalendar v-if="!loading" :key="isMobile ? 'fc-m' : 'fc-d'" :options="calendarOptions" />
      <div v-else class="p-10 text-center text-sm text-gray-400">Carregando...</div>
    </div>

    <!-- Visão diária por colunas (sem plugin premium) -->
    <div v-else class="flex-1 bg-white border border-gray-200 rounded-xl overflow-auto">
      <!-- Seletor de data para a visão em colunas -->
      <div class="flex items-center gap-3 px-4 py-3 border-b border-gray-100">
        <!-- Touch targets mínimos: w-11 h-11 = 44x44px (Apple HIG / Material Design) -->
        <button class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-lg text-xl transition-colors" @click="colunaDia = prevDay(colunaDia)" aria-label="Dia anterior">‹</button>
        <input v-model="colunaDia" type="date" class="border border-gray-200 rounded-lg px-3 py-2 h-11 text-sm focus:outline-none focus:ring-2 focus:ring-rose-300" />
        <button class="w-11 h-11 flex items-center justify-center text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-lg text-xl transition-colors" @click="colunaDia = nextDay(colunaDia)" aria-label="Próximo dia">›</button>
        <span class="text-sm text-gray-500 ml-1">{{ formatDayLabel(colunaDia) }}</span>
      </div>
      <!-- Grid de colunas -->
      <div class="overflow-x-auto">
        <div class="flex min-w-max">
          <!-- Hora axis -->
          <div class="w-14 flex-shrink-0">
            <div class="h-10 border-b border-gray-100"></div>
            <div v-for="h in colunaSlots" :key="h" class="h-14 border-b border-gray-100 flex items-start px-2 pt-1">
              <span class="text-xs text-gray-400">{{ h }}</span>
            </div>
          </div>
          <!-- One column per profissional -->
          <div
            v-for="prof in profissionaisColuna"
            :key="prof.id"
            class="flex-1 min-w-[140px] border-l border-gray-100"
          >
            <div class="h-10 border-b border-gray-100 flex items-center justify-center px-2">
              <span class="text-xs font-semibold text-gray-700 truncate">{{ prof.nome }}</span>
            </div>
            <div class="relative">
              <div
                v-for="h in colunaSlots"
                :key="h"
                class="h-14 border-b border-gray-100 cursor-pointer hover:bg-rose-50/50 transition-colors"
                @click="colunaSlotClick(prof.id, h)"
              ></div>
              <!-- Events -->
              <div
                v-for="ev in colunaEventosDoProfissional(prof.id)"
                :key="ev.id"
                class="absolute left-1 right-1 rounded-md px-1.5 py-0.5 text-xs cursor-pointer overflow-hidden"
                :style="colunaEventoStyle(ev)"
                :title="`Status: ${STATUS_LABELS[ev.ag?.status] || ev.ag?.status || 'Sem status'}`"
                @click="detalheAg = ev.ag"
              >
                <div class="font-semibold truncate" :style="{ color: ev.color.text }">{{ ev.clienteNome }}</div>
                <div class="truncate opacity-75" :style="{ color: ev.color.text }">{{ ev.servNome }}</div>
              </div>
            </div>
          </div>
          <!-- Coluna de tarefas internas: respeita o toggle mostrarTarefas -->
          <div v-if="mostrarTarefas" class="flex-1 min-w-[160px] border-l border-indigo-100">
            <div class="h-10 border-b border-gray-100 flex items-center justify-center px-2 bg-indigo-50/40">
              <span class="text-xs font-semibold text-indigo-700">Tarefas</span>
            </div>
            <div class="relative">
              <div
                v-for="h in colunaSlots"
                :key="h"
                class="h-14 border-b border-gray-100 cursor-pointer hover:bg-indigo-50/50 transition-colors"
                @click="abrirModalTarefa(colunaDia + 'T' + h)"
              ></div>
              <div
                v-for="t in colunaTarefasDoDia"
                :key="t.id"
                class="absolute left-1 right-1 rounded-md px-1.5 py-0.5 text-xs cursor-pointer overflow-hidden"
                :style="colunaTarefaStyle(t)"
                @click.stop="detalheTarefa = t"
              >
                <div class="font-semibold truncate" :class="t.concluida ? 'text-gray-500 line-through' : 'text-indigo-800'">{{ t.titulo }}</div>
                <div v-if="t.concluida" class="text-gray-400 text-xs">✓ Concluída</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL: Novo / Editar Agendamento -->
    <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-gray-800 mb-4">
          {{ modalMode === 'edit' ? `Editar Agendamento #${formData.id}` : 'Novo Agendamento' }}
        </h3>
        <form @submit.prevent="salvarModal" class="space-y-4">
          <div>
            <div class="flex items-center justify-between mb-1">
              <label class="block text-sm font-medium text-gray-700">Cliente *</label>
              <button type="button" class="text-xs text-rose-600 font-medium hover:underline" @click="abrirModalClienteRapido">+ Novo cliente</button>
            </div>
            <div class="relative">
              <input
                v-model="clienteBuscaNome"
                type="text"
                placeholder="Buscar cliente..."
                autocomplete="off"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"
                @input="showBuscaDropdown = true; formData.cliente_id = ''"
                @focus="showBuscaDropdown = true"
                @blur="setTimeout(() => showBuscaDropdown = false, 150)"
              />
              <ul v-if="showBuscaDropdown && clientesBuscaFiltrados.length" class="absolute z-50 w-full bg-white border border-gray-200 rounded-lg shadow-lg mt-1 max-h-48 overflow-y-auto">
                <li
                  v-for="c in clientesBuscaFiltrados"
                  :key="c.id"
                  class="px-3 py-2 text-sm cursor-pointer hover:bg-rose-50 hover:text-rose-700"
                  @mousedown.prevent="selectCliente(c)"
                >{{ c.nome }}</li>
              </ul>
            </div>
          </div>
          <div>
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">Serviços *</label>
              <button type="button" class="text-xs text-rose-600 font-medium hover:underline" @click="addItem">+ Adicionar</button>
            </div>
            <div v-for="(item, idx) in formData.itens" :key="idx" class="border border-gray-200 rounded-lg p-3 mb-2 space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-gray-500">Serviço {{ idx + 1 }}</span>
                <button v-if="formData.itens.length > 1" type="button" class="text-xs text-red-400 hover:text-red-600" @click="removeItem(idx)">Remover</button>
              </div>
              <div>
                <label class="block text-xs text-gray-600 mb-1">Serviço</label>
                <select v-model="item.servico_id" required class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" @change="onServicoChange(item, idx)">
                  <option value="">Selecione...</option>
                  <option v-for="s in servicos" :key="s.id" :value="s.id">{{ s.nome }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-600 mb-1">Profissional</label>
                <select v-model="item.profissional_id" required class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" @change="onProfissionalChange(item, idx)">
                  <option value="">Selecione...</option>
                  <option v-for="p in profissionaisParaItem(item)" :key="p.id" :value="p.id">{{ p.nome }}</option>
                </select>
                <p v-if="item.servico_id && profissionaisParaItem(item).length === 0" class="text-xs text-amber-600 mt-1">Nenhum profissional habilitado para este serviço.</p>
                <p v-if="conflictosPorItem[idx]" class="text-xs text-red-500 mt-1 font-medium">⚠ {{ conflictosPorItem[idx] }}</p>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label class="block text-xs text-gray-600 mb-1">Início *</label>
                  <input v-model="item.data_hora_inicio" type="datetime-local" required class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" @change="onInicioChange(item, idx)" />
                </div>
                <div>
                  <label class="block text-xs text-gray-600 mb-1">Fim</label>
                  <input v-model="item.data_hora_fim" type="datetime-local" class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
                </div>
              </div>
              <!-- Sugestão de horários disponíveis -->
              <div v-if="item.servico_id && item.profissional_id && formData.cliente_id">
                <div class="flex items-center gap-2 mt-1.5">
                  <button type="button" @click="abrirSugestoes(idx)" class="text-xs text-rose-600 font-medium hover:underline flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" d="M12 6v6l4 2"/></svg>
                    {{ sugestaoItemIdx === idx ? 'Fechar sugestões' : 'Ver horários livres' }}
                  </button>
                  <input v-if="sugestaoItemIdx === idx" v-model="sugestaoData" type="date" class="border border-gray-200 rounded-md px-2 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-rose-300" />
                </div>
                <div v-if="sugestaoItemIdx === idx" class="mt-2">
                  <p v-if="slotsDisponiveis.length === 0" class="text-xs text-gray-400 italic">Nenhum horário livre neste dia para este profissional e cliente.</p>
                  <div v-else class="flex flex-wrap gap-1.5">
                    <button
                      v-for="slot in slotsDisponiveis"
                      :key="slot"
                      type="button"
                      class="text-xs px-2.5 py-1 bg-rose-50 text-rose-700 rounded-full border border-rose-200 hover:bg-rose-100 font-medium transition-colors"
                      @click="aplicarSugestao(slot)"
                    >{{ slot }}</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Observações</label>
            <textarea v-model="formData.observacoes" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400"></textarea>
          </div>
          <p v-if="modalError" class="text-sm text-red-500">{{ modalError }}</p>
          <div class="flex gap-2 pt-2">
            <button type="button" class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-3 text-sm hover:bg-gray-50" @click="showModal = false">Cancelar</button>
            <button type="submit" :disabled="saving" class="flex-1 bg-rose-600 text-white rounded-lg py-3 text-sm font-semibold hover:bg-rose-700 disabled:opacity-50">
              {{ saving ? 'Salvando...' : (modalMode === 'edit' ? 'Salvar' : 'Criar') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- PAINEL LATERAL: Detalhe do Agendamento + Cliente -->
    <!--
      ARQUITETURA DE LAYOUT RESPONSIVO:
      Desktop: slide-in da direita (items-stretch justify-end), dois painéis side-by-side.
      Mobile:  bottom sheet (items-end justify-center), sobe de baixo com bordas arredondadas
               no topo. Os dois painéis viram tabs — o usuário alterna entre "Serviços" e
               "Cliente" ao invés de ver ambos espremidos.

      Para as tabs usamos :class condicional em vez de v-if/v-else porque:
      - Os dados já estão em memória (sem custo de fetch ao trocar de aba)
      - v-if desmontaria/remontaria o DOM a cada clique na tab (animações, scroll resetam)
      - hidden + :class é mais performático para alternância frequente
    -->
    <div v-if="detalheAg" class="fixed inset-0 bg-black/40 z-50 flex sm:items-stretch sm:justify-end items-end justify-center" @click.self="detalheAg = null">
      <div class="bg-white w-full sm:max-w-2xl flex flex-col shadow-2xl sm:rounded-none rounded-t-3xl max-h-[92vh] sm:max-h-none sm:h-full">
        <!-- Drag handle (mobile only) — sinal visual de que o painel é deslizável -->
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>

        <!-- Header -->
        <div class="flex items-start justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <span :class="statusBadgeClass(detalheAg.status)" class="text-xs font-semibold px-2.5 py-0.5 rounded-full">{{ detalheAg.status }}</span>
              <span class="text-xs text-gray-400">#{{ detalheAg.id }} · Criado {{ formatDateShort(detalheAg.criado_em) }}</span>
            </div>
            <h3 class="text-lg font-bold text-gray-800 mt-1">{{ detalheAg.cliente?.nome || '—' }}</h3>
          </div>
          <button @click="detalheAg = null" class="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-600 flex-shrink-0" aria-label="Fechar">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Tabs de navegação (mobile only) -->
        <div class="sm:hidden flex border-b border-gray-100 flex-shrink-0">
          <button
            @click="detalheTab = 'servicos'"
            :class="detalheTab === 'servicos' ? 'border-b-2 border-rose-600 text-rose-700 font-semibold' : 'text-gray-500'"
            class="flex-1 py-3 text-sm transition-colors"
          >Serviços</button>
          <button
            @click="detalheTab = 'cliente'"
            :class="detalheTab === 'cliente' ? 'border-b-2 border-rose-600 text-rose-700 font-semibold' : 'text-gray-500'"
            class="flex-1 py-3 text-sm transition-colors"
          >Cliente</button>
        </div>

        <!-- Body -->
        <div class="flex flex-1 overflow-hidden">
          <!-- Esquerda: detalhes do agendamento -->
          <!-- sm:block garante visibilidade no desktop. No mobile, controla a tab ativa. -->
          <div :class="['flex-1 overflow-y-auto p-5 border-r border-gray-100 min-w-0', isMobile && detalheTab !== 'servicos' ? 'hidden' : '']">
            <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Serviços</h4>
            <div class="space-y-2 mb-5">
              <div v-for="item in detalheAg.itens" :key="item.id" class="bg-gray-50 rounded-xl px-4 py-3 border border-gray-100">
                <div class="flex items-center gap-2 mb-0.5">
                  <span class="text-sm font-semibold text-gray-800">{{ item.servico?.nome }}</span>
                </div>
                <div class="text-xs text-gray-500">{{ item.profissional?.nome }}</div>
                <div class="text-xs text-gray-400 mt-0.5">{{ formatDate(item.data_hora_inicio) }}<span v-if="item.data_hora_fim"> → {{ formatHoraCliente(item.data_hora_fim) }}</span></div>
              </div>
            </div>

            <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Status</h4>
            <select
              :value="detalheAg.status"
              class="border border-gray-200 rounded-lg px-3 py-2 text-sm w-full mb-5 h-11 focus:outline-none focus:ring-2 focus:ring-rose-300"
              @change="alterarStatus(detalheAg.id, $event.target.value); detalheAg.status = $event.target.value"
            >
              <option value="pendente">Pendente</option>
              <option value="confirmado">Confirmado</option>
              <option value="concluido">Concluído</option>
              <option value="cancelado">Cancelado</option>
            </select>

            <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Cor do Agendamento</h4>
            <div class="mb-5 space-y-2.5">
              <div class="flex items-center gap-2">
                <input
                  v-model="detalheCorSelecionada"
                  type="color"
                  class="w-14 h-11 border border-gray-200 rounded-lg p-1 cursor-pointer"
                />
                <input
                  v-model="detalheCorSelecionada"
                  type="text"
                  class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm h-11 uppercase"
                  placeholder="#E5E7EB"
                />
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click="salvarCorAgendamento"
                  class="flex-1 bg-gray-800 text-white rounded-lg py-2.5 text-sm font-semibold hover:bg-gray-900 transition-colors"
                >Salvar cor</button>
                <button
                  @click="salvarCorFavorita"
                  class="flex-1 border border-gray-200 text-gray-700 rounded-lg py-2.5 text-sm font-semibold hover:bg-gray-50 transition-colors"
                >Salvar na paleta</button>
              </div>
              <div v-if="coresFavoritas.length" class="flex flex-wrap gap-2 pt-1">
                <button
                  v-for="cor in coresFavoritas"
                  :key="cor"
                  class="w-7 h-7 rounded-full border border-white shadow-sm ring-1 ring-gray-200"
                  :style="{ backgroundColor: cor }"
                  :title="cor"
                  @click="detalheCorSelecionada = cor"
                ></button>
              </div>
            </div>

            <div v-if="detalheAg.observacoes" class="mb-5">
              <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Observações</h4>
              <p class="text-sm text-gray-600 bg-gray-50 rounded-xl px-4 py-3 border border-gray-100">{{ detalheAg.observacoes }}</p>
            </div>

            <button @click="abrirModalEditar(detalheAg); detalheAg = null" class="w-full bg-rose-600 text-white rounded-xl py-3 text-sm font-semibold hover:bg-rose-700 transition-colors mb-2">
              Editar Agendamento
            </button>
            <button
              @click="abrirModalPagamento(detalheAg); detalheAg = null"
              class="w-full border border-green-300 text-green-700 rounded-xl py-3 text-sm font-semibold hover:bg-green-50 transition-colors mb-2"
            >
              Registrar Pagamento
            </button>
            <button
              v-if="authStore.user?.role === 'admin' || authStore.user?.role === 'recepcionista'"
              @click="confirmarExcluirAg(detalheAg)"
              class="w-full border border-red-200 text-red-600 rounded-xl py-3 text-sm font-semibold hover:bg-red-50 transition-colors"
            >
              Excluir Agendamento
            </button>
          </div>

          <!-- Direita: ficha do cliente + histórico -->
          <div :class="['sm:w-64 w-full flex-shrink-0 overflow-y-auto p-5', isMobile && detalheTab !== 'cliente' ? 'hidden' : '']">
            <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Cliente</h4>
            <div class="bg-gray-50 rounded-xl p-3.5 border border-gray-100 mb-4">
              <p class="text-sm font-bold text-gray-800">{{ detalheAg.cliente?.nome }}</p>
              <p v-if="detalheAg.cliente?.telefone" class="text-xs text-gray-500 mt-1">{{ detalheAg.cliente.telefone }}</p>
              <p v-if="detalheAg.cliente?.observacoes" class="text-xs text-gray-400 mt-1.5 italic">{{ detalheAg.cliente.observacoes }}</p>
              <button
                class="mt-3 text-xs text-rose-600 font-semibold hover:underline"
                @click="abrirDrawerCliente(detalheAg.cliente); detalheAg = null"
              >Ver perfil completo →</button>
            </div>

            <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
              Histórico
              <span v-if="!loadingDetalheClienteHistorico" class="font-normal text-gray-400 normal-case">({{ detalheClienteHistoricoItens.length }})</span>
            </h4>
            <div v-if="loadingDetalheClienteHistorico" class="text-xs text-gray-400 py-2">Carregando...</div>
            <div v-else-if="detalheClienteHistoricoItens.length === 0" class="text-xs text-gray-400 italic">Nenhuma visita.</div>
            <div
              v-for="(item, idx) in detalheClienteHistoricoItens.slice(0, 12)"
              :key="idx"
              class="mb-2 bg-white rounded-xl px-3 py-2.5 border border-gray-100"
            >
              <div class="flex items-start gap-2">
                <span class="mt-1.5 flex-shrink-0 w-2 h-2 rounded-full" :class="{ 'bg-yellow-400': item.agStatus==='pendente', 'bg-blue-400': item.agStatus==='confirmado', 'bg-green-400': item.agStatus==='concluido', 'bg-red-400': item.agStatus==='cancelado' }"></span>
                <div class="min-w-0">
                  <p class="text-xs font-semibold text-gray-800 truncate">{{ item.servico?.nome }}</p>
                  <p class="text-xs text-gray-400">{{ formatDataCliente(item.data_hora_inicio) }} · {{ formatHoraCliente(item.data_hora_inicio) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Confirmar Exclusão de Agendamento -->
    <div v-if="agParaExcluir" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-[60] p-4">
      <div class="bg-white w-full sm:max-w-xs sm:rounded-xl rounded-t-3xl shadow-xl p-6 text-center">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mb-4"></div>
        <p class="text-sm text-gray-700 mb-1">Excluir agendamento</p>
        <p class="font-semibold text-gray-900 mb-4">{{ agParaExcluir.cliente?.nome }}</p>
        <p class="text-xs text-gray-500 mb-6">Esta ação não pode ser desfeita.</p>
        <div class="flex gap-2">
          <button @click="agParaExcluir = null" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button @click="excluirAgendamento" :disabled="excluindoAg" class="flex-1 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ excluindoAg ? 'Excluindo...' : 'Excluir' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Registrar Pagamento (a partir dos agendamentos) -->
    <div v-if="modalPagAberto" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-[60] p-4" @click.self="modalPagAberto = false">
      <div class="bg-white w-full sm:max-w-sm sm:rounded-xl rounded-t-3xl shadow-xl max-h-[90vh] flex flex-col overflow-hidden">
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>
        <div class="flex-1 overflow-y-auto px-6 pt-5 pb-2">
          <h3 class="text-lg font-semibold text-gray-800 mb-1">Registrar Pagamento</h3>
          <p class="text-sm text-gray-500 mb-4">
            #{{ agPagSelecionado?.id }} · {{ agPagSelecionado?.cliente?.nome }}
          </p>

          <!-- Breakdown dos serviços -->
          <div class="bg-gray-50 rounded-lg p-3 mb-4 space-y-1">
            <div v-for="item in agPagSelecionado?.itens" :key="item.id"
              class="flex justify-between items-center text-xs text-gray-600">
              <span>{{ item.servico?.nome }}</span>
              <button type="button" class="text-xs font-semibold text-rose-600 hover:underline ml-2"
                @click="setPagValorBase(item.servico?.preco)">
                R$ {{ Number(item.servico?.preco).toFixed(2) }}
              </button>
            </div>
            <div class="border-t border-gray-200 pt-1 flex justify-between items-center text-sm font-bold text-gray-800">
              <span>Total</span>
              <button type="button" class="font-bold text-gray-800 hover:text-rose-600 transition-colors"
                @click="setPagValorBase(totalAgPag(agPagSelecionado))">
                R$ {{ totalAgPag(agPagSelecionado) }}
              </button>
            </div>
          </div>

          <form id="form-pag-ag" @submit.prevent="confirmarPagamentoAg" class="space-y-4">
            <div class="flex gap-3">
              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-1">Desconto (R$)</label>
                <input v-model="formPagAg.desconto" type="number" step="0.01" min="0"
                  class="w-full border border-amber-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 bg-amber-50"
                  placeholder="0.00" />
              </div>
              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-1">Valor (R$) *</label>
                <input v-model="formPagAg.valor" type="number" step="0.01" min="0.01" required
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400"
                  :class="{ 'border-amber-400 bg-amber-50': Number(formPagAg.desconto) > 0 }" />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Método *</label>
              <select v-model="formPagAg.metodo" required
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400">
                <option value="">Selecione...</option>
                <option value="dinheiro">Dinheiro</option>
                <option value="pix">PIX</option>
                <option value="cartao_credito">Cartão de Crédito</option>
                <option value="cartao_debito">Cartão de Débito</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status do agendamento</label>
              <select v-model="formPagAg.novoStatus"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400">
                <option value="">Manter atual</option>
                <option value="concluido">Marcar como Concluído</option>
                <option value="confirmado">Marcar como Confirmado</option>
              </select>
            </div>
            <p v-if="erroPagAg" class="text-sm text-red-600">{{ erroPagAg }}</p>
          </form>
        </div>
        <div class="flex gap-2 px-6 py-4 border-t border-gray-100 flex-shrink-0">
          <button type="button" @click="modalPagAberto = false" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-2.5 text-sm hover:bg-gray-50">Cancelar</button>
          <button type="submit" form="form-pag-ag" :disabled="savingPagAg" class="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg py-2.5 disabled:opacity-60">
            {{ savingPagAg ? 'Salvando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>

    <!-- PAINEL: Clientes -->
    <!-- PAINEL DE CLIENTES: lista + drawer de detalhes -->
    <div v-if="showClientesPanel" class="fixed inset-0 bg-black/40 flex items-end sm:items-center justify-center z-50 p-4" @click.self="showClientesPanel = false; clienteDrawer = false; buscaCliente = ''">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 flex-shrink-0">
          <h3 class="text-lg font-bold text-gray-800">Clientes</h3>
          <div class="flex items-center gap-2">
            <button class="bg-rose-600 text-white text-sm font-semibold px-4 py-1.5 rounded-lg hover:bg-rose-700" @click="abrirDrawerCliente(null)">+ Novo</button>
            <button @click="showClientesPanel = false; clienteDrawer = false; buscaCliente = ''" class="text-gray-400 hover:text-gray-600 text-xl leading-none ml-2">×</button>
          </div>
        </div>
        <div class="px-6 py-3 border-b border-gray-100 flex-shrink-0">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/>
            </svg>
            <input v-model="buscaCliente" type="text" placeholder="Buscar por nome..." class="w-full border border-gray-200 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
        </div>
        <div class="flex-1 overflow-auto">
          <div v-if="loadingClientes" class="p-8 text-center text-sm text-gray-400">Carregando...</div>
          <div v-else-if="clientesFiltrados.length === 0" class="p-8 text-center text-sm text-gray-400">Nenhum cliente encontrado.</div>
          <!--
            TABELA vs CARDS:
            Tabelas são ótimas no desktop mas quebram no mobile (colunas espremidas).
            Solução: tabela com hidden sm:table (só no desktop) +
            lista de cards com sm:hidden (só no mobile).
            Ambos dentro de <template v-else> para respeitar a cadeia v-if/v-else-if/v-else.
            Usamos CSS e não v-if/v-else porque ambas as listas leem o mesmo array em memória
            — não há custo de fetch ou renderização pesada em nenhum dos dois.
          -->
          <template v-else>
            <table class="hidden sm:table w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200 sticky top-0">
                <tr>
                  <th class="text-left px-4 py-3 font-medium text-gray-600">Nome</th>
                  <th class="text-left px-4 py-3 font-medium text-gray-600">Telefone</th>
                  <th class="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100">
                <tr v-for="c in clientesFiltrados" :key="c.id" class="hover:bg-rose-50 cursor-pointer" @click="abrirDrawerCliente(c)">
                  <td class="px-4 py-3 font-medium text-gray-800">{{ c.nome }}</td>
                  <td class="px-4 py-3 text-gray-500">{{ c.telefone || '-' }}</td>
                  <td class="px-4 py-3 text-right">
                    <button class="text-xs text-red-400 hover:text-red-600" @click.stop="removerCliente(c)">Remover</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <!-- Lista de cards para mobile (touch targets naturalmente maiores) -->
            <div class="sm:hidden divide-y divide-gray-100">
              <div
                v-for="c in clientesFiltrados"
                :key="c.id"
                class="flex items-center justify-between px-4 py-4 active:bg-rose-50 cursor-pointer"
                @click="abrirDrawerCliente(c)"
              >
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-gray-800">{{ c.nome }}</p>
                  <p class="text-xs text-gray-500 mt-0.5 truncate">{{ c.telefone || 'Sem contato' }}</p>
                </div>
                <div class="flex items-center gap-3 flex-shrink-0 ml-3">
                  <button
                    class="text-xs text-red-400 hover:text-red-600 px-2 py-1.5 rounded-lg hover:bg-red-50 transition-colors"
                    @click.stop="removerCliente(c)"
                  >Remover</button>
                  <svg class="w-4 h-4 text-gray-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- DRAWER DE CLIENTE (detalhes + histórico) -->
    <div v-if="clienteDrawer" class="fixed inset-0 bg-black/50 flex sm:items-center sm:justify-center items-end justify-center z-[60] sm:p-4" @click.self="clienteDrawer = false">
      <div class="bg-white sm:rounded-2xl rounded-t-3xl shadow-2xl w-full sm:max-w-3xl sm:max-h-[92vh] max-h-[95vh] flex flex-col overflow-hidden">
        <!-- Drag handle mobile -->
        <div class="sm:hidden w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-1 flex-shrink-0"></div>
        <div class="flex items-start justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <div>
            <h3 class="text-lg font-bold text-gray-800">{{ formCliente.nome || 'Novo Cliente' }}</h3>
            <p v-if="clienteSelecionadoPainel?.id" class="text-xs text-gray-400 mt-0.5">{{ historicoCliente.length }} visita{{ historicoCliente.length !== 1 ? 's' : '' }}</p>
          </div>
          <button @click="clienteDrawer = false" class="w-10 h-10 flex items-center justify-center rounded-xl hover:bg-gray-100 text-gray-400 hover:text-gray-600" aria-label="Fechar">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <!-- Tabs de navegação (mobile only) -->
        <div class="sm:hidden flex border-b border-gray-100 flex-shrink-0">
          <button
            @click="clienteTab = 'dados'"
            :class="clienteTab === 'dados' ? 'border-b-2 border-rose-600 text-rose-700 font-semibold' : 'text-gray-500'"
            class="flex-1 py-3 text-sm transition-colors"
          >Dados</button>
          <button
            @click="clienteTab = 'historico'"
            :class="clienteTab === 'historico' ? 'border-b-2 border-rose-600 text-rose-700 font-semibold' : 'text-gray-500'"
            class="flex-1 py-3 text-sm transition-colors"
          >Histórico</button>
        </div>
        <div class="flex flex-1 overflow-hidden">
          <!-- Esquerda: formulário -->
          <div :class="['sm:w-72 w-full flex-shrink-0 overflow-y-auto border-r border-gray-100 p-5', isMobile && clienteTab !== 'dados' ? 'hidden' : '']">
            <form @submit.prevent="salvarCliente" class="space-y-4">
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Nome</label>
                <input v-model="formCliente.nome" required class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 h-11" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Telefone</label>
                <div class="flex items-center border border-gray-200 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-rose-400 h-11">
                  <span class="flex items-center gap-1 px-3 py-2 bg-gray-50 text-sm text-gray-600 border-r border-gray-200 select-none whitespace-nowrap h-full">🇧🇷 +55</span>
                  <!--
                    type="tel" abre o teclado numérico no iOS/Android (com traços e parênteses).
                    inputmode="tel" reforça isso em browsers que ignoram o type.
                  -->
                  <input v-model="formCliente.telefone" type="tel" inputmode="tel" class="flex-1 px-3 py-2 text-sm focus:outline-none h-full" placeholder="(11) 99999-9999" />
                </div>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">Notas do cliente</label>
                <textarea v-model="formCliente.observacoes" rows="3" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 resize-none"></textarea>
              </div>
              <div>
                <div class="flex items-center justify-between mb-2">
                  <label class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Campos personalizados</label>
                  <button type="button" class="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-rose-600" @click="editandoCamposPainel = !editandoCamposPainel" :title="editandoCamposPainel ? 'Concluir' : 'Gerenciar campos'">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>
                  </button>
                </div>
                <div v-if="formCliente.campos_dinamicos.length === 0 && !editandoCamposPainel" class="text-xs text-gray-400 italic px-1">Nenhum campo adicionado.</div>
                <div v-for="(campo, i) in formCliente.campos_dinamicos" :key="i" class="mb-2">
                  <div v-if="editandoCamposPainel" class="flex gap-1.5 items-center">
                    <input v-model="campo.chave" placeholder="Nome do campo" class="flex-1 border border-gray-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-rose-400" />
                    <button type="button" class="w-8 h-8 flex items-center justify-center text-gray-300 hover:text-red-500 text-lg leading-none" @click="formCliente.campos_dinamicos.splice(i,1)">×</button>
                  </div>
                  <div v-else>
                    <label class="block text-xs font-medium text-gray-500 mb-0.5">{{ campo.chave }}</label>
                    <input v-model="campo.valor" class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
                  </div>
                </div>
                <button v-if="editandoCamposPainel" type="button" class="mt-1 w-full border border-dashed border-gray-300 text-xs text-gray-500 hover:border-rose-400 hover:text-rose-600 rounded-lg py-2" @click="formCliente.campos_dinamicos.push({ chave: '', valor: '' })">+ Adicionar campo</button>
              </div>
              <p v-if="erroCliente" class="text-sm text-red-500">{{ erroCliente }}</p>
              <div class="flex gap-2 pt-1">
                <button type="button" class="flex-1 border border-gray-200 text-gray-600 rounded-lg py-3 text-sm hover:bg-gray-50" @click="clienteDrawer = false">Cancelar</button>
                <button type="submit" :disabled="savingCliente" class="flex-1 bg-rose-600 text-white rounded-lg py-3 text-sm font-semibold hover:bg-rose-700 disabled:opacity-50">{{ savingCliente ? 'Salvando...' : 'Salvar' }}</button>
              </div>
            </form>
          </div>
          <!-- Direita: histórico -->
          <div :class="['flex-1 overflow-y-auto p-5', isMobile && clienteTab !== 'historico' ? 'hidden' : '']">
            <h4 class="text-sm font-semibold text-gray-700 mb-4">Visitas anteriores</h4>
            <div v-if="!clienteSelecionadoPainel?.id" class="text-sm text-gray-400 italic">Salve o cliente para ver o histórico.</div>
            <div v-else-if="loadingHistoricoCliente" class="text-sm text-gray-400">Carregando...</div>
            <div v-else-if="historicoClienteItens.length === 0" class="text-sm text-gray-400 italic">Nenhuma visita registrada.</div>
            <div v-for="(item, idx) in historicoClienteItens" :key="idx" class="mb-3 bg-gray-50 rounded-xl p-3.5 border border-gray-100">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-start gap-2.5 min-w-0">
                  <span class="mt-1.5 flex-shrink-0 w-2.5 h-2.5 rounded-full" :class="{ 'bg-yellow-400': item.agStatus==='pendente', 'bg-blue-400': item.agStatus==='confirmado', 'bg-green-400': item.agStatus==='concluido', 'bg-red-400': item.agStatus==='cancelado' }"></span>
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-gray-800 truncate">{{ item.servico?.nome }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">Colaborador: {{ item.profissional?.nome }}</p>
                    <p class="text-xs text-gray-400 mt-0.5">* {{ item.servico?.nome }}: {{ item.servico?.duracao_minutos }}min ({{ diaSemanaCliente(item.data_hora_inicio) }})</p>
                  </div>
                </div>
                <div class="text-right flex-shrink-0">
                  <p class="text-sm font-medium text-gray-700">{{ formatDataCliente(item.data_hora_inicio) }}</p>
                  <p class="text-xs text-gray-400">{{ formatHoraCliente(item.data_hora_inicio) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL: Tarefa Interna -->
    <div v-if="showModalTarefa" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">{{ modalTarefaMode === 'edit' ? 'Editar Tarefa' : 'Nova Tarefa' }}</h3>
        <form @submit.prevent="salvarTarefa" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Título *</label>
            <input v-model="formTarefa.titulo" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" placeholder="Ex.: Ligar para fornecedor" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Descrição</label>
            <textarea v-model="formTarefa.descricao" rows="2" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-xs text-gray-600 mb-1">Início *</label>
              <input v-model="formTarefa.data_hora_inicio" type="datetime-local" required class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            </div>
            <div>
              <label class="block text-xs text-gray-600 mb-1">Fim</label>
              <input v-model="formTarefa.data_hora_fim" type="datetime-local" class="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input v-model="formTarefa.concluida" type="checkbox" id="cb-concluida" class="accent-indigo-600" />
            <label for="cb-concluida" class="text-sm text-gray-700">Tarefa concluída</label>
          </div>
          <p v-if="modalTarefaError" class="text-sm text-red-500">{{ modalTarefaError }}</p>
          <div class="flex gap-2 pt-2">
            <button type="button" class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-3 text-sm hover:bg-gray-50" @click="showModalTarefa = false">Cancelar</button>
            <button type="submit" :disabled="savingTarefa" class="flex-1 bg-indigo-600 text-white rounded-lg py-3 text-sm font-semibold hover:bg-indigo-700 disabled:opacity-50">
              {{ savingTarefa ? 'Salvando...' : (modalTarefaMode === 'edit' ? 'Salvar' : 'Criar') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- PAINEL: Detalhe da Tarefa -->
    <div v-if="detalheTarefa" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" @click.self="detalheTarefa = null">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-2">
            <h3 class="text-base font-bold text-gray-800">{{ detalheTarefa.titulo }}</h3>
          </div>
          <button @click="detalheTarefa = null" class="p-1 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <p v-if="detalheTarefa.descricao" class="text-sm text-gray-600 bg-gray-50 rounded-lg px-3 py-2 mb-4">{{ detalheTarefa.descricao }}</p>
        <div class="text-sm text-gray-500 mb-1">{{ formatDate(detalheTarefa.data_hora_inicio) }}<span v-if="detalheTarefa.data_hora_fim"> → {{ formatHoraCliente(detalheTarefa.data_hora_fim) }}</span></div>
        <div class="flex items-center gap-2 mt-3 mb-4">
          <span :class="detalheTarefa.concluida ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'" class="text-xs font-semibold px-2.5 py-0.5 rounded-full">
            {{ detalheTarefa.concluida ? '✓ Concluída' : 'Pendente' }}
          </span>
        </div>
        <div class="flex gap-2">
          <button @click="abrirModalTarefa('', detalheTarefa); detalheTarefa = null" class="flex-1 bg-indigo-600 text-white rounded-lg py-3 text-sm font-semibold hover:bg-indigo-700">Editar</button>
          <button @click="excluirTarefa(detalheTarefa)" class="flex-1 border border-red-200 text-red-500 rounded-lg py-3 text-sm hover:bg-red-50">Excluir</button>
          <button @click="detalheTarefa = null" class="border border-gray-200 text-gray-500 rounded-lg py-3 px-4 text-sm hover:bg-gray-50">×</button>
        </div>
      </div>
    </div>

    <!-- MODAL RÁPIDO: Criar cliente dentro do agendamento -->
    <div v-if="showModalClienteRapido" class="fixed inset-0 bg-black/60 flex items-center justify-center z-[70] p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Novo Cliente</h3>
        <form @submit.prevent="salvarClienteRapido" class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
            <input v-model="formClienteRapido.nome" required class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefone</label>
            <input v-model="formClienteRapido.telefone" type="tel" inputmode="tel" class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-rose-400 h-11" placeholder="(11) 99999-9999" />
          </div>
          <p v-if="erroClienteRapido" class="text-sm text-red-500">{{ erroClienteRapido }}</p>
          <div class="flex gap-2 pt-2">
            <button type="button" class="flex-1 border border-gray-300 text-gray-600 rounded-lg py-3 text-sm hover:bg-gray-50" @click="showModalClienteRapido = false">Cancelar</button>
            <button type="submit" :disabled="savingClienteRapido" class="flex-1 bg-rose-600 text-white rounded-lg py-3 text-sm font-semibold hover:bg-rose-700 disabled:opacity-50">
              {{ savingClienteRapido ? 'Criando...' : 'Criar e selecionar' }}
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Calendar, ClipboardList, ChevronDown } from '@lucide/vue'
import { useAuthStore } from '@/stores/auth'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import ptBrLocale from '@fullcalendar/core/locales/pt-br'
import api from '@/api/client'
import { useToast } from '@/composables/useToast'

const { sucesso: toastSucesso } = useToast()

// ─── State ─────────────────────────────────────────────────────────────────
const authStore = useAuthStore()
const isProfissional = computed(() => authStore.user?.role === 'profissional')
const isRecepcionistaOuAdmin = computed(() => ['recepcionista', 'admin'].includes(authStore.user?.role))

const agendamentos = ref([])
const clientes = ref([])
const servicos = ref([])
const profissionais = ref([])
const loading = ref(true)
const loadingClientes = ref(false)

const filtroProfissional = ref(null)
const buscaCalendario = ref('')
const filtroPendentesProximos = ref(false)

/** Retorna a data daqui a `days` dias úteis (seg=folga: pula segunda-feira) */
function addDiasUteis(date, days) {
  const d = new Date(date)
  let added = 0
  while (added < days) {
    d.setDate(d.getDate() + 1)
    if (d.getDay() !== 1) added++ // pula segunda-feira
  }
  return d
}

const agendamentosPendentesProximos = computed(() => {
  const agora = new Date()
  const limite = addDiasUteis(agora, 4)
  return agendamentos.value
    .filter(ag => {
      if (ag.status !== 'pendente') return false
      return ag.itens?.some(item => {
        const inicio = new Date(item.data_hora_inicio)
        return inicio >= agora && inicio <= limite
      })
    })
    .sort((a, b) => {
      const aMin = Math.min(...(a.itens ?? []).map(i => new Date(i.data_hora_inicio).getTime()))
      const bMin = Math.min(...(b.itens ?? []).map(i => new Date(i.data_hora_inicio).getTime()))
      return aMin - bMin
    })
})

// ─── Viewport & Mobile UI ──────────────────────────────────────────────────
// isMobile é um ref reativo que rastreia a largura da janela. Não podemos
// usar só CSS aqui porque precisamos que computed properties (como
// calendarOptions) reajam a esta mudança e recalculem seus valores.
// Breakpoint ajustado para o menu de ações entrar antes em telas médias.
const MOBILE_BREAKPOINT = 1100
const isMobile = ref(window.innerWidth < MOBILE_BREAKPOINT)
function handleResize() { isMobile.value = window.innerWidth < MOBILE_BREAKPOINT }
onMounted(() => window.addEventListener('resize', handleResize))
onUnmounted(() => window.removeEventListener('resize', handleResize))

// Controla o menu dropdown de ações secundárias no mobile
const showMobileMenu = ref(false)
const showNovoMenu = ref(false)

// Toggle: mostrar ou esconder tarefas internas no calendário
const mostrarTarefas = ref(true)

// Controla qual tab está ativa nos painéis de detalhe (mobile only).
// No desktop os dois painéis ficam side-by-side; no mobile viram tabs.
const detalheTab = ref('servicos')
const clienteTab = ref('dados')

const showModal = ref(false)
const modalMode = ref('create')
const saving = ref(false)
const modalError = ref('')
const detalheAg = ref(null)
const agParaExcluir = ref(null)
const excluindoAg = ref(false)
const detalheCorSelecionada = ref('#9ca3af')
const coresFavoritas = ref([])

const STATUS_LABELS = {
  pendente: 'Pendente',
  confirmado: 'Confirmado',
  concluido: 'Concluído',
  cancelado: 'Cancelado',
}

// Pagamento rápido a partir do agendamento
const modalPagAberto = ref(false)
const agPagSelecionado = ref(null)
const savingPagAg = ref(false)
const erroPagAg = ref('')
const basePagAg = ref('0.00')
const formPagAg = ref({ valor: '', desconto: '0.00', metodo: '', novoStatus: '' })
const formData = ref({ id: null, cliente_id: '', cor_hex: null, observacoes: '', itens: [] })

// Modal rápido de cliente dentro do agendamento
const showModalClienteRapido = ref(false)
const savingClienteRapido = ref(false)
const erroClienteRapido = ref('')
const formClienteRapido = ref({ nome: '', telefone: '' })

// Visão colunas por profissional
const colunaPorProfissional = ref(false)

// Tarefas internas
const tarefas = ref([])
const showModalTarefa = ref(false)
const modalTarefaMode = ref('create')
const savingTarefa = ref(false)
const modalTarefaError = ref('')
const detalheTarefa = ref(null)
const formTarefa = ref({ id: null, titulo: '', descricao: '', data_hora_inicio: '', data_hora_fim: '', responsavel_id: null, concluida: false })

const showClientesPanel = ref(false)
const clienteDrawer = ref(false)
const clienteSelecionadoPainel = ref(null)
const savingCliente = ref(false)
const erroCliente = ref('')
const editandoCamposPainel = ref(false)
const formCliente = ref({ nome: '', telefone: '', observacoes: '', campos_dinamicos: [] })
const historicoCliente = ref([])
const loadingHistoricoCliente = ref(false)
const buscaCliente = ref('')

// Reseta as tabs ao abrir os painéis (watches colocados APÓS as declarações
// das refs que observam, para evitar ReferenceError por TDZ)
watch(detalheAg, (val) => { if (val) detalheTab.value = 'servicos' })
watch(clienteDrawer, (val) => { if (val) clienteTab.value = 'dados' })
watch(isMobile, (mobile) => {
  if (!mobile) showMobileMenu.value = false
})

// Detalhe panel: histórico separado para não conflitar com o drawer de clientes
const detalheClienteHistorico = ref([])
const loadingDetalheClienteHistorico = ref(false)
const detalheClienteHistoricoItens = computed(() => {
  const items = []
  for (const ag of detalheClienteHistorico.value) {
    for (const item of ag.itens ?? []) items.push({ ...item, agStatus: ag.status })
  }
  return items.sort((a, b) => new Date(b.data_hora_inicio) - new Date(a.data_hora_inicio))
})
watch(detalheAg, (ag) => {
  if (ag?.cliente?.id) {
    loadingDetalheClienteHistorico.value = true
    detalheClienteHistorico.value = []
    api.get(`/agendamentos/?cliente_id=${ag.cliente.id}`)
      .then(r => { detalheClienteHistorico.value = r.data })
      .finally(() => { loadingDetalheClienteHistorico.value = false })
  } else {
    detalheClienteHistorico.value = []
  }
})

watch(detalheAg, (ag) => {
  detalheCorSelecionada.value = normalizarHexColor(ag?.cor_hex) || '#9ca3af'
})

const clientesFiltrados = computed(() => {
  const q = buscaCliente.value.trim().toLowerCase()
  if (!q) return clientes.value
  return clientes.value.filter(c => c.nome.toLowerCase().includes(q))
})

// Autocomplete de cliente no modal de agendamento
const clienteBuscaNome = ref('')
const showBuscaDropdown = ref(false)
const clientesBuscaFiltrados = computed(() => {
  const q = clienteBuscaNome.value.trim().toLowerCase()
  if (!q) return clientes.value.slice(0, 20)
  return clientes.value.filter(c => c.nome.toLowerCase().includes(q))
})
function selectCliente(c) {
  formData.value.cliente_id = c.id
  clienteBuscaNome.value = c.nome
  showBuscaDropdown.value = false
}

// ─── FullCalendar ──────────────────────────────────────────────────────────
const DEFAULT_AGENDAMENTO_COLOR = '#9ca3af'

function normalizarHexColor(value) {
  if (!value) return null
  const raw = String(value).trim()
  const normalized = raw.startsWith('#') ? raw : `#${raw}`
  return /^#[0-9a-fA-F]{6}$/.test(normalized) ? normalized.toLowerCase() : null
}

function isHexCorEscura(hex) {
  const safe = normalizarHexColor(hex) || DEFAULT_AGENDAMENTO_COLOR
  const r = parseInt(safe.slice(1, 3), 16)
  const g = parseInt(safe.slice(3, 5), 16)
  const b = parseInt(safe.slice(5, 7), 16)
  const luminancia = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
  return luminancia < 0.55
}

function corComAlpha(hex, alpha) {
  const safe = normalizarHexColor(hex) || DEFAULT_AGENDAMENTO_COLOR
  const r = parseInt(safe.slice(1, 3), 16)
  const g = parseInt(safe.slice(3, 5), 16)
  const b = parseInt(safe.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

function getAgendamentoColor(ag) {
  const bgBase = normalizarHexColor(ag?.cor_hex) || DEFAULT_AGENDAMENTO_COLOR
  const textoEscuro = !isHexCorEscura(bgBase)
  return {
    bg: corComAlpha(bgBase, 0.2),
    border: bgBase,
    text: textoEscuro ? '#1f2937' : '#f9fafb',
  }
}

const computedSlotMax = computed(() => {
  let maxH = 22
  for (const ag of agendamentos.value) {
    for (const item of ag.itens ?? []) {
      if (!item.data_hora_inicio) continue
      const h = new Date(item.data_hora_inicio).getHours()
      if (h >= maxH) maxH = h + 2
    }
  }
  return String(maxH).padStart(2, '0') + ':00:00'
})

const calendarEvents = computed(() => {
  const q = buscaCalendario.value.trim().toLowerCase()
  const profFiltroId = filtroProfissional.value ? Number(filtroProfissional.value) : null
  const events = []
  for (const ag of agendamentos.value) {
    if (q && !(ag.cliente?.nome ?? '').toLowerCase().includes(q)) continue
    const color = getAgendamentoColor(ag)

    // Agrupar itens por profissional para mesclar blocos consecutivos do mesmo atendimento
    const byProf = new Map()
    for (const item of ag.itens ?? []) {
      if (profFiltroId && item.profissional?.id !== profFiltroId) continue
      const profId = item.profissional?.id ?? item.profissional_id
      if (!byProf.has(profId)) byProf.set(profId, [])
      byProf.get(profId).push(item)
    }

    for (const [profId, items] of byProf) {
      const profNome = items[0]?.profissional?.nome ?? ''
      // Ordenar por início
      const sorted = [...items].sort((a, b) =>
        new Date(a.data_hora_inicio) - new Date(b.data_hora_inicio)
      )
      // Mesclar blocos contíguos/sobrepostos em um único evento por profissional
      const blocos = []
      for (const item of sorted) {
        const ultimo = blocos[blocos.length - 1]
        if (ultimo && new Date(item.data_hora_inicio) <= new Date(ultimo.end)) {
          if (item.data_hora_fim > ultimo.end) ultimo.end = item.data_hora_fim
          ultimo.servicos.push(item.servico?.nome ?? '')
        } else {
          blocos.push({
            start: item.data_hora_inicio,
            end: item.data_hora_fim ?? item.data_hora_inicio,
            servicos: [item.servico?.nome ?? ''],
          })
        }
      }
      for (const bloco of blocos) {
        const servNome = bloco.servicos.filter(Boolean).join(' + ')
        events.push({
          id: `${ag.id}-prof${profId}-${bloco.start}`,
          title: ag.cliente?.nome ?? '—',
          start: bloco.start,
          end: bloco.end,
          backgroundColor: color.bg,
          borderColor: color.border,
          textColor: color.text,
          extendedProps: { ag, servNome, profNome, profId, statusLabel: STATUS_LABELS[ag.status] ?? ag.status },
        })
      }
    }
  }
  return events
})

const TAREFA_COLORS      = { bg: '#ede9fe', border: '#7c3aed', text: '#4c1d95' }
const TAREFA_COLORS_DONE = { bg: '#f3f4f6', border: '#9ca3af', text: '#6b7280' }

const calendarEventsTarefas = computed(() => {
  const q = buscaCalendario.value.trim().toLowerCase()
  return tarefas.value
    .filter(t => !q || t.titulo.toLowerCase().includes(q))
    .map(t => {
      const c = t.concluida ? TAREFA_COLORS_DONE : TAREFA_COLORS
      return {
        id: `tarefa-${t.id}`,
        title: `${t.titulo}`,
        start: t.data_hora_inicio,
        end: t.data_hora_fim ?? t.data_hora_inicio,
        backgroundColor: c.bg,
        borderColor: c.border,
        textColor: c.text,
        extendedProps: { tarefa: t, tipo: 'tarefa' },
      }
    })
})

const allCalendarEvents = computed(() => [
  ...calendarEvents.value,
  ...(mostrarTarefas.value ? calendarEventsTarefas.value : []),
])

// Na visão diária por colunas, quando um profissional está filtrado,
// exibe apenas a coluna dele. Isso mantém o foco sem informar em excesso.
const profissionaisColuna = computed(() => {
  if (filtroProfissional.value) {
    return profissionais.value.filter(p => p.id === Number(filtroProfissional.value))
  }
  return profissionais.value
})

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  locale: ptBrLocale,
  // No mobile, timeGridWeek renderiza 7 colunas em ~375px — inutilizável.
  // listWeek é a view mais amigável em telas pequenas.
  initialView: isMobile.value ? 'listWeek' : 'timeGridWeek',
  // headerToolbar no mobile: apenas prev/next e today. Os botões de view
  // ficam escondidos pois o usuário pode usar gestos de swipe no listWeek.
  headerToolbar: isMobile.value
    ? { left: 'prev,next', center: 'title', right: 'today' }
    : { left: 'prev,next today', center: 'title', right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek' },
  allDaySlot: false,
  slotMinTime: '07:00:00',
  slotMaxTime: computedSlotMax.value,
  slotDuration: '00:30:00',
  slotLabelInterval: '01:00:00',
  slotLabelFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
  expandRows: true,
  nowIndicator: true,
  editable: false,
  droppable: false,
  eventDurationEditable: false,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: true,
  weekends: true,
  firstDay: 1,
  height: '100%',
  events: allCalendarEvents.value,
  eventClick: onEventClick,
  eventDidMount: onEventDidMount,
  dateClick: onDateClick,
  eventContent: renderEventContent,
}))

// ─── Visão em colunas por profissional ─────────────────────────────────────
const colunaDia = ref(new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date()))

const colunaSlots = computed(() => {
  const slots = []
  for (let h = 7; h <= 21; h++) {
    slots.push(String(h).padStart(2, '0') + ':00')
    slots.push(String(h).padStart(2, '0') + ':30')
  }
  return slots
})

const SLOT_HEIGHT = 56 // px — must match h-14 (3.5rem = 56px)
const DAY_START_MINUTES = 7 * 60  // 07:00

function colunaEventosDoProfissional(profId) {
  return calendarEvents.value.filter(ev => {
    const evDate = ev.start ? ev.start.slice(0, 10) : ''
    return evDate === colunaDia.value && ev.extendedProps?.profId === profId
  }).map(ev => ({
    ...ev,
    ag: ev.extendedProps.ag,
    clienteNome: ev.extendedProps.ag?.cliente?.nome ?? '—',
    servNome: ev.extendedProps.servNome,
    color: getAgendamentoColor(ev.extendedProps.ag),
    startIso: ev.start,
    endIso: ev.end,
  }))
}

function colunaEventoStyle(ev) {
  const startMin = toMinutes(ev.startIso) - DAY_START_MINUTES
  const endMin = toMinutes(ev.endIso) - DAY_START_MINUTES
  const top = (startMin / 30) * SLOT_HEIGHT
  const height = Math.max(((endMin - startMin) / 30) * SLOT_HEIGHT, SLOT_HEIGHT / 2)
  return {
    top: top + 'px',
    height: height + 'px',
    backgroundColor: ev.color.bg,
    border: `1px solid ${ev.color.border}`,
  }
}

function toMinutes(iso) {
  if (!iso) return DAY_START_MINUTES
  const d = new Date(iso)
  return d.getHours() * 60 + d.getMinutes()
}

function prevDay(dateStr) {
  const d = new Date(dateStr + 'T12:00:00')
  d.setDate(d.getDate() - 1)
  return formatDateISOInSaoPaulo(d)
}
function nextDay(dateStr) {
  const d = new Date(dateStr + 'T12:00:00')
  d.setDate(d.getDate() + 1)
  return formatDateISOInSaoPaulo(d)
}
function formatDayLabel(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr + 'T12:00').toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: 'long' })
}

function escapeHtml(str) {
  if (!str) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function renderEventContent(arg) {
  const { servNome, profNome } = arg.event.extendedProps
  const ag = arg.event.extendedProps.ag
  const clienteNome = ag?.cliente?.nome ?? arg.event.title
  const hora = arg.event.start
    ? new Date(arg.event.start).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' })
    : ''

  const durMin = (arg.event.end && arg.event.start)
    ? (arg.event.end.getTime() - arg.event.start.getTime()) / 60000
    : 60

  const firstName = (s) => s ? s.split(' ')[0] : ''
  const te = escapeHtml

  // ≤ 30 min (~48px): linha única compacta
  if (durMin <= 30) {
    return {
      html: `<div class="fc-ev-chip">`
        + `<span class="fc-ev-chip-name">${te(firstName(clienteNome))}</span>`
        + (hora ? `<span class="fc-ev-chip-sep">·</span><span class="fc-ev-chip-time">${te(hora)}</span>` : '')
        + `</div>`,
    }
  }

  // 31–60 min (~96px): 2 linhas — nome + serviço/prof comprimidos
  if (durMin <= 60) {
    const sub = [servNome, firstName(profNome)].filter(Boolean).join(' · ')
    return {
      html: `<div class="fc-event-inner">`
        + `<div class="fc-ev-title">${te(firstName(clienteNome))}</div>`
        + (sub ? `<div class="fc-ev-sub">${te(sub)}</div>` : '')
        + `</div>`,
    }
  }

  // > 60 min: layout completo — nome + serviço + prof · hora
  const sub2 = [firstName(profNome), hora].filter(Boolean).join(' · ')
  return {
    html: `<div class="fc-event-inner">`
      + `<div class="fc-ev-title">${te(clienteNome)}</div>`
      + (servNome ? `<div class="fc-ev-sub">${te(servNome)}</div>` : '')
      + (sub2 ? `<div class="fc-ev-sub">${te(sub2)}</div>` : '')
      + `</div>`,
  }
}

function onEventClick(info) {
  if (info.event.extendedProps.tipo === 'tarefa') {
    detalheTarefa.value = info.event.extendedProps.tarefa
  } else {
    detalheAg.value = info.event.extendedProps.ag
  }
}

function onEventDidMount(info) {
  if (info.event.extendedProps.tipo === 'tarefa') return
  const statusLabel = info.event.extendedProps.statusLabel || 'Sem status'
  info.el.title = `Status: ${statusLabel}`
}

function onDateClick(info) {
  const dt = info.dateStr.includes('T') ? info.dateStr.slice(0, 16) : info.dateStr + 'T09:00'
  abrirModalNovo(dt)
}

async function onEventDrop(info) {
  const ag = info.event.extendedProps.ag
  const delta = info.event.start - new Date(ag.itens?.[0]?.data_hora_inicio)
  try {
    await api.put(`/agendamentos/${ag.id}`, {
      cliente_id: ag.cliente_id,
      observacoes: ag.observacoes || null,
      itens: ag.itens.map(i => ({
        servico_id: i.servico?.id ?? i.servico_id,
        profissional_id: i.profissional?.id ?? i.profissional_id,
        data_hora_inicio: new Date(new Date(i.data_hora_inicio).getTime() + delta).toISOString(),
      })),
    })
    await fetchAgendamentos()
  } catch (e) {
    info.revert()
    alert(e.response?.data?.detail || 'Erro ao mover agendamento.')
  }
}

// ─── Agendamento CRUD ──────────────────────────────────────────────────────
function emptyItem(dt = '') {
  return { servico_id: '', profissional_id: '', data_hora_inicio: dt, data_hora_fim: '' }
}

function abrirModalNovo(dt = '', profId = null) {
  modalMode.value = 'create'
  const item = emptyItem(dt)
  if (profId) item.profissional_id = profId
  formData.value = { id: null, cliente_id: '', cor_hex: null, observacoes: '', itens: [item] }
  clienteBuscaNome.value = ''
  modalError.value = ''
  sugestaoItemIdx.value = -1
  showModal.value = true
}

function abrirModalEditar(ag) {
  modalMode.value = 'edit'
  formData.value = {
    id: ag.id,
    cliente_id: ag.cliente_id,
    cor_hex: ag.cor_hex || null,
    observacoes: ag.observacoes || '',
    itens: ag.itens.map(i => ({
      servico_id: i.servico?.id ?? i.servico_id,
      profissional_id: i.profissional?.id ?? i.profissional_id,
      data_hora_inicio: toDatetimeLocal(i.data_hora_inicio),
      data_hora_fim: toDatetimeLocal(i.data_hora_fim),
    })),
  }
  clienteBuscaNome.value = ag.cliente?.nome || ''
  modalError.value = ''
  sugestaoItemIdx.value = -1
  showModal.value = true
}

function addItem() {
  // Usa o fim do último item como início do novo (encadeamento sequencial)
  const lastItem = formData.value.itens[formData.value.itens.length - 1]
  const novoInicio = lastItem?.data_hora_fim || lastItem?.data_hora_inicio || ''
  formData.value.itens.push(emptyItem(novoInicio))
}
function removeItem(idx) { formData.value.itens.splice(idx, 1) }

/** Quando o serviço muda, filtra profissionais e preenche data_hora_fim automaticamente */
function onServicoChange(item, idx) {
  // Se o profissional atual não atende esse serviço, limpa a seleção
  if (item.profissional_id && item.servico_id) {
    const aptos = profissionaisParaItem(item)
    if (!aptos.some(p => p.id === item.profissional_id)) {
      item.profissional_id = ''
    }
  }
  if (!item.data_hora_inicio || !item.servico_id) return
  const servico = servicos.value.find(s => s.id === item.servico_id)
  if (!servico) return
  const inicio = new Date(item.data_hora_inicio)
  const fim = new Date(inicio.getTime() + servico.duracao_minutos * 60000)
  item.data_hora_fim = toDatetimeLocal(fim.toISOString())
}

/** Quando o início muda, desloca o fim mantendo a duração */
function onInicioChange(item, idx) {
  if (!item.data_hora_inicio || !item.data_hora_fim) return
  const servico = servicos.value.find(s => s.id === item.servico_id)
  if (!servico) return
  const inicio = new Date(item.data_hora_inicio)
  const fim = new Date(inicio.getTime() + servico.duracao_minutos * 60000)
  item.data_hora_fim = toDatetimeLocal(fim.toISOString())
  // Herda a data para itens subsequentes ainda sem data
  for (let i = idx + 1; i < formData.value.itens.length; i++) {
    if (!formData.value.itens[i].data_hora_inicio) {
      formData.value.itens[i].data_hora_inicio = item.data_hora_inicio
    }
  }
}

/** Quando o profissional muda, encadeia o início após o último serviço do mesmo profissional */
function onProfissionalChange(item, idx) {
  if (!item.profissional_id) return
  const anterior = formData.value.itens
    .slice(0, idx)
    .filter(i => Number(i.profissional_id) === Number(item.profissional_id) && i.data_hora_fim)
  if (anterior.length === 0) return
  const ultimo = anterior[anterior.length - 1]
  item.data_hora_inicio = ultimo.data_hora_fim
  if (item.servico_id) {
    const servico = servicos.value.find(s => s.id === item.servico_id)
    if (servico) {
      const inicio = new Date(item.data_hora_inicio)
      item.data_hora_fim = toDatetimeLocal(new Date(inicio.getTime() + servico.duracao_minutos * 60000).toISOString())
    }
  }
}

/** Detecção de conflito em tempo real para cada item do modal */
const conflictosPorItem = computed(() => {
  const clienteId = Number(formData.value.cliente_id)
  return formData.value.itens.map((item, idx) => {
    if (!item.profissional_id || !item.data_hora_inicio || !item.data_hora_fim) return null
    const inicio = new Date(item.data_hora_inicio)
    const fim = new Date(item.data_hora_fim)
    if (isNaN(inicio.getTime()) || isNaN(fim.getTime())) return null
    const profId = Number(item.profissional_id)
    const editandoId = modalMode.value === 'edit' ? formData.value.id : null

    // Verificar contra agendamentos existentes (profissional e cliente)
    for (const ag of agendamentos.value) {
      if (editandoId && ag.id === editandoId) continue
      if (ag.status === 'cancelado') continue
      const agClienteId = ag.cliente_id ?? ag.cliente?.id
      for (const ex of ag.itens ?? []) {
        const eInicio = new Date(ex.data_hora_inicio)
        const eFim = new Date(ex.data_hora_fim)
        if (!(inicio < eFim && fim > eInicio)) continue
        if ((ex.profissional?.id ?? ex.profissional_id) === profId)
          return `${ex.profissional?.nome ?? 'Profissional'} já tem "${ex.servico?.nome ?? 'serviço'}" às ${formatHoraCliente(ex.data_hora_inicio)}`
        if (clienteId && agClienteId === clienteId)
          return `Cliente já tem "${ex.servico?.nome ?? 'serviço'}" às ${formatHoraCliente(ex.data_hora_inicio)} — dois serviços simultâneos não são permitidos`
      }
    }

    // Verificar conflito entre itens do mesmo formulário (cliente não pode estar em dois lugares)
    for (let i = 0; i < formData.value.itens.length; i++) {
      if (i === idx) continue
      const other = formData.value.itens[i]
      if (!other.data_hora_inicio || !other.data_hora_fim) continue
      const oInicio = new Date(other.data_hora_inicio)
      const oFim = new Date(other.data_hora_fim)
      if (inicio < oFim && fim > oInicio) {
        const otherServ = servicos.value.find(s => s.id === other.servico_id)
        return `Conflito com Serviço ${i + 1} (${otherServ?.nome ?? '—'}) — cliente não pode ter dois serviços ao mesmo tempo`
      }
    }

    return null
  })
})

// ─── Sugestão de horários disponíveis ──────────────────────────────────────
const sugestaoItemIdx = ref(-1)
const sugestaoData = ref(new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(new Date()))

function abrirSugestoes(idx) {
  sugestaoItemIdx.value = sugestaoItemIdx.value === idx ? -1 : idx
  const item = formData.value.itens[idx]
  if (item?.data_hora_inicio?.length >= 10) sugestaoData.value = item.data_hora_inicio.slice(0, 10)
}

const slotsDisponiveis = computed(() => {
  const idx = sugestaoItemIdx.value
  if (idx < 0 || !formData.value.itens[idx]) return []
  const item = formData.value.itens[idx]
  const profId = Number(item.profissional_id)
  const clienteId = Number(formData.value.cliente_id)
  const servico = servicos.value.find(s => s.id === item.servico_id)
  if (!servico || !profId || !clienteId || !sugestaoData.value) return []
  const durMin = servico.duracao_minutos
  const date = sugestaoData.value
  const editandoId = modalMode.value === 'edit' ? formData.value.id : null
  const agora = new Date()
  const result = []

  for (let h = 7; h <= 21; h++) {
    for (let m = 0; m < 60; m += 30) {
      const startStr = `${date}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
      const inicio = new Date(startStr)
      const fim = new Date(inicio.getTime() + durMin * 60000)
      // Não sugerir horários no passado
      if (inicio <= agora) continue
      // Não sugerir se o serviço ultrapassa 22h
      if (fim.getHours() > 22 || (fim.getHours() === 22 && fim.getMinutes() > 0)) continue

      let ok = true
      for (const ag of agendamentos.value) {
        if (!ok) break
        if (ag.status === 'cancelado') continue
        if (editandoId && ag.id === editandoId) continue
        const agClienteId = ag.cliente_id ?? ag.cliente?.id
        for (const ex of ag.itens ?? []) {
          const eInicio = new Date(ex.data_hora_inicio)
          const eFim = new Date(ex.data_hora_fim)
          if (!(inicio < eFim && fim > eInicio)) continue
          if ((ex.profissional?.id ?? ex.profissional_id) === profId) { ok = false; break }
          if (agClienteId === clienteId) { ok = false; break }
        }
      }
      if (!ok) continue

      // Verificar conflito com outros itens do mesmo formulário
      for (let i = 0; i < formData.value.itens.length; i++) {
        if (i === idx) continue
        const other = formData.value.itens[i]
        if (!other.data_hora_inicio || !other.data_hora_fim) continue
        const oInicio = new Date(other.data_hora_inicio)
        const oFim = new Date(other.data_hora_fim)
        if (inicio < oFim && fim > oInicio) { ok = false; break }
      }

      if (ok) result.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`)
    }
  }
  return result
})

function aplicarSugestao(horaStr) {
  const idx = sugestaoItemIdx.value
  if (idx < 0) return
  const item = formData.value.itens[idx]
  item.data_hora_inicio = sugestaoData.value + 'T' + horaStr
  onInicioChange(item, idx)
  sugestaoItemIdx.value = -1
}

/** Abre o modal rápido de criação de cliente sem perder dados do agendamento */
function abrirModalClienteRapido() {
  formClienteRapido.value = { nome: '', telefone: '' }
  erroClienteRapido.value = ''
  showModalClienteRapido.value = true
}

async function salvarClienteRapido() {
  erroClienteRapido.value = ''
  savingClienteRapido.value = true
  try {
    const { data: novoCliente } = await api.post('/clientes/', formClienteRapido.value)
    clientes.value = [...clientes.value, novoCliente].sort((a, b) => a.nome.localeCompare(b.nome))
    formData.value.cliente_id = novoCliente.id
    clienteBuscaNome.value = novoCliente.nome
    showModalClienteRapido.value = false
  } catch (e) {
    erroClienteRapido.value = e.response?.data?.detail || 'Erro ao criar cliente.'
  } finally {
    savingClienteRapido.value = false
  }
}

/** Liga/desliga a visão em colunas por profissional */
function toggleColunaPorProfissional() {
  colunaPorProfissional.value = !colunaPorProfissional.value
}

/** Clique em slot de hora na visão diária: abre modal pré-preenchido */
function colunaSlotClick(profId, horaSlot) {
  const dt = colunaDia.value + 'T' + horaSlot
  abrirModalNovo(dt, profId)
}

/** Retorna apenas os profissionais habilitados para o serviço selecionado */
function profissionaisParaItem(item) {
  if (!item.servico_id) return profissionais.value
  return profissionais.value.filter(p =>
    p.servicos?.some(s => s.id === Number(item.servico_id))
  )
}

/** Classes de badge para cada status */
function statusBadgeClass(status) {
  return ({
    pendente:   'bg-yellow-100 text-yellow-800',
    confirmado: 'bg-blue-100 text-blue-800',
    concluido:  'bg-green-100 text-green-800',
    cancelado:  'bg-red-100 text-red-800',
  })[status] ?? 'bg-gray-100 text-gray-600'
}

// ─── Tarefas Internas ──────────────────────────────────────────────────────
const colunaTarefasDoDia = computed(() =>
  tarefas.value.filter(t => {
    const d = t.data_hora_inicio ? formatDateISOInSaoPaulo(new Date(t.data_hora_inicio)) : ''
    return d === colunaDia.value
  })
)

function colunaTarefaStyle(t) {
  const startMin = toMinutes(t.data_hora_inicio) - DAY_START_MINUTES
  const endIso = t.data_hora_fim ?? null
  const endMin = endIso ? toMinutes(endIso) - DAY_START_MINUTES : startMin + 60
  const top = (startMin / 30) * SLOT_HEIGHT
  const height = Math.max(((endMin - startMin) / 30) * SLOT_HEIGHT, SLOT_HEIGHT / 2)
  const c = t.concluida ? TAREFA_COLORS_DONE : TAREFA_COLORS
  return {
    top: top + 'px',
    height: height + 'px',
    backgroundColor: c.bg,
    border: `1px solid ${c.border}`,
  }
}

function abrirModalTarefa(dt = '', tarefa = null) {
  if (tarefa) {
    modalTarefaMode.value = 'edit'
    formTarefa.value = {
      id: tarefa.id,
      titulo: tarefa.titulo,
      descricao: tarefa.descricao || '',
      data_hora_inicio: toDatetimeLocal(tarefa.data_hora_inicio),
      data_hora_fim: toDatetimeLocal(tarefa.data_hora_fim),
      responsavel_id: tarefa.responsavel_id || null,
      concluida: tarefa.concluida,
    }
  } else {
    modalTarefaMode.value = 'create'
    const dtFmt = dt ? (dt.includes('T') ? dt.slice(0, 16) : dt + 'T09:00') : ''
    formTarefa.value = { id: null, titulo: '', descricao: '', data_hora_inicio: dtFmt, data_hora_fim: '', responsavel_id: null, concluida: false }
  }
  modalTarefaError.value = ''
  showModalTarefa.value = true
}

async function salvarTarefa() {
  modalTarefaError.value = ''
  if (!formTarefa.value.titulo.trim()) {
    modalTarefaError.value = 'Informe um título.'
    return
  }
  savingTarefa.value = true
  try {
    const payload = {
      titulo: formTarefa.value.titulo.trim(),
      descricao: formTarefa.value.descricao || null,
      data_hora_inicio: formTarefa.value.data_hora_inicio,
      data_hora_fim: formTarefa.value.data_hora_fim || null,
      responsavel_id: formTarefa.value.responsavel_id || null,
      concluida: formTarefa.value.concluida,
    }
    if (modalTarefaMode.value === 'edit') {
      await api.patch(`/tarefas/${formTarefa.value.id}`, payload)
    } else {
      await api.post('/tarefas/', payload)
    }
    showModalTarefa.value = false
    await fetchTarefas()
  } catch (e) {
    modalTarefaError.value = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    savingTarefa.value = false
  }
}

async function excluirTarefa(t) {
  if (!confirm(`Remover a tarefa "${t.titulo}"?`)) return
  await api.delete(`/tarefas/${t.id}`)
  detalheTarefa.value = null
  await fetchTarefas()
}

async function fetchTarefas() {
  try {
    const { data } = await api.get('/tarefas/')
    tarefas.value = data
  } catch (e) { console.error('Erro ao carregar tarefas:', e) }
}

async function salvarModal() {
  modalError.value = ''
  if (!formData.value.cliente_id) {
    modalError.value = 'Selecione um cliente da lista.'
    return
  }
  saving.value = true
  try {
    const payload = {
      cliente_id: formData.value.cliente_id,
      cor_hex: normalizarHexColor(formData.value.cor_hex),
      observacoes: formData.value.observacoes || null,
      itens: formData.value.itens.map(i => ({
        servico_id: i.servico_id,
        profissional_id: i.profissional_id,
        data_hora_inicio: i.data_hora_inicio,
        data_hora_fim: i.data_hora_fim || null,
      })),
    }
    if (modalMode.value === 'edit') {
      await api.put(`/agendamentos/${formData.value.id}`, payload)
    } else {
      await api.post('/agendamentos/', payload)
    }
    showModal.value = false
    toastSucesso(modalMode.value === 'edit' ? 'Agendamento atualizado!' : 'Agendamento criado!')
    await fetchAgendamentos()
  } catch (e) {
    modalError.value = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    saving.value = false
  }
}

function alterarStatus(id, status) {
  api.patch(`/agendamentos/${id}/status`, { status }).then(fetchAgendamentos)
}

function confirmarExcluirAg(ag) {
  agParaExcluir.value = ag
  detalheAg.value = null
}

async function excluirAgendamento() {
  if (!agParaExcluir.value) return
  excluindoAg.value = true
  try {
    await api.delete(`/agendamentos/${agParaExcluir.value.id}`)
    agParaExcluir.value = null
    await fetchAgendamentos()
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao excluir agendamento.')
  } finally {
    excluindoAg.value = false
  }
}

function totalAgPag(ag) {
  if (!ag?.itens) return '0.00'
  return ag.itens.reduce((sum, item) => sum + Number(item.servico?.preco || 0), 0).toFixed(2)
}

function setPagValorBase(preco) {
  const v = Number(preco).toFixed(2)
  basePagAg.value = v
  formPagAg.value.valor = v
  formPagAg.value.desconto = '0.00'
}

function abrirModalPagamento(ag) {
  agPagSelecionado.value = ag
  const total = totalAgPag(ag)
  basePagAg.value = total
  formPagAg.value = { valor: total, desconto: '0.00', metodo: '', novoStatus: '' }
  erroPagAg.value = ''
  modalPagAberto.value = true
}

watch(() => formPagAg.value.desconto, (desc) => {
  if (!agPagSelecionado.value) return
  const newValor = Math.max(0, Number(basePagAg.value) - Number(desc)).toFixed(2)
  if (Number(newValor) !== Number(formPagAg.value.valor)) formPagAg.value.valor = newValor
})

async function confirmarPagamentoAg() {
  savingPagAg.value = true
  erroPagAg.value = ''
  try {
    if (formPagAg.value.novoStatus) {
      await api.patch(`/agendamentos/${agPagSelecionado.value.id}/status`, {
        status: formPagAg.value.novoStatus,
      })
    }
    await api.post(`/agendamentos/${agPagSelecionado.value.id}/pagamento`, {
      valor: formPagAg.value.valor,
      metodo: formPagAg.value.metodo,
    })
    modalPagAberto.value = false
    await fetchAgendamentos()
  } catch (e) {
    erroPagAg.value = e.response?.data?.detail || 'Erro ao registrar pagamento.'
  } finally {
    savingPagAg.value = false
  }
}

async function fetchAgendamentos(options = {}) {
  const {
    silent = false,
    mesesPassados = 3,
    mesesFuturos = 4,
  } = options

  if (!silent) loading.value = true
  const hoje = new Date()
  // Janela configurável para permitir carga inicial rápida e hidratação em segundo plano.
  const inicio = new Date(hoje.getFullYear(), hoje.getMonth() - mesesPassados, 1)
  const fim = new Date(hoje.getFullYear(), hoje.getMonth() + mesesFuturos, 0)
  const params = {
    data_inicio: formatDateISOInSaoPaulo(inicio),
    data_fim: formatDateISOInSaoPaulo(fim),
  }
  if (filtroProfissional.value) params.profissional_id = filtroProfissional.value
  try {
    const { data } = await api.get('/agendamentos/', { params })
    agendamentos.value = data
  } catch (e) {
    console.error('Erro ao carregar agendamentos:', e)
  } finally {
    if (!silent) loading.value = false
  }
}

watch(filtroProfissional, () => fetchAgendamentos())

// ─── Clientes CRUD ─────────────────────────────────────────────────────────
const DIAS_SEMANA = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado']
function formatDataCliente(s) {
  if (!s) return ''
  const d = new Date(s)
  return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}/${d.getFullYear()}`
}
function formatHoraCliente(s) {
  if (!s) return ''
  return new Date(s).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' })
}
function diaSemanaCliente(s) {
  if (!s) return ''
  return DIAS_SEMANA[new Date(s).getDay()]
}
const historicoClienteItens = computed(() => {
  const items = []
  for (const ag of historicoCliente.value) {
    for (const item of ag.itens ?? []) items.push({ ...item, agStatus: ag.status })
  }
  return items.sort((a, b) => new Date(b.data_hora_inicio) - new Date(a.data_hora_inicio))
})

function abrirDrawerCliente(cliente = null) {
  clienteSelecionadoPainel.value = cliente
  formCliente.value = {
    nome: cliente?.nome || '',
    telefone: cliente?.telefone || '',
    observacoes: cliente?.observacoes || '',
    campos_dinamicos: cliente?.campos_dinamicos ? JSON.parse(JSON.stringify(cliente.campos_dinamicos)) : [],
  }
  erroCliente.value = ''
  editandoCamposPainel.value = false
  historicoCliente.value = []
  clienteDrawer.value = true
  if (cliente?.id) {
    // Busca o cliente completo para garantir todos os campos atualizados
    api.get(`/clientes/${cliente.id}`).then(r => {
      clienteSelecionadoPainel.value = r.data
      formCliente.value = {
        nome: r.data.nome || '',
        telefone: r.data.telefone || '',
        observacoes: r.data.observacoes || '',
        campos_dinamicos: r.data.campos_dinamicos ? JSON.parse(JSON.stringify(r.data.campos_dinamicos)) : [],
      }
    }).catch(() => {})
    fetchHistoricoCliente(cliente.id)
  }
}

async function fetchHistoricoCliente(clienteId) {
  loadingHistoricoCliente.value = true
  try {
    const { data } = await api.get(`/agendamentos/?cliente_id=${clienteId}`)
    historicoCliente.value = data
  } finally {
    loadingHistoricoCliente.value = false
  }
}

async function salvarCliente() {
  erroCliente.value = ''
  savingCliente.value = true
  try {
    const payload = {
      nome: formCliente.value.nome,
      telefone: formCliente.value.telefone || null,
      observacoes: formCliente.value.observacoes || null,
      campos_dinamicos: formCliente.value.campos_dinamicos.length ? formCliente.value.campos_dinamicos : null,
    }
    if (clienteSelecionadoPainel.value?.id) {
      const { data } = await api.patch(`/clientes/${clienteSelecionadoPainel.value.id}`, payload)
      clienteSelecionadoPainel.value = data
      toastSucesso('Cliente salvo com sucesso!')
    } else {
      const { data } = await api.post('/clientes/', payload)
      clienteSelecionadoPainel.value = data
      toastSucesso('Cliente criado com sucesso!')
      await fetchHistoricoCliente(data.id)
    }
    await fetchClientes()
  } catch (e) {
    erroCliente.value = e.response?.data?.detail || 'Erro ao salvar.'
  } finally {
    savingCliente.value = false
  }
}

async function removerCliente(c) {
  if (!confirm(`Remover o cliente "${c.nome}"?`)) return
  await api.delete(`/clientes/${c.id}`)
  if (clienteSelecionadoPainel.value?.id === c.id) clienteDrawer.value = false
  await fetchClientes()
}

async function fetchClientes() {
  loadingClientes.value = true
  const { data } = await api.get('/clientes/')
  clientes.value = data
  loadingClientes.value = false
}

// ─── Helpers ───────────────────────────────────────────────────────────────
function formatDateISOInSaoPaulo(value) {
  const d = value instanceof Date ? value : new Date(value)
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Sao_Paulo' }).format(d)
}

function toDatetimeLocal(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Sao_Paulo',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(d)
  const get = (type) => parts.find(p => p.type === type)?.value || '00'
  return `${get('year')}-${get('month')}-${get('day')}T${get('hour')}:${get('minute')}`
}

function carregarCoresFavoritas() {
  try {
    const raw = localStorage.getItem('agendamento-cores-favoritas')
    const list = raw ? JSON.parse(raw) : []
    if (!Array.isArray(list)) return
    coresFavoritas.value = list
      .map(c => normalizarHexColor(c))
      .filter(Boolean)
      .slice(0, 20)
  } catch {
    coresFavoritas.value = []
  }
}

function salvarCorFavorita() {
  const cor = normalizarHexColor(detalheCorSelecionada.value)
  if (!cor) return
  const merged = [cor, ...coresFavoritas.value.filter(c => c !== cor)].slice(0, 20)
  coresFavoritas.value = merged
  localStorage.setItem('agendamento-cores-favoritas', JSON.stringify(merged))
}

async function salvarCorAgendamento() {
  if (!detalheAg.value?.id) return
  const cor = normalizarHexColor(detalheCorSelecionada.value)
  try {
    await api.patch(`/agendamentos/${detalheAg.value.id}/cor`, { cor_hex: cor })
    detalheAg.value.cor_hex = cor
    await fetchAgendamentos()
    toastSucesso('Cor do agendamento atualizada!')
  } catch (e) {
    alert(e.response?.data?.detail || 'Erro ao salvar cor do agendamento.')
  }
}

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', timeZone: 'America/Sao_Paulo' })
}

function formatDateShort(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: '2-digit', timeZone: 'America/Sao_Paulo' })
}

async function fetchReferencias() {
  try {
    const [s, p] = await Promise.all([api.get('/servicos/'), api.get('/profissionais/')])
    servicos.value = s.data.filter(sv => sv.ativo !== false)
    profissionais.value = p.data
  } catch (e) { console.error('Erro ao carregar referências:', e) }
}

onMounted(async () => {
  carregarCoresFavoritas()

  // 1) Resposta rápida: janela menor para renderizar calendário mais cedo.
  await fetchAgendamentos({ mesesPassados: 1, mesesFuturos: 2 })

  // 2) Hidratação em segundo plano: dados completos e auxiliares sem travar a primeira pintura.
  setTimeout(() => {
    fetchAgendamentos({ silent: true, mesesPassados: 3, mesesFuturos: 4 })
    fetchClientes()
    fetchReferencias()
    fetchTarefas()
  }, 0)
})
</script>

<style>
.fc-wrapper .fc {
  font-family: inherit;
  height: 100%;
}
.fc-wrapper .fc-toolbar {
  padding: 4px 8px !important;
}
.fc-wrapper .fc-toolbar-title {
  font-size: 0.9rem;
  font-weight: 700;
}
.fc-wrapper .fc-button {
  background: white !important;
  border: 1px solid #e5e7eb !important;
  color: #374151 !important;
  font-size: 0.7rem !important;
  font-weight: 500 !important;
  padding: 3px 8px !important;
  box-shadow: none !important;
  border-radius: 6px !important;
}
.fc-wrapper .fc-button:hover {
  background: #f9fafb !important;
}
.fc-wrapper .fc-button-active,
.fc-wrapper .fc-button:focus {
  background: #e11d48 !important;
  border-color: #e11d48 !important;
  color: white !important;
  outline: none !important;
}
.fc-wrapper .fc-timegrid-slot {
  height: 2rem !important;
}
/* Evento timegrid: clip garantido no nível mais externo */
.fc-wrapper .fc-timegrid-event {
  overflow: hidden !important;
}
/* Zerar o padding que o FullCalendar coloca no fc-event-main;
   nós controlamos o espaçamento via fc-event-inner / fc-ev-chip */
.fc-wrapper .fc-timegrid-event .fc-event-main {
  padding: 0 !important;
  overflow: hidden !important;
  height: 100% !important;
}
.fc-wrapper .fc-event {
  border-radius: 4px !important;
  cursor: pointer !important;
  padding: 0 !important;
  overflow: hidden !important;
}
.fc-wrapper .fc-event-main,
.fc-wrapper .fc-event-main-frame {
  overflow: hidden !important;
  height: 100% !important;
  min-height: 0 !important;
  max-height: 100% !important;
}
/* Layout flex-column (2-3 linhas) */
.fc-wrapper .fc-event-inner {
  display: flex;
  flex-direction: column;
  gap: 1px;
  overflow: hidden;
  height: 100%;
  min-height: 0;
  max-height: 100%;
  padding: 2px 4px;
  box-sizing: border-box;
}
/* Chip inline de linha única para eventos curtos (≤30 min) */
.fc-wrapper .fc-ev-chip {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 100%;
  padding: 1px 4px;
  overflow: hidden;
  min-width: 0;
}
.fc-wrapper .fc-ev-chip-name {
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
  line-height: 1.2;
}
.fc-wrapper .fc-ev-chip-sep {
  font-size: 0.6rem;
  opacity: 0.5;
  flex-shrink: 0;
}
.fc-wrapper .fc-ev-chip-time {
  font-size: 0.65rem;
  opacity: 0.75;
  flex-shrink: 0;
  white-space: nowrap;
}
.fc-wrapper .fc-ev-title {
  font-weight: 600;
  font-size: 0.72rem;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}
.fc-wrapper .fc-ev-sub {
  font-size: 0.65rem;
  opacity: 0.85;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 1;
  min-height: 0;
  line-height: 1.2;
}
.fc-wrapper .fc-col-header-cell {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  padding: 6px 0;
}
.fc-wrapper .fc-timegrid-slot-label {
  font-size: 0.7rem;
  color: #9ca3af;
}
.fc-wrapper .fc-now-indicator-line {
  border-color: #e11d48;
}
.fc-wrapper .fc-now-indicator-arrow {
  border-top-color: #e11d48;
  border-bottom-color: #e11d48;
}
.fc-wrapper .fc-toolbar {
  padding: 8px 12px !important;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
