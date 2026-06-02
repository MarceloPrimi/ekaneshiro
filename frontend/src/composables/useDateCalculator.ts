// useDateCalculator.ts — Composable da Calculadora de Antecipação/Projeção

import { ref, computed, watch } from 'vue'

type Unidade = 'days' | 'weeks'

const PT_DIAS_SEMANA = [
  'Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira',
  'Quinta-feira', 'Sexta-feira', 'Sábado',
]

export function useDateCalculator(dataBaseRef: { value: string | null }) {
  const quantidade = ref<number | null>(null)
  const unidade = ref<Unidade>('days')

  /** Data resultante após soma */
  const dataResultante = computed<Date | null>(() => {
    if (!quantidade.value || !dataBaseRef.value) return null
    const qtd = Number(quantidade.value)
    if (!Number.isFinite(qtd) || qtd <= 0) return null

    const base = new Date(dataBaseRef.value)
    if (isNaN(base.getTime())) return null

    if (unidade.value === 'days') {
      base.setDate(base.getDate() + qtd)
    } else {
      base.setDate(base.getDate() + qtd * 7)
    }
    return base
  })

  /** String ISO (yyyy-MM-dd) para preencher o input de data do formulário */
  const dataResultanteISO = computed<string>(() => {
    if (!dataResultante.value) return ''
    return dataResultante.value.toISOString().split('T')[0]
  })

  /** Texto legível para o usuário (ex: "Isso cairá em uma Terça-feira, 14/06/2026") */
  const descricaoResultado = computed<string>(() => {
    if (!dataResultante.value) return ''
    const d = dataResultante.value
    const nomeDia = PT_DIAS_SEMANA[d.getDay()]
    const dataFmt = d.toLocaleDateString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
    })
    return `Isso cairá em uma ${nomeDia}, ${dataFmt}`
  })

  function resetar() {
    quantidade.value = null
    unidade.value = 'days'
  }

  return {
    quantidade,
    unidade,
    dataResultanteISO,
    descricaoResultado,
    resetar,
  }
}
