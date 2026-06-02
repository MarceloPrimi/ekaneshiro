// categoriasApi.ts — Funções de acesso à API de Categorias de Agendamento
import api from '@/api/client'

export interface CategoriaAgendamento {
  id: number
  nome: string
  cor_hex: string
  ativo: boolean
}

export interface CategoriaCreate {
  nome: string
  cor_hex: string
}

export interface CategoriaUpdate {
  nome?: string
  cor_hex?: string
  ativo?: boolean
}

export const categoriasApi = {
  async listar(apenasAtivas = true): Promise<CategoriaAgendamento[]> {
    const { data } = await api.get('/categorias-agendamento/', {
      params: { apenas_ativas: apenasAtivas },
    })
    return data
  },

  async criar(payload: CategoriaCreate): Promise<CategoriaAgendamento> {
    const { data } = await api.post('/categorias-agendamento/', payload)
    return data
  },

  async editar(id: number, payload: CategoriaUpdate): Promise<CategoriaAgendamento> {
    const { data } = await api.patch(`/categorias-agendamento/${id}`, payload)
    return data
  },

  async excluir(id: number): Promise<void> {
    await api.delete(`/categorias-agendamento/${id}`)
  },
}
