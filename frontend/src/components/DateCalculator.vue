<script setup lang="ts">
// DateCalculator.vue — Widget embutível no formulário de agendamento

import { ref, computed, watch } from 'vue'
import { useDateCalculator } from '@/composables/useDateCalculator'

const props = defineProps<{
  /** Data base (yyyy-MM-dd) — normalmente "hoje" ou data de início do agendamento */
  dataBase: string | null
}>()

const emit = defineEmits<{
  /** Emite a data calculada no formato ISO (yyyy-MM-dd) para preencher o campo pai */
  (e: 'update:dataFinal', val: string): void
}>()

// Proxy reativo para o composable aceitar ref
const dataBaseProxy = computed(() => props.dataBase)

const {
  quantidade,
  unidade,
  dataResultanteISO,
  descricaoResultado,
  resetar,
} = useDateCalculator(dataBaseProxy)

// Quando o resultado muda, notifica o formulário pai
watch(dataResultanteISO, (val) => {
  if (val) emit('update:dataFinal', val)
})

const UNIDADES = [
  { value: 'days',  label: 'Dias' },
  { value: 'weeks', label: 'Semanas' },
]
</script>

<template>
  <fieldset class="border border-dashed border-indigo-200 rounded-xl p-3 bg-indigo-50/40">
    <legend class="text-xs font-semibold text-indigo-600 px-1">⏩ Calculadora de Antecipação</legend>

    <div class="flex items-center gap-2">
      <!-- Input numérico -->
      <input
        v-model.number="quantidade"
        type="number"
        min="1"
        max="999"
        placeholder="Ex: 40"
        class="w-24 border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        aria-label="Quantidade"
      />

      <!-- Seletor de unidade -->
      <select
        v-model="unidade"
        class="border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-300"
        aria-label="Unidade de tempo"
      >
        <option v-for="u in UNIDADES" :key="u.value" :value="u.value">{{ u.label }}</option>
      </select>

      <!-- Botão de reset -->
      <button
        type="button"
        class="text-gray-400 hover:text-red-400 text-lg leading-none"
        title="Limpar calculadora"
        @click="resetar()"
        aria-label="Limpar calculadora"
      >×</button>
    </div>

    <!-- Resultado legível -->
    <Transition name="fade">
      <p
        v-if="descricaoResultado"
        class="mt-2 text-xs font-medium text-indigo-700 flex items-center gap-1"
      >
        <span class="text-base">📅</span>
        {{ descricaoResultado }}
      </p>
    </Transition>
  </fieldset>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
