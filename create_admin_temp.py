"""
Script temporário: cria usuário admin com senha padrão para recuperação de acesso.

USO:
  python create_admin_temp.py

DEPOIS DE USAR:
  1. Logue com admin / admin123
  2. Troque a senha pelo painel de Usuários
  3. Delete este arquivo e faça commit

SEGURANÇA:
  Não faça deploy deste arquivo em produção por mais tempo do que o necessário.
"""

from db.database import SessionLocal
from db.models import RoleEnum, Usuario
from core.security import hash_password
from datetime import datetime

USERNAME = "admin_temp"
PASSWORD = "admin123"

db = SessionLocal()
try:
    existente = db.query(Usuario).filter(Usuario.username == USERNAME).first()
    if existente:
        print(f"[!] Usuário '{USERNAME}' já existe. Nada foi criado.")
    else:
        usuario = Usuario(
            nome="Admin Temp",
            username=USERNAME,
            hashed_password=hash_password(PASSWORD),
            role=RoleEnum.admin,
            ativo=True,
            criado_em=datetime.utcnow(),
        )
        db.add(usuario)
        db.commit()
        print(f"[OK] Usuário criado!")
        print(f"     username : {USERNAME}")
        print(f"     senha    : {PASSWORD}")
        print(f"     perfil   : admin")
        print()
        print("[!] LEMBRE-SE de deletar este arquivo após usar.")
finally:
    db.close()
