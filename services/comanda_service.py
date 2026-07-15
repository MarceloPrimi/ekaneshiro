"""Lógica de negócio para o sistema de Comanda.

Fluxo típico:
    1. abrir_comanda()                        → cria comanda com status=aberta
    2. adicionar_itens_agendamento()          → vincula serviços de um agendamento
    3. adicionar_item_avulso()                → (opcional) inclui serviços extras
    4. registrar_pagamento()                  → registra um ou mais pagamentos
    5. fechar_comanda()                       → valida e fecha a comanda

Regras de negócio:
    - Só comandas abertas podem receber itens ou pagamentos.
    - Um ItemAgendamento só pode estar em UMA comanda (restrição UNIQUE no banco).
    - O total pago deve cobrir o total dos itens para fechar a comanda.
    - Troco em dinheiro é convertido em crédito para o pagador.
    - Crédito do cliente é validado antes de ser consumido.
"""

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from db.models import (
    Agendamento,
    Cliente,
    Comanda,
    ItemAgendamento,
    ItemComanda,
    PagamentoComanda,
    ProfissionalServico,
    Servico,
    StatusAgendamentoEnum,
    StatusComandaEnum,
    TipoItemComandaEnum,
)
from schemas.comandas import (
    ComandaCreate,
    ItemAgendamentoComandaCreate,
    ItemAvulsoCreate,
    PagamentoComandaCreate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_comanda_aberta_ou_404(db: Session, comanda_id: int) -> Comanda:
    comanda = (
        db.query(Comanda)
        .options(
            joinedload(Comanda.itens),
            joinedload(Comanda.pagamentos),
        )
        .filter(Comanda.id == comanda_id)
        .first()
    )
    if not comanda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comanda não encontrada.",
        )
    if comanda.status != StatusComandaEnum.aberta:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Comanda #{comanda_id} está {comanda.status.value} e não pode ser alterada.",
        )
    return comanda


def _preco_profissional(db: Session, profissional_id: int, servico_id: int) -> Decimal:
    """Retorna o preço que o profissional cobra pelo serviço.

    Prioridade:
        1. ProfissionalServico.preco_proprio (preço personalizado do profissional)
        2. Servico.preco (preço padrão do catálogo)
    """
    vinculo = (
        db.query(ProfissionalServico)
        .filter_by(profissional_id=profissional_id, servico_id=servico_id)
        .first()
    )
    if vinculo and vinculo.preco_proprio is not None:
        return Decimal(str(vinculo.preco_proprio))

    servico = db.get(Servico, servico_id)
    return Decimal(str(servico.preco)) if servico else Decimal("0.00")


def _calcular_total_itens(comanda: Comanda) -> Decimal:
    return sum(
        Decimal(str(i.valor_unitario)) * i.quantidade - Decimal(str(i.desconto))
        for i in comanda.itens
    )


def _calcular_total_pago(comanda: Comanda) -> Decimal:
    return sum(Decimal(str(p.valor)) for p in comanda.pagamentos)


# ---------------------------------------------------------------------------
# Abrir comanda
# ---------------------------------------------------------------------------

def abrir_comanda(
    db: Session,
    payload: ComandaCreate,
    criada_por_id: int,
) -> Comanda:
    comanda = Comanda(
        status=StatusComandaEnum.aberta,
        observacoes=payload.observacoes,
        criada_por_id=criada_por_id,
    )
    db.add(comanda)
    db.commit()
    db.refresh(comanda)
    return comanda


# ---------------------------------------------------------------------------
# Adicionar itens de um agendamento existente
# ---------------------------------------------------------------------------

def adicionar_itens_agendamento(
    db: Session,
    comanda_id: int,
    payload: ItemAgendamentoComandaCreate,
) -> list[ItemComanda]:
    """Cria um ItemComanda para cada ItemAgendamento do agendamento informado.

    Cada serviço/profissional do agendamento vira uma linha separada na comanda,
    permitindo rastreamento financeiro individual por profissional.
    """
    comanda = _get_comanda_aberta_ou_404(db, comanda_id)

    agendamento = (
        db.query(Agendamento)
        .options(joinedload(Agendamento.itens))
        .filter(Agendamento.id == payload.agendamento_id)
        .first()
    )
    if not agendamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agendamento {payload.agendamento_id} não encontrado.",
        )
    if agendamento.status in (
        StatusAgendamentoEnum.cancelado,
        StatusAgendamentoEnum.pre_agendamento,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não é possível cobrar agendamento cancelado ou em pré-agendamento.",
        )
    if not agendamento.itens:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="O agendamento não possui itens para incluir na comanda.",
        )

    novos_itens: list[ItemComanda] = []
    for item_ag in agendamento.itens:
        # Verifica se este item já está em alguma comanda (UNIQUE constraint no banco)
        ja_existe = (
            db.query(ItemComanda)
            .filter(ItemComanda.item_agendamento_id == item_ag.id)
            .first()
        )
        if ja_existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"O item de agendamento {item_ag.id} "
                    f"(serviço: {item_ag.servico.nome}) "
                    f"já está na comanda #{ja_existe.comanda_id}."
                ),
            )

        # Preço: override manual > preco_proprio do profissional > preco padrão do serviço
        if payload.valor_unitario_override is not None:
            valor = payload.valor_unitario_override
        else:
            valor = _preco_profissional(db, item_ag.profissional_id, item_ag.servico_id)

        item_comanda = ItemComanda(
            comanda_id=comanda.id,
            tipo=TipoItemComandaEnum.agendamento,
            agendamento_id=agendamento.id,
            item_agendamento_id=item_ag.id,
            cliente_id=payload.cliente_id,
            profissional_id=item_ag.profissional_id,
            servico_id=item_ag.servico_id,
            descricao=None,
            valor_unitario=valor,
            quantidade=1,
            desconto=Decimal("0.00"),
        )
        db.add(item_comanda)
        novos_itens.append(item_comanda)

    db.commit()
    for item in novos_itens:
        db.refresh(item)
    return novos_itens


# ---------------------------------------------------------------------------
# Adicionar item avulso (serviço ou produto não agendado)
# ---------------------------------------------------------------------------

def adicionar_item_avulso(
    db: Session,
    comanda_id: int,
    payload: ItemAvulsoCreate,
) -> ItemComanda:
    """Adiciona um serviço ou produto que não foi agendado previamente."""
    comanda = _get_comanda_aberta_ou_404(db, comanda_id)

    cliente = db.get(Cliente, payload.cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {payload.cliente_id} não encontrado.",
        )

    tipo = (
        TipoItemComandaEnum.produto
        if payload.tipo == "produto"
        else TipoItemComandaEnum.servico_avulso
    )

    item_comanda = ItemComanda(
        comanda_id=comanda.id,
        tipo=tipo,
        agendamento_id=None,
        item_agendamento_id=None,
        cliente_id=payload.cliente_id,
        profissional_id=payload.profissional_id,
        servico_id=payload.servico_id,
        descricao=payload.descricao,
        valor_unitario=payload.valor_unitario,
        quantidade=payload.quantidade,
        desconto=payload.desconto,
    )
    db.add(item_comanda)
    db.commit()
    db.refresh(item_comanda)
    return item_comanda


# ---------------------------------------------------------------------------
# Remover item da comanda
# ---------------------------------------------------------------------------

def remover_item(db: Session, comanda_id: int, item_id: int) -> None:
    """Remove um item de uma comanda aberta."""
    comanda = _get_comanda_aberta_ou_404(db, comanda_id)

    item = (
        db.query(ItemComanda)
        .filter(ItemComanda.id == item_id, ItemComanda.comanda_id == comanda.id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado nesta comanda.",
        )

    db.delete(item)
    db.commit()


# ---------------------------------------------------------------------------
# Registrar pagamento
# ---------------------------------------------------------------------------

def registrar_pagamento(
    db: Session,
    comanda_id: int,
    payload: PagamentoComandaCreate,
    registrado_por_id: int,
) -> PagamentoComanda:
    """Registra um pagamento (parcial ou total) na comanda.

    Suporta split: você pode chamar este endpoint múltiplas vezes com métodos
    diferentes (ex: R$50 em PIX + R$30 em dinheiro).
    """
    comanda = _get_comanda_aberta_ou_404(db, comanda_id)

    if not comanda.itens:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Adicione itens à comanda antes de registrar pagamento.",
        )

    # Resolve o cliente pagador (para crédito/troco)
    pagador_id = payload.pagador_cliente_id
    if pagador_id is None and comanda.itens:
        pagador_id = comanda.itens[0].cliente_id

    pagador: Cliente | None = db.get(Cliente, pagador_id) if pagador_id else None

    credito = payload.credito_utilizado
    if credito > 0:
        if pagador is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Informe 'pagador_cliente_id' para usar crédito.",
            )
        if credito > pagador.saldo_credito:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Crédito insuficiente. Saldo disponível: R$ {pagador.saldo_credito:.2f}."
                ),
            )
        pagador.saldo_credito -= credito

    pagamento = PagamentoComanda(
        comanda_id=comanda.id,
        valor=payload.valor,
        metodo=payload.metodo,
        credito_utilizado=credito,
        pagador_cliente_id=pagador_id,
        registrado_por_id=registrado_por_id,
    )
    db.add(pagamento)

    # Troco em dinheiro → vira crédito para o pagador
    if payload.metodo == "dinheiro" and pagador is not None:
        total_itens = _calcular_total_itens(comanda)
        total_ja_pago = _calcular_total_pago(comanda)  # ainda sem o pagamento atual
        valor_devido = total_itens - total_ja_pago - credito
        if payload.valor > valor_devido > 0:
            troco = payload.valor - valor_devido
            pagador.saldo_credito += troco

    db.commit()
    db.refresh(pagamento)
    return pagamento


# ---------------------------------------------------------------------------
# Fechar comanda
# ---------------------------------------------------------------------------

def fechar_comanda(db: Session, comanda_id: int) -> Comanda:
    """Valida cobertura total e fecha a comanda.

    Ao fechar:
    - Verifica que o valor total pago cobre todos os itens.
    - Marca os agendamentos vinculados como 'confirmado'.
    - Define fechada_em com o timestamp atual.
    """
    comanda = _get_comanda_aberta_ou_404(db, comanda_id)

    if not comanda.itens:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não é possível fechar uma comanda sem itens.",
        )

    total_itens = _calcular_total_itens(comanda)
    total_pago = _calcular_total_pago(comanda)

    if total_pago < total_itens:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Pagamento insuficiente. "
                f"Total: R$ {total_itens:.2f} | Pago: R$ {total_pago:.2f} | "
                f"Restante: R$ {total_itens - total_pago:.2f}."
            ),
        )

    # Confirma os agendamentos vinculados aos itens da comanda
    agendamento_ids = {
        item.agendamento_id
        for item in comanda.itens
        if item.agendamento_id is not None
    }
    for ag_id in agendamento_ids:
        agendamento = db.get(Agendamento, ag_id)
        if agendamento and agendamento.status not in (
            StatusAgendamentoEnum.cancelado,
            StatusAgendamentoEnum.concluido,
        ):
            agendamento.status = StatusAgendamentoEnum.confirmado

    comanda.status = StatusComandaEnum.fechada
    comanda.fechada_em = datetime.utcnow()

    db.commit()
    db.refresh(comanda)
    return comanda


# ---------------------------------------------------------------------------
# Cancelar comanda
# ---------------------------------------------------------------------------

def cancelar_comanda(db: Session, comanda_id: int) -> Comanda:
    """Cancela uma comanda aberta e estorna créditos consumidos."""
    comanda = _get_comanda_aberta_ou_404(db, comanda_id)

    # Estorna créditos que já foram consumidos nos pagamentos desta comanda
    for pagamento in comanda.pagamentos:
        if pagamento.credito_utilizado > 0 and pagamento.pagador_cliente_id:
            pagador = db.get(Cliente, pagamento.pagador_cliente_id)
            if pagador:
                pagador.saldo_credito += Decimal(str(pagamento.credito_utilizado))

    comanda.status = StatusComandaEnum.cancelada
    db.commit()
    db.refresh(comanda)
    return comanda
