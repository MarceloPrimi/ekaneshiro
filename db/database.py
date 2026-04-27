from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # Reconecta automaticamente se a conexão cair
    pool_recycle=3600,       # Recicla conexões a cada hora (evita timeout do MySQL)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependency injetável via FastAPI para obter sessão do banco."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
