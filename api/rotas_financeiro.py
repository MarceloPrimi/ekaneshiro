"""Módulo Financeiro — Controle de Despesas (admin only)."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from api.dependencias import get_current_admin
from db.database import get_db
from db.models import CategoriaDespesa, Despesa, Usuario
from schemas.despesas import (
    CategoriaDespesaCreate,
    CategoriaDespesaResponse,
    DespesaCreate,
    DespesaResponse,
    DespesaStatusUpdate,
    DespesaUpdate,
    DespesasPainelResponse,
    DespesasResumoResponse,
    ImportacaoDespesasResponse,
)
from services import despesa_service

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])


def _get_despesa_ou_404(despesa_id: int, db: Session) -> Despesa:
    despesa = (
        db.query(Despesa)
        .options(joinedload(Despesa.categoria))
        .filter(Despesa.id == despesa_id)
        .first()
    )
    if not despesa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despesa não encontrada.")
    return despesa


@router.get(
    "/categorias-despesa",
    response_model=list[CategoriaDespesaResponse],
    summary="Listar categorias de despesa",
)
def listar_categorias(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
    apenas_ativas: bool = Query(True),
):
    query = db.query(CategoriaDespesa)
    if apenas_ativas:
        query = query.filter(CategoriaDespesa.ativo == True)
    return query.order_by(CategoriaDespesa.nome).all()


@router.post(
    "/categorias-despesa",
    response_model=CategoriaDespesaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar tipo de despesa",
)
def criar_categoria(
    payload: CategoriaDespesaCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    nome = payload.nome.strip()
    if not nome:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nome do tipo de despesa é obrigatório.",
        )
    from sqlalchemy import func as sa_func

    existente = (
        db.query(CategoriaDespesa)
        .filter(sa_func.lower(CategoriaDespesa.nome) == nome.lower())
        .first()
    )
    if existente:
        if not existente.ativo:
            existente.ativo = True
            resp = {"id": existente.id, "nome": existente.nome, "ativo": True}
            db.commit()
            return resp
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um tipo de despesa com esse nome.",
        )
    categoria = CategoriaDespesa(nome=nome, ativo=True)
    db.add(categoria)
    db.flush()
    resp = {"id": categoria.id, "nome": categoria.nome, "ativo": categoria.ativo}
    db.commit()
    return resp


@router.get(
    "/despesas/painel",
    response_model=DespesasPainelResponse,
    summary="Painel: lista + resumo em uma chamada",
)
def painel_despesas(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
    mes: str | None = Query(None, description="YYYY-MM"),
    status_filtro: str | None = Query(None, alias="status", description="pago | pendente"),
    categoria_id: int | None = Query(None),
):
    try:
        return despesa_service.painel_despesas(
            db, mes=mes, status=status_filtro, categoria_id=categoria_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get(
    "/despesas/resumo",
    response_model=DespesasResumoResponse,
    summary="Resumo de despesas (KPIs + por categoria)",
)
def resumo_despesas(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
    mes: str | None = Query(None, description="YYYY-MM — omite para todos os períodos"),
):
    try:
        return despesa_service.resumo_despesas(db, mes=mes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get(
    "/despesas",
    response_model=list[DespesaResponse],
    summary="Listar despesas",
)
def listar_despesas(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
    mes: str | None = Query(None, description="YYYY-MM"),
    status_filtro: str | None = Query(None, alias="status", description="pago | pendente"),
    categoria_id: int | None = Query(None),
):
    try:
        return despesa_service.listar_despesas(
            db, mes=mes, status=status_filtro, categoria_id=categoria_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.post(
    "/despesas",
    response_model=DespesaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar despesa",
)
def criar_despesa(
    payload: DespesaCreate,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[Usuario, Depends(get_current_admin)],
):
    try:
        return despesa_service.criar_despesa(
            db,
            data_pagamento=payload.data_pagamento,
            data_vencimento=payload.data_vencimento,
            descricao=payload.descricao,
            categoria_id=payload.categoria_id,
            status=payload.status,
            valor=payload.valor,
            recorrencia=payload.recorrencia,
            vigencia_inicio=payload.vigencia_inicio,
            vigencia_fim=payload.vigencia_fim,
            criado_por_id=admin.id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.post(
    "/despesas/importar",
    response_model=ImportacaoDespesasResponse,
    summary="Importar planilha Excel de despesas",
)
async def importar_despesas(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[Usuario, Depends(get_current_admin)],
    arquivo: UploadFile = File(..., description="Arquivo .xlsx com aba Controle de Despesas"),
):
    nome = (arquivo.filename or "").lower()
    if not nome.endswith((".xlsx", ".xlsm")):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Envie um arquivo Excel (.xlsx).",
        )
    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Arquivo vazio.")
    try:
        return despesa_service.importar_planilha(
            db, conteudo, criado_por_id=admin.id
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar planilha: {exc}",
        )


@router.patch(
    "/despesas/{despesa_id}",
    response_model=DespesaResponse,
    summary="Atualizar despesa",
)
def atualizar_despesa(
    despesa_id: int,
    payload: DespesaUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    despesa = _get_despesa_ou_404(despesa_id, db)
    try:
        return despesa_service.atualizar_despesa(
            db, despesa, payload.model_dump(exclude_unset=True)
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.patch(
    "/despesas/{despesa_id}/status",
    response_model=DespesaResponse,
    summary="Alternar status pago/pendente (atualização rápida)",
)
def atualizar_status_despesa(
    despesa_id: int,
    payload: DespesaStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    despesa = _get_despesa_ou_404(despesa_id, db)
    try:
        return despesa_service.atualizar_status(
            db,
            despesa,
            payload.status,
            data_pagamento=payload.data_pagamento,
            mes=payload.mes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.delete(
    "/despesas/{despesa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir despesa",
)
def excluir_despesa(
    despesa_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    despesa = _get_despesa_ou_404(despesa_id, db)
    despesa_service.excluir_despesa(db, despesa)
