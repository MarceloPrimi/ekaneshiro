<script setup lang="ts">
// CalendarClickModal.vue — Pop-over de decisão ao clicar na célula do calendário
// Apresenta: [Nova Tarefa] ou [Novo Agendamento]

const props = defineProps<{
  /** Data/hora do slot clicado (ISO string) */
  dataHora: string | null
  show: boolean
  /** Posição do popover (px) relativa ao viewport */
  posX?: number
  posY?: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select:agendamento', dataHora: string): void
  (e: 'select:tarefa', dataHora: string): void
}>()

function escolher(tipo: 'agendamento' | 'tarefa') {
  if (!props.dataHora) return
  if (tipo === 'agendamento') {
    emit('select:agendamento', props.dataHora)
  } else {
    emit('select:tarefa', props.dataHora)
  }
  emit('close')
}

function formataDataHora(dt: string | null) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('pt-BR', {
    weekday: 'short', day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}
</script>

<template>
  <Teleport to="body">
    <!-- Overlay transparente para fechar ao clicar fora -->
    <div
      v-if="show"
      class="fixed inset-0 z-40"
      @click="emit('close')"
      aria-hidden="true"
    />

    <Transition name="popover">
      <div
        v-if="show"
        class="fixed z-50 bg-white border border-gray-100 rounded-2xl shadow-2xl p-3 w-64"
        :style="{
          top: `${posY ?? 120}px`,
          left: `${posX ?? 120}px`,
        }"
        role="dialog"
        aria-modal="true"
        aria-label="Criar novo item no calendário"
      >
        <!-- Cabeçalho com data/hora -->
        <p class="text-[11px] text-gray-400 font-semibold uppercase tracking-wider mb-2 text-center">
          {{ formataDataHora(dataHora) }}
        </p>

        <p class="text-xs text-gray-500 text-center mb-3">O que deseja criar?</p>

        <!-- Botão: Novo Agendamento -->
        <button
          class="w-full flex items-center gap-3 px-3 py-3 rounded-xl bg-rose-50 hover:bg-rose-100 transition-colors text-left mb-2 focus:outline-none focus:ring-2 focus:ring-rose-300"
          @click="escolher('agendamento')"
        >
          <span class="w-9 h-9 flex items-center justify-center bg-rose-500 rounded-lg text-white text-lg shrink-0">📅</span>
          <div>
            <p class="text-sm font-semibold text-rose-700">Novo Agendamento</p>
            <p class="text-[11px] text-rose-400 leading-tight">Cliente, serviço, profissional</p>
          </div>
        </button>

        <!-- Botão: Nova Tarefa -->
        <button
          class="w-full flex items-center gap-3 px-3 py-3 rounded-xl bg-indigo-50 hover:bg-indigo-100 transition-colors text-left focus:outline-none focus:ring-2 focus:ring-indigo-300"
          @click="escolher('tarefa')"
        >
          <span class="w-9 h-9 flex items-center justify-center bg-indigo-500 rounded-lg text-white text-lg shrink-0">📝</span>
          <div>
            <p class="text-sm font-semibold text-indigo-700">Nova Tarefa</p>
            <p class="text-[11px] text-indigo-400 leading-tight">Lembrete interno, sem cliente</p>
          </div>
        </button>

        <!-- Botão fechar (acessibilidade) -->
        <button
          class="mt-3 w-full text-center text-xs text-gray-400 hover:text-gray-600 py-1"
          @click="emit('close')"
        >Cancelar</button>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.popover-enter-active,
.popover-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.popover-enter-from,
.popover-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-6px);
}
</style>
