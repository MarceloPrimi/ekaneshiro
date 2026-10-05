"""Regras de negócio do Controle de Despesas (Financeiro / Contas a Pagar)."""

from __future__ import annotations

import hashlib
import io
import re
from calendar import monthrange
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from openpyxl import load_workbook
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from db.models import (
    CategoriaDespesa,
    Despesa,
    DespesaOcorrencia,
    RecorrenciaDespesaEnum,
    StatusDespesaEnum,
)

_STATUS_MAP = {
    "pago": StatusDespesaEnum.pago,
    "pendente": StatusDespesaEnum.pendente,
}
_RECORRENCIA_MAP = {
    "avulsa": RecorrenciaDespesaEnum.avulsa,
    "mensal": RecorrenciaDespesaEnum.mensal,
    "temporaria": RecorrenciaDespesaEnum.temporaria,
}

CATEGORIA_CUSTOS_FIXOS = "custos fixos"


def parse_status(raw: str | StatusDespesaEnum) -> StatusDespesaEnum:
    if isinstance(raw, StatusDespesaEnum):
        return raw
    key = (raw or "").strip().lower()
    if key not in _STATUS_MAP:
        raise ValueError("Status inválido. Use 'pago' ou 'pendente'.")
    return _STATUS_MAP[key]


def parse_recorrencia(raw: str | RecorrenciaDespesaEnum) -> RecorrenciaDespesaEnum:
    if isinstance(raw, RecorrenciaDespesaEnum):
        return raw
    key = (raw or "avulsa").strip().lower()
    if key not in _RECORRENCIA_MAP:
        raise ValueError("Recorrência inválida. Use avulsa, mensal ou temporaria.")
    return _RECORRENCIA_MAP[key]


def mes_para_intervalo(mes: str) -> tuple[date, date]:
    if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", mes):
        raise ValueError("Formato inválido. Use YYYY-MM (ex: 2026-03).")
    ano, mnum = int(mes[:4]), int(mes[5:7])
    ultimo = monthrange(ano, mnum)[1]
    return date(ano, mnum, 1), date(ano, mnum, ultimo)


def make_import_hash(
    data_pagamento: date | None,
    descricao: str,
    valor: Decimal,
    categoria_nome: str,
    status: StatusDespesaEnum,
) -> str:
    data_key = data_pagamento.isoformat() if data_pagamento else "sem-data"
    payload = (
        f"{data_key}|{descricao.strip().lower()}|{valor:.2f}|"
        f"{categoria_nome.strip().lower()}|{status.value}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def aplicar_regras_pagamento(
    status: StatusDespesaEnum,
    data_pagamento: date | None,
    *,
    default_pago_hoje: bool = False,
) -> date | None:
    if status == StatusDespesaEnum.pendente:
        return None
    if data_pagamento is not None:
        return data_pagamento
    if default_pago_hoje:
        return date.today()
    raise ValueError("Data do pagamento é obrigatória quando a despesa está paga.")


def _enum_val(v) -> str:
    return v.value if hasattr(v, "value") else str(v)


def _ativa_na_competencia(despesa: Despesa, mes: str) -> bool:
    inicio_mes, fim_mes = mes_para_intervalo(mes)
    rec = despesa.recorrencia
    if isinstance(rec, str):
        rec = parse_recorrencia(rec)
    if rec == RecorrenciaDespesaEnum.avulsa:
        return False
    vi = despesa.vigencia_inicio or date.min
    vf = despesa.vigencia_fim
    if vi > fim_mes:
        return False
    if vf is not None and vf < inicio_mes:
        return False
    return True


def vencimento_na_competencia(data_vencimento: date | None, mes: str | None) -> date | None:
    """Para recorrente mensal, aplica o dia do vencimento na competência."""
    if data_vencimento is None:
        return None
    if not mes:
        return data_vencimento
    inicio, fim = mes_para_intervalo(mes)
    dia = min(data_vencimento.day, fim.day)
    return date(inicio.year, inicio.month, dia)


def to_response_dict(
    despesa: Despesa,
    *,
    competencia: str | None = None,
    ocorrencia: DespesaOcorrencia | None = None,
) -> dict:
    rec = _enum_val(despesa.recorrencia) if despesa.recorrencia else "avulsa"
    if ocorrencia is not None:
        status = _enum_val(ocorrencia.status)
        data_pag = ocorrencia.data_pagamento
        ocorrencia_id = ocorrencia.id
    elif rec != "avulsa":
        status = "pendente"
        data_pag = None
        ocorrencia_id = None
    else:
        status = _enum_val(despesa.status)
        data_pag = despesa.data_pagamento
        ocorrencia_id = None

    data_venc = despesa.data_vencimento
    if rec != "avulsa" and competencia:
        data_venc = vencimento_na_competencia(despesa.data_vencimento, competencia)

    return {
        "id": despesa.id,
        "data_pagamento": data_pag,
        "data_vencimento": data_venc,
        "descricao": despesa.descricao,
        "categoria_id": despesa.categoria_id,
        "categoria_nome": despesa.categoria.nome if despesa.categoria else None,
        "status": status,
        "valor": despesa.valor,
        "recorrencia": rec,
        "vigencia_inicio": despesa.vigencia_inicio,
        "vigencia_fim": despesa.vigencia_fim,
        "competencia": competencia,
        "ocorrencia_id": ocorrencia_id,
        "criado_em": despesa.criado_em,
        "atualizado_em": despesa.atualizado_em,
    }


def listar_despesas(
    db: Session,
    *,
    mes: str | None = None,
    status: str | None = None,
    categoria_id: int | None = None,
) -> list[dict]:
    status_filtro = parse_status(status) if status else None
    itens: list[dict] = []

    # --- Avulsas ---
    q_avulsa = (
        db.query(Despesa)
        .options(joinedload(Despesa.categoria))
        .filter(Despesa.recorrencia == RecorrenciaDespesaEnum.avulsa)
    )
    if mes:
        inicio, fim = mes_para_intervalo(mes)
        q_avulsa = q_avulsa.filter(
            or_(
                (Despesa.data_pagamento >= inicio) & (Despesa.data_pagamento <= fim),
                (Despesa.status == StatusDespesaEnum.pendente) & (Despesa.data_pagamento.is_(None)),
            )
        )
    if categoria_id:
        q_avulsa = q_avulsa.filter(Despesa.categoria_id == categoria_id)
    for d in q_avulsa.all():
        row = to_response_dict(d, competencia=mes)
        if status_filtro and row["status"] != status_filtro.value:
            continue
        itens.append(row)

    # --- Recorrentes (mensal / temporária) ---
    if mes:
        inicio, fim = mes_para_intervalo(mes)
        q_rec = (
            db.query(Despesa)
            .options(joinedload(Despesa.categoria))
            .filter(
                Despesa.recorrencia.in_(
                    [RecorrenciaDespesaEnum.mensal, RecorrenciaDespesaEnum.temporaria]
                ),
                # Filtra vigência no SQL (evita trazer templates inativos)
                or_(Despesa.vigencia_inicio.is_(None), Despesa.vigencia_inicio <= fim),
                or_(Despesa.vigencia_fim.is_(None), Despesa.vigencia_fim >= inicio),
            )
        )
        if categoria_id:
            q_rec = q_rec.filter(Despesa.categoria_id == categoria_id)

        ocorrencias = {
            o.despesa_id: o
            for o in db.query(DespesaOcorrencia).filter(DespesaOcorrencia.competencia == mes).all()
        }
        for d in q_rec.all():
            occ = ocorrencias.get(d.id)
            row = to_response_dict(d, competencia=mes, ocorrencia=occ)
            if status_filtro and row["status"] != status_filtro.value:
                continue
            itens.append(row)

    def _sort_key(r: dict):
        pend = 0 if r["status"] == "pendente" else 1
        dp = r["data_pagamento"].isoformat() if r["data_pagamento"] else ""
        return (pend, dp, -r["id"])

    itens.sort(key=_sort_key)
    return itens


def criar_despesa(
    db: Session,
    *,
    data_pagamento: date | None,
    descricao: str,
    categoria_id: int,
    status: str,
    valor: Decimal,
    recorrencia: str = "avulsa",
    vigencia_inicio: date | None = None,
    vigencia_fim: date | None = None,
    data_vencimento: date | None = None,
    criado_por_id: int | None = None,
) -> dict:
    categoria = db.query(CategoriaDespesa).filter(CategoriaDespesa.id == categoria_id).first()
    if not categoria:
        raise LookupError("Categoria de despesa não encontrada.")

    # Custos Fixos → mensal por padrão se cliente mandou avulsa sem querer
    rec = parse_recorrencia(recorrencia)
    if categoria.nome.strip().lower() == CATEGORIA_CUSTOS_FIXOS and rec == RecorrenciaDespesaEnum.avulsa:
        # só força se não foi temporária explicitamente — avulsa em custos fixos vira mensal
        rec = RecorrenciaDespesaEnum.mensal
        if vigencia_inicio is None:
            vigencia_inicio = date.today().replace(day=1)

    st = parse_status(status)

    if rec == RecorrenciaDespesaEnum.avulsa:
        data_pag = aplicar_regras_pagamento(st, data_pagamento)
        despesa = Despesa(
            data_pagamento=data_pag,
            data_vencimento=data_vencimento,
            descricao=descricao.strip(),
            categoria_id=categoria_id,
            status=st,
            valor=valor,
            recorrencia=rec,
            vigencia_inicio=None,
            vigencia_fim=None,
            criado_por_id=criado_por_id,
        )
        despesa.categoria = categoria
        db.add(despesa)
        db.flush()
        resp = to_response_dict(despesa)
        db.commit()
        return resp

    # Recorrente / temporário — vencimento obrigatório
    if data_vencimento is None:
        raise ValueError("Data de vencimento é obrigatória para custo recorrente ou temporário.")

    if rec == RecorrenciaDespesaEnum.mensal:
        vi = vigencia_inicio or date.today().replace(day=1)
        vf = None
    else:
        if vigencia_inicio is None or vigencia_fim is None:
            raise ValueError("Custo temporário exige data de início e fim.")
        if vigencia_fim < vigencia_inicio:
            raise ValueError("A data fim deve ser maior ou igual à data início.")
        vi, vf = vigencia_inicio, vigencia_fim

    despesa = Despesa(
        data_pagamento=None,
        data_vencimento=data_vencimento,
        descricao=descricao.strip(),
        categoria_id=categoria_id,
        status=StatusDespesaEnum.pendente,
        valor=valor,
        recorrencia=rec,
        vigencia_inicio=vi,
        vigencia_fim=vf,
        criado_por_id=criado_por_id,
    )
    despesa.categoria = categoria
    db.add(despesa)
    db.flush()

    # Se já veio como pago, cria ocorrência no mês da data (ou mês atual)
    competencia = None
    occ = None
    if st == StatusDespesaEnum.pago:
        data_pag = aplicar_regras_pagamento(st, data_pagamento, default_pago_hoje=True)
        competencia = f"{data_pag.year:04d}-{data_pag.month:02d}"
        if _ativa_na_competencia(despesa, competencia):
            occ = DespesaOcorrencia(
                despesa_id=despesa.id,
                competencia=competencia,
                status=StatusDespesaEnum.pago,
                data_pagamento=data_pag,
            )
            db.add(occ)
            db.flush()

    resp = to_response_dict(despesa, competencia=competencia, ocorrencia=occ)
    db.commit()
    return resp


def atualizar_despesa(db: Session, despesa: Despesa, campos: dict) -> dict:
    # Garante categoria em memória (evita lazy/refresh pós-commit)
    if "categoria_id" in campos and campos["categoria_id"] is not None:
        cat = db.query(CategoriaDespesa).filter(CategoriaDespesa.id == campos["categoria_id"]).first()
        if not cat:
            raise LookupError("Categoria de despesa não encontrada.")
        despesa.categoria_id = cat.id
        despesa.categoria = cat
    else:
        _ = despesa.categoria

    if "descricao" in campos and campos["descricao"] is not None:
        despesa.descricao = campos["descricao"].strip()
    if "valor" in campos and campos["valor"] is not None:
        despesa.valor = campos["valor"]

    if "recorrencia" in campos and campos["recorrencia"] is not None:
        despesa.recorrencia = parse_recorrencia(campos["recorrencia"])
    if "vigencia_inicio" in campos:
        despesa.vigencia_inicio = campos["vigencia_inicio"]
    if "vigencia_fim" in campos:
        despesa.vigencia_fim = campos["vigencia_fim"]
    if "data_vencimento" in campos:
        despesa.data_vencimento = campos["data_vencimento"]

    rec = despesa.recorrencia
    if isinstance(rec, str):
        rec = parse_recorrencia(rec)

    if rec == RecorrenciaDespesaEnum.avulsa:
        st = parse_status(campos["status"]) if campos.get("status") is not None else despesa.status
        data_in = campos["data_pagamento"] if "data_pagamento" in campos else despesa.data_pagamento
        despesa.status = st
        despesa.data_pagamento = aplicar_regras_pagamento(st, data_in)
        despesa.vigencia_inicio = None
        despesa.vigencia_fim = None
    elif rec == RecorrenciaDespesaEnum.mensal:
        if despesa.data_vencimento is None:
            raise ValueError("Data de vencimento é obrigatória para custo recorrente (fixo).")
        if despesa.vigencia_inicio is None:
            despesa.vigencia_inicio = date.today().replace(day=1)
        despesa.vigencia_fim = None
        despesa.status = StatusDespesaEnum.pendente
        despesa.data_pagamento = None
    else:
        if despesa.data_vencimento is None:
            raise ValueError("Data de vencimento é obrigatória para custo temporário.")
        if not despesa.vigencia_inicio or not despesa.vigencia_fim:
            raise ValueError("Custo temporário exige data de início e fim.")
        if despesa.vigencia_fim < despesa.vigencia_inicio:
            raise ValueError("A data fim deve ser maior ou igual à data início.")
        despesa.status = StatusDespesaEnum.pendente
        despesa.data_pagamento = None

    despesa.atualizado_em = datetime.utcnow()
    resp = to_response_dict(despesa)
    db.commit()
    return resp


def atualizar_status(
    db: Session,
    despesa: Despesa,
    status: str,
    data_pagamento: date | None = None,
    mes: str | None = None,
) -> dict:
    st = parse_status(status)
    rec = despesa.recorrencia
    if isinstance(rec, str):
        rec = parse_recorrencia(rec)

    # Garante categoria em memória antes do commit (evita refresh/lazy pós-expire)
    _ = despesa.categoria

    if rec == RecorrenciaDespesaEnum.avulsa:
        despesa.status = st
        despesa.data_pagamento = aplicar_regras_pagamento(st, data_pagamento, default_pago_hoje=True)
        despesa.atualizado_em = datetime.utcnow()
        resp = to_response_dict(despesa)
        db.commit()
        return resp

    if not mes:
        raise ValueError("Informe o mês (competência) para atualizar despesa recorrente.")
    mes_para_intervalo(mes)  # valida formato
    if not _ativa_na_competencia(despesa, mes):
        raise ValueError("Esta despesa não está vigente no mês informado.")

    data_pag = aplicar_regras_pagamento(st, data_pagamento, default_pago_hoje=True)
    occ = (
        db.query(DespesaOcorrencia)
        .filter(
            DespesaOcorrencia.despesa_id == despesa.id,
            DespesaOcorrencia.competencia == mes,
        )
        .first()
    )
    if not occ:
        occ = DespesaOcorrencia(
            despesa_id=despesa.id,
            competencia=mes,
            status=st,
            data_pagamento=data_pag,
        )
        db.add(occ)
        db.flush()  # obtém id sem refresh extra depois
    else:
        occ.status = st
        occ.data_pagamento = data_pag
        occ.atualizado_em = datetime.utcnow()

    resp = to_response_dict(despesa, competencia=mes, ocorrencia=occ)
    db.commit()
    return resp


def excluir_despesa(db: Session, despesa: Despesa) -> None:
    db.delete(despesa)
    db.commit()


def resumo_from_rows(rows: list[dict], *, mes: str | None = None) -> dict:
    total = sum((Decimal(str(r["valor"])) for r in rows), Decimal("0"))
    total_pago = sum(
        (Decimal(str(r["valor"])) for r in rows if r["status"] == "pago"),
        Decimal("0"),
    )
    total_pendente = sum(
        (Decimal(str(r["valor"])) for r in rows if r["status"] == "pendente"),
        Decimal("0"),
    )

    por_cat: dict[int, dict] = {}
    for r in rows:
        cid = r["categoria_id"]
        if cid not in por_cat:
            por_cat[cid] = {
                "categoria_id": cid,
                "categoria_nome": r["categoria_nome"] or "—",
                "total": Decimal("0"),
            }
        por_cat[cid]["total"] += Decimal(str(r["valor"]))

    por_categoria = []
    for item in sorted(por_cat.values(), key=lambda x: x["total"], reverse=True):
        pct = float((item["total"] / total * 100) if total > 0 else 0)
        por_categoria.append(
            {
                "categoria_id": item["categoria_id"],
                "categoria_nome": item["categoria_nome"],
                "total": item["total"],
                "percentual": round(pct, 1),
            }
        )

    return {
        "mes": mes,
        "total": total,
        "total_pago": total_pago,
        "total_pendente": total_pendente,
        "quantidade": len(rows),
        "por_categoria": por_categoria,
    }


def resumo_despesas(db: Session, *, mes: str | None = None) -> dict:
    return resumo_from_rows(listar_despesas(db, mes=mes), mes=mes)


def painel_despesas(
    db: Session,
    *,
    mes: str | None = None,
    status: str | None = None,
    categoria_id: int | None = None,
) -> dict:
    """Lista + KPIs sem duplicar a query de listagem."""
    rows = listar_despesas(db, mes=mes, status=status, categoria_id=categoria_id)
    if status or categoria_id:
        rows_resumo = listar_despesas(db, mes=mes)
    else:
        rows_resumo = rows
    return {
        "despesas": rows,
        "resumo": resumo_from_rows(rows_resumo, mes=mes),
    }


def _parse_excel_date(raw) -> date | None:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    text = str(raw).strip()
    if not text or text.upper().startswith("TOTAL"):
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text[:10], fmt).date()
        except ValueError:
            continue
    return None


def _parse_valor(raw) -> Decimal | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float, Decimal)):
        return Decimal(str(raw)).quantize(Decimal("0.01"))
    text = str(raw).strip().replace("R$", "").replace(" ", "")
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return Decimal(text).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def importar_planilha(
    db: Session,
    file_bytes: bytes,
    *,
    criado_por_id: int | None = None,
) -> dict:
    wb = load_workbook(io.BytesIO(file_bytes), data_only=True, read_only=True)
    sheet_name = "Controle de Despesas"
    ws = wb[sheet_name] if sheet_name in wb.sheetnames else wb[wb.sheetnames[0]]

    categorias = {
        c.nome.strip().lower(): c
        for c in db.query(CategoriaDespesa).filter(CategoriaDespesa.ativo == True).all()
    }

    inseridas = 0
    ignoradas = 0
    erros: list[str] = []

    header_row = None
    for i, row in enumerate(ws.iter_rows(max_row=30, values_only=True), 1):
        cells = [str(c).strip().lower() if c is not None else "" for c in row]
        if any("data" == c for c in cells) and any("valor" in c for c in cells):
            header_row = i
            break

    if header_row is None:
        wb.close()
        raise ValueError(
            "Cabeçalho não encontrado. Esperado: Data, Conta/Descrição, Tipo de Despesa, Status, Valor."
        )

    header_cells = list(next(ws.iter_rows(min_row=header_row, max_row=header_row, values_only=True)))
    col_idx = {}
    for idx, cell in enumerate(header_cells):
        if cell is None:
            continue
        label = str(cell).strip().lower()
        if label == "data":
            col_idx["data"] = idx
        elif "descri" in label or "conta" in label:
            col_idx["descricao"] = idx
        elif "tipo" in label:
            col_idx["tipo"] = idx
        elif label == "status":
            col_idx["status"] = idx
        elif "valor" in label:
            col_idx["valor"] = idx

    required = ("data", "descricao", "tipo", "status", "valor")
    missing = [k for k in required if k not in col_idx]
    if missing:
        wb.close()
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing)}")

    existing_hashes = {
        h for (h,) in db.query(Despesa.import_hash).filter(Despesa.import_hash.isnot(None)).all()
    }

    for row_num, row in enumerate(
        ws.iter_rows(min_row=header_row + 1, values_only=True),
        start=header_row + 1,
    ):
        cells = list(row)
        if not any(cells):
            continue

        data_bruta = _parse_excel_date(cells[col_idx["data"]] if col_idx["data"] < len(cells) else None)
        descricao_raw = cells[col_idx["descricao"]] if col_idx["descricao"] < len(cells) else None
        tipo_raw = cells[col_idx["tipo"]] if col_idx["tipo"] < len(cells) else None
        status_raw = cells[col_idx["status"]] if col_idx["status"] < len(cells) else None
        valor = _parse_valor(cells[col_idx["valor"]] if col_idx["valor"] < len(cells) else None)

        descricao = str(descricao_raw).strip() if descricao_raw else ""
        tipo = str(tipo_raw).strip() if tipo_raw else ""

        if not descricao and valor is None:
            continue
        if descricao.upper().startswith("TOTAL"):
            continue
        if not descricao or not tipo or valor is None:
            erros.append(f"Linha {row_num}: dados incompletos — ignorada.")
            continue

        categoria = categorias.get(tipo.lower())
        if not categoria:
            categoria = CategoriaDespesa(nome=tipo, ativo=True)
            db.add(categoria)
            db.flush()
            categorias[tipo.lower()] = categoria

        try:
            status = parse_status(str(status_raw or "pendente"))
        except ValueError:
            erros.append(f"Linha {row_num}: status inválido '{status_raw}' — ignorada.")
            continue

        is_fixo = categoria.nome.strip().lower() == CATEGORIA_CUSTOS_FIXOS
        rec = RecorrenciaDespesaEnum.mensal if is_fixo else RecorrenciaDespesaEnum.avulsa

        if rec == RecorrenciaDespesaEnum.avulsa:
            try:
                data_pag = aplicar_regras_pagamento(status, data_bruta)
            except ValueError:
                erros.append(f"Linha {row_num}: despesa paga sem data — ignorada.")
                continue
            h = make_import_hash(data_pag, descricao, valor, categoria.nome, status)
            if h in existing_hashes:
                ignoradas += 1
                continue
            db.add(
                Despesa(
                    data_pagamento=data_pag,
                    descricao=descricao,
                    categoria_id=categoria.id,
                    status=status,
                    valor=valor,
                    recorrencia=rec,
                    import_hash=h,
                    criado_por_id=criado_por_id,
                )
            )
            existing_hashes.add(h)
            inseridas += 1
        else:
            # Mensal (Custos Fixos): template + ocorrência do mês
            vi = data_bruta or date.today().replace(day=1)
            try:
                data_pag = aplicar_regras_pagamento(status, data_bruta, default_pago_hoje=False) if status == StatusDespesaEnum.pago else None
            except ValueError:
                erros.append(f"Linha {row_num}: despesa paga sem data — ignorada.")
                continue
            if status == StatusDespesaEnum.pago and data_pag is None:
                erros.append(f"Linha {row_num}: despesa paga sem data — ignorada.")
                continue

            h = make_import_hash(vi, descricao, valor, categoria.nome, StatusDespesaEnum.pendente)
            if h in existing_hashes:
                ignoradas += 1
                continue

            despesa = Despesa(
                data_pagamento=None,
                data_vencimento=data_bruta or vi,
                descricao=descricao,
                categoria_id=categoria.id,
                status=StatusDespesaEnum.pendente,
                valor=valor,
                recorrencia=RecorrenciaDespesaEnum.mensal,
                vigencia_inicio=vi.replace(day=1) if hasattr(vi, "replace") else vi,
                vigencia_fim=None,
                import_hash=h,
                criado_por_id=criado_por_id,
            )
            db.add(despesa)
            db.flush()
            if data_pag is not None or status == StatusDespesaEnum.pendente:
                comp_date = data_pag or vi
                competencia = f"{comp_date.year:04d}-{comp_date.month:02d}"
                db.add(
                    DespesaOcorrencia(
                        despesa_id=despesa.id,
                        competencia=competencia,
                        status=status,
                        data_pagamento=data_pag,
                    )
                )
            existing_hashes.add(h)
            inseridas += 1

    db.commit()
    wb.close()
    return {
        "inseridas": inseridas,
        "ignoradas_duplicadas": ignoradas,
        "erros": erros[:50],
    }
