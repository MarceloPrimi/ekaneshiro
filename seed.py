"""
Cria o primeiro usuário admin no banco.
Execute uma única vez após criar as tabelas:

    python seed.py
"""
from db.database import SessionLocal
from db.models import Usuario, RoleEnum
from core.security import hash_password


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(Usuario).filter(Usuario.role == RoleEnum.admin).first():
            print("Admin já existe. Nenhuma ação necessária.")
            return

        admin = Usuario(
            nome="Admin Kaneshiro",
            email="admin@kaneshiro.com",
            hashed_password=hash_password("admin@123"),
            role=RoleEnum.admin,
        )
        db.add(admin)
        db.commit()
        print("✓ Admin criado com sucesso!")
        print(f"  Email : {admin.email}")
        print(f"  Senha : admin@123")
        print("  ⚠️  Troque a senha após o primeiro login.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
