<script setup lang="ts">
// MiniEtiquetasPicker.vue — Seletor de mini etiquetas para o formulário de agendamento

type Codigo = string

interface Etiqueta {
  codigo: Codigo
  emoji: string
  label: string
}

const CATALOGO: Etiqueta[] = [
  { codigo: 'urgente',      emoji: '🚀', label: 'Urgente' },
  { codigo: 'pago',         emoji: '💰', label: 'Pago' },
  { codigo: 'falta_doc',    emoji: '⚠️', label: 'Falta Documento' },
  { codigo: 'confirmado',   emoji: '✅', label: 'Confirmado' },
  { codigo: 'retorno',      emoji: '🔄', label: 'Retorno' },
  { codigo: 'vip',          emoji: '⭐', label: 'VIP' },
  { codigo: 'primeira_vez', emoji: '✨', label: 'Primeira Vez (automático)' },
]

const props = defineProps<{
  modelValue: Codigo[]
  /** Quando true, exibe 'primeira_vez' como desabilitado (já detectado automaticamente) */
  primeiraVezDetectada?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: Codigo[]): void
}>()

function toggle(codigo: Codigo) {
  // primeira_vez é injetado automaticamente pelo backend — não pode ser desmarcado manualmente
  if (codigo === 'primeira_vez') return

  const selecionadas = [...props.modelValue]
  const idx = selecionadas.indexOf(codigo)
  if (idx >= 0) {
    selecionadas.splice(idx, 1)
  } else {
    selecionadas.push(codigo)
  }
  emit('update:modelValue', selecionadas)
}

function estaAtiva(codigo: Codigo): boolean {
  if (codigo === 'primeira_vez') return props.primeiraVezDetectada ?? false
  return props.modelValue.includes(codigo)
}
</script>

<template>
  <fieldset class="border border-dashed border-amber-200 rounded-xl p-3 bg-amber-50/30">
    <legend class="text-xs font-semibold text-amber-600 px-1">🏷️ Mini Etiquetas</legend>

    <div class="flex flex-wrap gap-2 mt-1">
      <button
        v-for="et in CATALOGO"
        :key="et.codigo"
        type="button"
        :disabled="et.codigo === 'primeira_vez'"
        :title="et.codigo === 'primeira_vez' && primeiraVezDetectada
          ? 'Adicionado automaticamente — é a primeira visita deste cliente!'
          : et.label"
        :class="[
          'flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-all select-none',
          estaAtiva(et.codigo)
            ? 'bg-amber-400 border-amber-500 text-white shadow-sm'
            : 'bg-white border-gray-200 text-gray-600 hover:border-amber-300 hover:bg-amber-50',
          et.codigo === 'primeira_vez' ? 'cursor-default opacity-80' : 'cursor-pointer',
        ]"
        @click="toggle(et.codigo)"
        :aria-pressed="estaAtiva(et.codigo)"
      >
        <span class="text-base leading-none">{{ et.emoji }}</span>
        <span>{{ et.label }}</span>
        <span
          v-if="et.codigo === 'primeira_vez' && primeiraVezDetectada"
          class="ml-1 text-[10px] bg-white/40 text-white px-1 rounded"
        >auto</span>
      </button>
    </div>
  </fieldset>
</template>
