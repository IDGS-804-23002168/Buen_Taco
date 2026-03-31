from app import app
from models import db, Usuario, Rol, UsuariosRoles
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    rol = Rol.query.filter_by(Nombre='Administrador').first()
    if not rol:
        rol = Rol(Nombre='Administrador', Descripcion='Acceso total', Activo=True)
        db.session.add(rol)
        db.session.flush()

    u = Usuario(
        Nombre='Administrador',
        Username='admin',
        Email='admin@buentaco.mx',
        PasswordHash=generate_password_hash('Admin@1234', method='pbkdf2:sha256', salt_length=16),
        Salt='',
        FechaCambioPassword=datetime.utcnow(),
        RequiereCambioPassword=False,
        TwoFactorHabilitado=False,
        Activo=True
    )
    db.session.add(u)
    db.session.flush()

    ur = UsuariosRoles(UsuarioId=u.UsuarioId, RolId=rol.RolId, Activo=True)
    db.session.add(ur)
    db.session.commit()
    print("Usuario creado OK")