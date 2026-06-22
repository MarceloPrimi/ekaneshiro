<script setup lang="ts">
// AgendamentoCard.vue — Card de agendamento com mini etiquetas e categoria de cor

interface Servico {
  nome: string
}
interface Profissional {
  nome: string
}
interface Item {
  data_hora_inicio: string
  data_hora_fim: string
  servico: Servico
  profissional: Profissional
}
interface Categoria {
  id: number
  nome: string
  cor_hex: string
}
interface Agendamento {
  id: number
  cliente?: { nome: string }
  status: string
  cor_hex?: string | null
  itens: Item[]
  mini_etiquetas?: string[] | null
  primeira_vez?: boolean
  categoria?: Categoria | null
  recurrence_rule?: string | null
  observacoes?: string | null
}

// Catálogo de mini etiquetas — espelho do backend
const ETIQUETA_MAP: Record<string, { emoji: string; label: string }> = {
  urgente:      { emoji: '🚀', label: 'Urgente' },
  pago:         { emoji: '💰', label: 'Pago' },
  falta_doc:    { emoji: '⚠️', label: 'Falta Documento' },
  confirmado:   { emoji: '✅', label: 'Confirmado' },
  retorno:      { emoji: '🔄', label: 'Retorno' },
  vip:          { emoji: '⭐', label: 'VIP' },
  primeira_vez: { emoji: '✨', label: 'Primeira Vez' },
}

// Cores por status — bandeirinha no canto (paleta escura)
const STATUS_FLAG: Record<string, { color: string; label: string }> = {
  pendente:        { color: '#4b5563', label: 'Pendente' },
  confirmado:      { color: '#15803d', label: 'Confirmado' },
  concluido:       { color: '#1d4ed8', label: 'Concluído' },
  pre_agendamento: { color: '#b91c1c', label: 'Pré-agendamento' },
  cancelado:       { color: '#b91c1c', label: 'Cancelado' },
}
const statusFlag = STATUS_FLAG[props.agendamento.status] ?? { color: '#9ca3af', label: props.agendamento.status }

const RECURRENCE_LABEL: Record<string, string> = {
  'FREQ=WEEKLY;INTERVAL=1':  '↻ Semanal',
  'FREQ=WEEKLY;INTERVAL=2':  '↻ Quinzenal',
  'FREQ=MONTHLY;INTERVAL=1': '↻ Mensal',
}

const props = defineProps<{
  agendamento: Agendamento
  compact?: boolean
}>()

const emit = defineEmits<{
  (e: 'click', ag: Agendamento): void
}>()

// Cor do card: categoria tem prioridade sobre cor_hex avulsa
const cardColor = props.agendamento.categoria?.cor_hex
  ?? props.agendamento.cor_hex
  ?? '#e2e8f0'

// Hora do primeiro item
const horaInicio = (dt: string) =>
  new Date(dt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })

// Etiquetas visíveis no card
const etiquetasVisiveis = (props.agendamento.mini_etiquetas ?? [])
  .map(k => ETIQUETA_MAP[k])
  .filter(Boolean)

const recorrenciaLabel = props.agendamento.recurrence_rule
  ? (RECURRENCE_LABEL[props.agendamento.recurrence_rule] ?? '↻ Recorrente')
  : null
</script>

<template>
  <div
    class="relative rounded-xl overflow-hidden cursor-pointer shadow-sm hover:shadow-md transition-shadow select-none"
    :style="{ borderLeft: `4px solid ${cardColor}`, backgroundColor: `${cardColor}18` }"
    @click="emit('click', agendamento)"
    role="button"
    :aria-label="`Agendamento de ${agendamento.cliente?.nome}`"
  >
    <!-- Bandeirinha de status — canto superior direito -->
    <div
      class="absolute top-0 right-0 w-0 h-0 z-10"
      :title="statusFlag.label"
      :aria-label="statusFlag.label"
      :style="{
        borderTop: `20px solid ${statusFlag.color}`,
        borderLeft: '20px solid transparent',
      }"
    ></div>

    <!-- Mini etiquetas: abaixo da bandeirinha -->
    <div v-if="etiquetasVisiveis.length" class="absolute top-5 right-1 flex flex-col gap-0.5 z-10 items-end">
      <span
        v-for="(et, idx) in etiquetasVisiveis"
        :key="idx"
        :title="et.label"
        class="text-xs leading-none select-none"
        :aria-label="et.label"
      >{{ et.emoji }}</span>
    </div>

    <div class="px-2.5 py-2 pr-7">
      <!-- Hora -->
      <p class="text-[11px] font-semibold text-gray-500 leading-none mb-0.5">
        {{ horaInicio(agendamento.itens[0]?.data_hora_inicio) }}
      </p>

      <!-- Nome do cliente -->
      <p class="text-sm font-bold text-gray-800 truncate leading-snug">
        {{ agendamento.cliente?.nome ?? '—' }}
      </p>

      <!-- Categoria label (tooltip já existe via CSS; exibimos como subheader) -->
      <p
        v-if="agendamento.categoria"
        class="text-[11px] font-medium truncate leading-none mt-0.5"
        :style="{ color: cardColor }"
      >
        {{ agendamento.categoria.nome }}
      </p>

      <!-- Serviços (compact: apenas o primeiro) -->
      <p class="text-[11px] text-gray-500 truncate leading-tight mt-0.5">
        {{ agendamento.itens.map(i => i.servico.nome).slice(0, compact ? 1 : 3).join(', ') }}
        <span v-if="compact && agendamento.itens.length > 1" class="text-gray-400">
          +{{ agendamento.itens.length - 1 }}
        </span>
      </p>

      <!-- Badge de recorrência -->
      <span
        v-if="recorrenciaLabel"
        class="inline-block mt-1 text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-white/60 text-gray-600 border border-gray-200"
      >
        {{ recorrenciaLabel }}
      </span>
    </div>
  </div>
</template>
