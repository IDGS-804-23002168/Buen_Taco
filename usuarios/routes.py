import functools
from datetime import datetime

from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from usuarios import usuarios_bp
from usuarios.forms import CrearUsuarioForm, EditarUsuarioForm
from models import db, Usuario, Rol, UsuariosRoles
from auth.routes import _registrar_log


# ---------------------------------------------------------------------------
# DECORADOR: solo administrador
# ---------------------------------------------------------------------------
def solo_admin(f):
    @functools.wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        ur = UsuariosRoles.query.filter_by(
            UsuarioId=current_user.UsuarioId, Activo=True
        ).first()
        if not ur:
            abort(403)
        rol = Rol.query.get(ur.RolId)
        if not rol or rol.Nombre != 'Administrador':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------------------------
# HELPER: obtener rol activo de un usuario
# ---------------------------------------------------------------------------
def _get_rol_activo(usuario_id):
    ur = UsuariosRoles.query.filter_by(UsuarioId=usuario_id, Activo=True).first()
    if ur:
        return Rol.query.get(ur.RolId)
    return None


# ---------------------------------------------------------------------------
# RUTA: INDEX
# ---------------------------------------------------------------------------
@usuarios_bp.route('/')
@solo_admin
def index():
    filtro = request.args.get('filtro', 'todos')

    if filtro == 'activos':
        usuarios = Usuario.query.filter_by(Activo=True).order_by(Usuario.Nombre).all()
    elif filtro == 'inactivos':
        usuarios = Usuario.query.filter_by(Activo=False).order_by(Usuario.Nombre).all()
    else:
        usuarios = Usuario.query.order_by(Usuario.Nombre).all()

    usuarios_data = []
    for u in usuarios:
        rol = _get_rol_activo(u.UsuarioId)
        usuarios_data.append({
            'usuario': u,
            'rol': rol.Nombre if rol else 'Sin rol'
        })

    return render_template('Usuarios/index.html', usuarios_data=usuarios_data, filtro=filtro)


# ---------------------------------------------------------------------------
# RUTA: CREAR
# ---------------------------------------------------------------------------
@usuarios_bp.route('/crear', methods=['GET', 'POST'])
@solo_admin
def crear():
    roles = Rol.query.order_by(Rol.Nombre).all()
    form = CrearUsuarioForm()
    form.rol_id.choices = [(r.RolId, r.Nombre) for r in roles]
    # Opción vacía al inicio
    form.rol_id.choices.insert(0, (0, '— Selecciona un rol —'))

    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            Nombre=form.nombre.data.strip(),
            Username=form.username.data.strip(),
            Email=form.email.data.strip().lower(),
            PasswordHash=generate_password_hash(
                form.password.data, method='pbkdf2:sha256', salt_length=16
            ),
            Salt='',
            FechaCambioPassword=datetime.utcnow(),
            RequiereCambioPassword=True,
            Activo=True,
            Bloqueado=False,
            IntentosFallidos=0
        )
        db.session.add(nuevo_usuario)
        db.session.flush()

        ur = UsuariosRoles(
            UsuarioId=nuevo_usuario.UsuarioId,
            RolId=form.rol_id.data,
            FechaAsignacion=datetime.utcnow(),
            Activo=True
        )
        db.session.add(ur)
        db.session.commit()

        _registrar_log(
            "USUARIO_CREADO",
            usuario_id=current_user.UsuarioId,
            detalle=f"nuevo_usuario={form.username.data}"
        )
        flash(f"Usuario '{form.username.data}' creado correctamente.", "success")
        return redirect(url_for('usuarios.index'))

    return render_template('Usuarios/crear.html', form=form)


# ---------------------------------------------------------------------------
# RUTA: EDITAR
# ---------------------------------------------------------------------------
@usuarios_bp.route('/<int:usuario_id>/editar', methods=['GET', 'POST'])
@solo_admin
def editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    roles = Rol.query.order_by(Rol.Nombre).all()
    rol_actual = _get_rol_activo(usuario_id)

    form = EditarUsuarioForm(usuario_id=usuario_id)

    # 🔥 IMPORTANTE: primero los choices
    form.rol_id.choices = [(r.RolId, r.Nombre) for r in roles]

    # 🔥 Solo en GET llenas los datos
    if request.method == 'GET':
        form.nombre.data = usuario.Nombre
        form.email.data = usuario.Email
        form.rol_id.data = rol_actual.RolId if rol_actual else None

    if form.validate_on_submit():
        usuario.Nombre = form.nombre.data.strip()
        usuario.Email  = form.email.data.strip().lower()

        if not rol_actual or rol_actual.RolId != form.rol_id.data:
            UsuariosRoles.query.filter_by(UsuarioId=usuario_id).update({'Activo': False})
            db.session.add(UsuariosRoles(
                UsuarioId=usuario_id,
                RolId=form.rol_id.data,
                FechaAsignacion=datetime.utcnow(),
                Activo=True
            ))

        db.session.commit()

        _registrar_log(
            "USUARIO_EDITADO",
            usuario_id=current_user.UsuarioId,
            detalle=f"editado={usuario.Username}"
        )
        flash(f"Usuario '{usuario.Username}' actualizado correctamente.", "success")
        return redirect(url_for('usuarios.index'))

    return render_template('Usuarios/editar.html',
                           form=form, usuario=usuario, rol_actual=rol_actual)


# ---------------------------------------------------------------------------
# RUTA: TOGGLE ACTIVO
# ---------------------------------------------------------------------------
@usuarios_bp.route('/<int:usuario_id>/toggle', methods=['POST'])
@solo_admin
def toggle_activo(usuario_id):
    if usuario_id == current_user.UsuarioId:
        flash("No puedes desactivarte a ti mismo.", "warning")
        return redirect(url_for('usuarios.index'))

    usuario = Usuario.query.get_or_404(usuario_id)
    filtro = request.form.get('filtro', 'todos')
    usuario.Activo = not usuario.Activo

    if not usuario.Activo:
        usuario.Bloqueado = False
        usuario.IntentosFallidos = 0
        accion, msg, cat = "USUARIO_DESACTIVADO", f"Usuario '{usuario.Username}' desactivado.", "warning"
    else:
        accion, msg, cat = "USUARIO_ACTIVADO", f"Usuario '{usuario.Username}' activado.", "success"

    db.session.commit()
    _registrar_log(accion, usuario_id=current_user.UsuarioId, detalle=f"afectado={usuario.Username}")
    flash(msg, cat)
    return redirect(url_for('usuarios.index', filtro=filtro))