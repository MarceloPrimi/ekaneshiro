import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, ForeignKey,
    Integer, JSON, Numeric, String, Text,
)
from sqlalchemy.orm import relationship

from db.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RoleEnum(str, enum.Enum):
    admin = "admin"
    recepcionista = "recepcionista"
    profissional = "profissional"


class StatusAgendamentoEnum(str, enum.Enum):
    pendente = "pendente"
    confirmado = "confirmado"
    concluido = "concluido"
    cancelado = "cancelado"


# ---------------------------------------------------------------------------
# Usuários do sistema (login/acesso)
# ---------------------------------------------------------------------------

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.recepcionista)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Se o usuário for um profissional, pode ter um vínculo
    profissional = relationship("Profissional", back_populates="usuario", uselist=False)


# ---------------------------------------------------------------------------
# Clientes do salão
# ---------------------------------------------------------------------------

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True, index=True)
    observacoes = Column(Text, nullable=True)
    # JSON: lista de {chave, valor} para campos customizados
    campos_dinamicos = Column(JSON, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    agendamentos = relationship("Agendamento", back_populates="cliente")


# ---------------------------------------------------------------------------
# Profissionais do salão
# ---------------------------------------------------------------------------

class Profissional(Base):
    __tablename__ = "profissionais"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    telefone = Column(String(30), nullable=True)
    chave_pix = Column(String(200), nullable=True)

    # Vínculo opcional com um usuário do sistema (para login com role=profissional)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, unique=True)
    usuario = relationship("Usuario", back_populates="profissional")

    # Google Calendar: ID da agenda pessoal do profissional
    google_calendar_id = Column(String(255), nullable=True)

    servicos = relationship("ProfissionalServico", back_populates="profissional")
    agendamentos = relationship("ItemAgendamento", back_populates="profissional")


# ---------------------------------------------------------------------------
# Catálogo de Serviços
# ---------------------------------------------------------------------------

class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text, nullable=True)
    duracao_minutos = Column(Integer, nullable=False)
    preco = Column(Numeric(10, 2), nullable=False)
    preco_minimo = Column(Numeric(10, 2), nullable=True)
    preco_maximo = Column(Numeric(10, 2), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    profissionais = relationship("ProfissionalServico", back_populates="servico")


# ---------------------------------------------------------------------------
# Relacionamento N:N — Profissional habilita Serviço
# ---------------------------------------------------------------------------

class ProfissionalServico(Base):
    __tablename__ = "profissionais_servicos"

    profissional_id = Column(Integer, ForeignKey("profissionais.id"), primary_key=True)
    servico_id = Column(Integer, ForeignKey("servicos.id"), primary_key=True)
    # Preço que este profissional cobra pelo serviço (sobrescreve o padrão do serviço)
    preco_proprio = Column(Numeric(10, 2), nullable=True)

    profissional = relationship("Profissional", back_populates="servicos")
    servico = relationship("Servico", back_populates="profissionais")


# ---------------------------------------------------------------------------
# Agendamento (cabeçalho — pode ter múltiplos itens)
# ---------------------------------------------------------------------------

class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    status = Column(
        Enum(StatusAgendamentoEnum),
        nullable=False,
        default=StatusAgendamentoEnum.pendente,
        index=True,
    )
    observacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    cliente = relationship("Cliente", back_populates="agendamentos")
    itens = relationship(
        "ItemAgendamento", back_populates="agendamento", cascade="all, delete-orphan"
    )
    pagamento = relationship("Pagamento", back_populates="agendamento", uselist=False)


# ---------------------------------------------------------------------------
# Item de Agendamento (um serviço com um profissional em uma data/hora)
# ---------------------------------------------------------------------------

class ItemAgendamento(Base):
    __tablename__ = "itens_agendamento"

    id = Column(Integer, primary_key=True, index=True)
    agendamento_id = Column(Integer, ForeignKey("agendamentos.id"), nullable=False, index=True)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False, index=True)
    data_hora_inicio = Column(DateTime, nullable=False, index=True)
    data_hora_fim = Column(DateTime, nullable=False)

    # ID do evento criado no Google Calendar
    google_event_id = Column(String(255), nullable=True)

    agendamento = relationship("Agendamento", back_populates="itens")
    servico = relationship("Servico")
    profissional = relationship("Profissional", back_populates="agendamentos")


# ---------------------------------------------------------------------------
# Pagamentos
# ---------------------------------------------------------------------------

class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    agendamento_id = Column(Integer, ForeignKey("agendamentos.id"), nullable=False, unique=True)
    valor = Column(Numeric(10, 2), nullable=False)
    metodo = Column(String(50), nullable=False)   # ex: "pix", "cartao_credito", "dinheiro"
    pago_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    registrado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    agendamento = relationship("Agendamento", back_populates="pagamento")


# ---------------------------------------------------------------------------
# Tokens Google OAuth (armazenados no banco, nunca em arquivo)
# ---------------------------------------------------------------------------

class GoogleToken(Base):
    __tablename__ = "google_tokens"

    id = Column(Integer, primary_key=True, index=True)
    # Identifica qual agenda/conta este token pertence (ex: "principal")
    account_label = Column(String(100), unique=True, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------------------------------------------------------------------------
# Planilhas mensais do Google Sheets (rastreio de IDs criados)
# ---------------------------------------------------------------------------

class PlanilhaMensal(Base):
    __tablename__ = "planilhas_mensais"

    id = Column(Integer, primary_key=True, index=True)
    # "2026-04" — chave única por mês
    mes = Column(String(7), unique=True, nullable=False, index=True)
    spreadsheet_id = Column(String(255), nullable=False)
    spreadsheet_url = Column(String(500), nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    ultima_exportacao = Column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# Controle de Estoque — Produtos
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Categorias de Produto
# ---------------------------------------------------------------------------

class CategoriaProduto(Base):
    __tablename__ = "categorias_produto"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    categoria = Column(String(100), nullable=True)
    marca = Column(String(100), nullable=True)
    preco_custo = Column(Numeric(10, 2), nullable=True)
    preco_venda = Column(Numeric(10, 2), nullable=True)
    estoque_atual = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ---------------------------------------------------------------------------
# Tarefas Internas (agenda pessoal da recepção, sem vínculo com cliente)
# ---------------------------------------------------------------------------

class TarefaInterna(Base):
    __tablename__ = "tarefas_internas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    data_hora_inicio = Column(DateTime, nullable=False, index=True)
    data_hora_fim = Column(DateTime, nullable=True)
    # Usuário responsável (opcional — pode ser uma tarefa geral da recepção)
    responsavel_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    concluida = Column(Boolean, default=False, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

    responsavel = relationship("Usuario", foreign_keys=[responsavel_id])
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
