from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from api.dependencias import get_current_admin, get_current_user
from db.database import get_db
from db.models import ItemAgendamento, Profissional, ProfissionalSecao, ProfissionalServico, RoleEnum, Secao, Servico, Usuario
from schemas.profissionais import (
    ProfissionalComServicosResponse,
    ProfissionalCreate,
    ProfissionalResponse,
    ProfissionalServicoPrecoUpdate,
    ProfissionalUpdate,
)
from schemas.secoes import SecaoResponse, SecaosProfissionalUpdate

router = APIRouter(prefix="/profissionais", tags=["Profissionais"])

# Eager loading: evita N+1 ao montar a resposta com serviços + seções.
# Sem isso, cada profissional dispara 1 query por serviço e por seção,
# o que com latência alta ao banco (produção) deixa a listagem lenta.
_EAGER_PROFISSIONAL = [
    selectinload(Profissional.servicos).joinedload(ProfissionalServico.servico),
    selectinload(Profissional.secoes).joinedload(ProfissionalSecao.secao),
]


@router.post(
    "/",
    response_model=ProfissionalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar profissional (Admin)",
)
def criar_profissional(
    payload: ProfissionalCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    if db.query(Profissional).filter(
        func.lower(Profissional.nome) == payload.nome.strip().lower()
    ).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um profissional cadastrado com este nome.",
        )
    dados = payload.model_dump(exclude={"secao_ids"})
    novo = Profissional(**dados)
    db.add(novo)
    db.flush()  # obtém o id antes do commit
    if payload.secao_ids:
        secoes = db.query(Secao).filter(Secao.id.in_(payload.secao_ids)).all()
        for secao in secoes:
            db.add(ProfissionalSecao(profissional_id=novo.id, secao_id=secao.id))
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=list[ProfissionalComServicosResponse], summary="Listar profissionais")
def listar_profissionais(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
    apenas_ativos: bool = True,
):
    query = db.query(Profissional).options(*_EAGER_PROFISSIONAL)
    if apenas_ativos:
        query = query.filter(Profissional.ativo == True)
    profissionais = query.order_by(Profissional.nome).all()
    return [ProfissionalComServicosResponse.from_orm_with_servicos(p) for p in profissionais]


@router.get(
    "/{profissional_id}",
    response_model=ProfissionalComServicosResponse,
    summary="Buscar profissional com seus serviços",
)
def buscar_profissional(
    profissional_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    profissional = (
        db.query(Profissional)
        .options(*_EAGER_PROFISSIONAL)
        .filter(Profissional.id == profissional_id)
        .first()
    )
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado."
        )
    return ProfissionalComServicosResponse.from_orm_with_servicos(profissional)


@router.patch(
    "/{profissional_id}",
    response_model=ProfissionalResponse,
    summary="Atualizar profissional (Admin)",
)
def atualizar_profissional(
    profissional_id: int,
    payload: ProfissionalUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    profissional = db.query(Profissional).filter(Profissional.id == profissional_id).first()
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado."
        )

    update_data = payload.model_dump(exclude_unset=True, exclude={"secao_ids"})

    # Validar vínculo de usuário quando explicitamente fornecido
    if "usuario_id" in update_data and update_data["usuario_id"] is not None:
        uid = update_data["usuario_id"]
        usuario = db.get(Usuario, uid)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )
        if usuario.role != RoleEnum.profissional:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O usuário precisa ter o perfil 'profissional' para ser vinculado.",
            )
        conflito = (
            db.query(Profissional)
            .filter(
                Profissional.usuario_id == uid,
                Profissional.id != profissional_id,
            )
            .first()
        )
        if conflito:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Este usuário já está vinculado ao profissional '{conflito.nome}'.",
            )

    for field, value in update_data.items():
        setattr(profissional, field, value)

    db.commit()
    db.refresh(profissional)
    return profissional


@router.post(
    "/{profissional_id}/servicos/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Habilitar serviço para profissional (Admin)",
)
def habilitar_servico(
    profissional_id: int,
    servico_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    profissional = db.query(Profissional).filter(Profissional.id == profissional_id).first()
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado."
        )

    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado.")

    ja_existe = (
        db.query(ProfissionalServico)
        .filter_by(profissional_id=profissional_id, servico_id=servico_id)
        .first()
    )
    if ja_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profissional já habilitado para este serviço.",
        )

    db.add(ProfissionalServico(profissional_id=profissional_id, servico_id=servico_id))
    db.commit()


@router.delete(
    "/{profissional_id}/servicos/{servico_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover habilitação de serviço (Admin)",
)
def remover_servico(
    profissional_id: int,
    servico_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    vinculo = (
        db.query(ProfissionalServico)
        .filter_by(profissional_id=profissional_id, servico_id=servico_id)
        .first()
    )
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vínculo não encontrado."
        )
    db.delete(vinculo)
    db.commit()


@router.delete(
    "/{profissional_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover profissional (Admin)",
)
def deletar_profissional(
    profissional_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    profissional = db.query(Profissional).filter(Profissional.id == profissional_id).first()
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profissional não encontrado."
        )
    # remover vínculos de serviços e itens de agendamento antes
    db.query(ProfissionalServico).filter_by(profissional_id=profissional_id).delete()
    db.query(ItemAgendamento).filter_by(profissional_id=profissional_id).delete()
    db.delete(profissional)
    db.commit()


@router.patch(
    "/{profissional_id}/servicos/{servico_id}/preco",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Atualizar preço próprio do profissional para um serviço",
)
def atualizar_preco_proprio(
    profissional_id: int,
    servico_id: int,
    payload: ProfissionalServicoPrecoUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """
    Permite que o próprio profissional (ou um admin/recepcionista)
    defina seu preço pessoal para um serviço habilitado.
    """
    # Profissional só pode alterar o seu próprio preço
    from db.models import RoleEnum as RE
    if current_user.role == RE.profissional:
        prof_do_user = db.query(Profissional).filter_by(usuario_id=current_user.id).first()
        if not prof_do_user or prof_do_user.id != profissional_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode editar seu próprio preço.",
            )

    vinculo = (
        db.query(ProfissionalServico)
        .filter_by(profissional_id=profissional_id, servico_id=servico_id)
        .first()
    )
    if not vinculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vínculo profissional-serviço não encontrado.",
        )
    vinculo.preco_proprio = payload.preco_proprio
    db.commit()


# ---------------------------------------------------------------------------
# Seções do profissional
# ---------------------------------------------------------------------------


@router.get(
    "/{profissional_id}/secoes",
    response_model=list[SecaoResponse],
    summary="Listar seções do profissional",
)
def listar_secoes_profissional(
    profissional_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_user)],
):
    profissional = db.query(Profissional).filter(Profissional.id == profissional_id).first()
    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")
    return [ps.secao for ps in profissional.secoes]


@router.put(
    "/{profissional_id}/secoes",
    response_model=list[SecaoResponse],
    summary="Definir seções do profissional (substitui a lista atual)",
)
def definir_secoes_profissional(
    profissional_id: int,
    payload: SecaosProfissionalUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[Usuario, Depends(get_current_admin)],
):
    profissional = db.query(Profissional).filter(Profissional.id == profissional_id).first()
    if not profissional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado.")

    secoes = db.query(Secao).filter(Secao.id.in_(payload.secao_ids)).all()
    if len(secoes) != len(payload.secao_ids):
        raise HTTPException(status_code=400, detail="Uma ou mais seções não encontradas.")

    db.query(ProfissionalSecao).filter_by(profissional_id=profissional_id).delete()
    for secao in secoes:
        db.add(ProfissionalSecao(profissional_id=profissional_id, secao_id=secao.id))

    # Auto-sync: replace profissional's services with all services from selected sections
    secao_ids = [s.id for s in secoes]
    servicos_das_secoes = (
        db.query(Servico).filter(Servico.secao_id.in_(secao_ids)).all()
        if secao_ids else []
    )
    servico_ids_novos = {s.id for s in servicos_das_secoes}

    # Remove services no longer in selected sections
    vinculos_atuais = (
        db.query(ProfissionalServico).filter_by(profissional_id=profissional_id).all()
    )
    for v in vinculos_atuais:
        if v.servico_id not in servico_ids_novos:
            db.delete(v)

    # Add new services not yet linked
    ids_atuais = {v.servico_id for v in vinculos_atuais}
    for sid in servico_ids_novos:
        if sid not in ids_atuais:
            db.add(ProfissionalServico(profissional_id=profissional_id, servico_id=sid))

    db.commit()
    db.refresh(profissional)
    return [ps.secao for ps in profissional.secoes]
