import os
import random
import string
import logging
import logging.handlers
from datetime import datetime, timedelta
import secrets

from flask import (
    render_template, request, redirect, url_for,
    flash, session
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from auth import auth_bp
from models import db, Usuario, Rol, UsuariosRoles

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DEL LOGGER A ARCHIVO (A09)
# ---------------------------------------------------------------------------
if not os.path.exists('logs'):
    os.makedirs('logs')

handler = logging.handlers.RotatingFileHandler(
    'logs/auth.log',
    maxBytes=1_000_000,
    backupCount=10
)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))

logger = logging.getLogger('auth')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# ---------------------------------------------------------------------------
# CONTRASEÑAS DÉBILES (A07)
# ---------------------------------------------------------------------------
WEAK_PASSWORDS = {
    "password", "12345678", "123456789", "qwerty123", "password1",
    "iloveyou", "admin123", "letmein1", "welcome1", "monkey123",
    "sunshine", "princess", "football", "superman", "batman123",
    "trustno1", "dragon12", "master12", "abc12345", "passw0rd",
}

ROLE_REDIRECTS = {
    'Administrador':     'dashboard.index',
    'Encargado_Almacen': 'index',
    'Cocinero':          'index',
    'Vendedor':          'index',
    'Usuario':           'venta_linea.index',
}

# ---------------------------------------------------------------------------
# EXPIRACIÓN PERIÓDICA DE CONTRASEÑA
# ---------------------------------------------------------------------------
DIAS_EXPIRACION_PASSWORD = 90
DIAS_AVISO_PASSWORD      = 80


# ---------------------------------------------------------------------------
# HELPERS INTERNOS
# ---------------------------------------------------------------------------
def _get_active_role(user):
    ur = UsuariosRoles.query.filter_by(UsuarioId=user.UsuarioId, Activo=True).first()
    if ur:
        rol = Rol.query.get(ur.RolId)
        return rol.Nombre if rol else 'Usuario'
    return 'Usuario'


def redirect_by_role(user):
    rol = _get_active_role(user)
    endpoint = ROLE_REDIRECTS.get(rol, 'auth.login')
    return redirect(url_for(endpoint))


def _validar_password_segura(password):
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not any(c.isupper() for c in password):
        return False, "Debe contener al menos una letra mayúscula."
    if not any(c.islower() for c in password):
        return False, "Debe contener al menos una letra minúscula."
    if not any(c.isdigit() for c in password):
        return False, "Debe contener al menos un número."
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        return False, "Debe contener al menos un carácter especial (!@#$%...)."
    if password.lower() in WEAK_PASSWORDS:
        return False, "Esa contraseña es demasiado común. Elige una más segura."
    return True, ""


def _generar_token_2fa(longitud=6):
    return ''.join([str(secrets.randbelow(10)) for _ in range(longitud)])


def _generar_token_recuperacion(longitud=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=longitud))


def _registrar_log(accion, usuario_id=None, detalle="", nivel="INFO"):
    mensaje = f"accion={accion} usuario_id={usuario_id} detalle={detalle}"
    if nivel == "WARNING":
        logger.warning(mensaje)
    elif nivel == "ERROR":
        logger.error(mensaje)
    else:
        logger.info(mensaje)

    # Auditoría en MongoDB (RS 020)
    try:
        from mongo_client import logs_col
        logs_col.insert_one({
            "accion"    : accion,
            "usuario_id": usuario_id,
            "detalle"   : detalle,
            "nivel"     : nivel,
            "timestamp" : datetime.utcnow()
        })
    except Exception:
        pass


def _completar_login(usuario):
    ultimo = usuario.UltimoLogin
    usuario.UltimoLogin = datetime.utcnow()
    db.session.commit()

    login_user(usuario, remember=False)
    session.permanent = True

    _registrar_log("LOGIN_EXITOSO", usuario_id=usuario.UsuarioId)

    ultimo_str = ultimo.strftime('%d/%m/%Y %H:%M') if ultimo else 'Primera vez'
    flash(f"Bienvenido, {usuario.Nombre}. Último acceso: {ultimo_str}.", "success")


def _enviar_correo_2fa(email, token):
    try:
        from flask_mail import Message
        from app import mail
        msg = Message(
            subject="Código de verificación - El Buen Taco",
            recipients=[email],
            body=(
                f"Tu código de verificación es: {token}\n"
                f"Este código expira en 10 minutos.\n\n"
                f"Si no solicitaste este código, ignora este mensaje."
            )
        )
        mail.send(msg)
    except Exception as e:
        logger.error(f"Error al enviar correo 2FA a {email}: {e}")


def _enviar_correo_recuperacion(email, link):
    try:
        from flask_mail import Message
        from app import mail
        msg = Message(
            subject="Recuperación de contraseña - El Buen Taco",
            recipients=[email],
            body=(
                f"Haz clic en el siguiente enlace para restablecer tu contraseña:\n"
                f"{link}\n\n"
                f"Este enlace expira en 1 hora.\n"
                f"Si no solicitaste esto, ignora este mensaje."
            )
        )
        mail.send(msg)
    except Exception as e:
        logger.error(f"Error al enviar correo recuperación a {email}: {e}")


# ---------------------------------------------------------------------------
# HELPER: VERIFICAR EXPIRACIÓN PERIÓDICA DE CONTRASEÑA
# ---------------------------------------------------------------------------
def _verificar_expiracion_password(usuario):
    """
    Revisa si la contraseña del usuario ha expirado o está próxima a expirar.
    - Si han pasado DIAS_EXPIRACION_PASSWORD días: marca RequiereCambioPassword = True.
    - Si están entre DIAS_AVISO_PASSWORD y DIAS_EXPIRACION_PASSWORD: muestra aviso.
    - Si FechaCambioPassword es None, no hace nada para no romper cuentas existentes.
    Retorna True si se forzó el cambio, False en cualquier otro caso.
    """
    if not usuario.FechaCambioPassword:
        return False

    dias = (datetime.utcnow() - usuario.FechaCambioPassword).days

    if dias >= DIAS_EXPIRACION_PASSWORD:
        usuario.RequiereCambioPassword = True
        db.session.commit()
        _registrar_log("PASSWORD_EXPIRADO", usuario_id=usuario.UsuarioId,
                       detalle=f"{dias} días sin cambio", nivel="WARNING")
        return True

    if dias >= DIAS_AVISO_PASSWORD:
        dias_restantes = DIAS_EXPIRACION_PASSWORD - dias
        flash(f"Tu contraseña expira en {dias_restantes} día(s). Te recomendamos cambiarla pronto.", "warning")

    return False


# ---------------------------------------------------------------------------
# RUTA: LOGIN
# ---------------------------------------------------------------------------
@auth_bp.route('/acceso', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == 'POST':
        captcha_input = request.form.get('captcha', '').strip().upper()
        expected_captcha = session.get('captcha_text', '')

        if not expected_captcha or captcha_input != expected_captcha:
            flash("El código Captcha es incorrecto. Inténtalo de nuevo.", "danger")
            session['captcha_text'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            return render_template('auth/index.html')

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash("Completa todos los campos.", "danger")
            return render_template('auth/index.html')

        usuario = Usuario.query.filter_by(Username=username).first()

        if not usuario:
            _registrar_log("LOGIN_FALLIDO", detalle=f"username={username} no existe", nivel="WARNING")
            flash("Credenciales incorrectas.", "danger")
            return render_template('auth/index.html')

        if usuario.Bloqueado:
            flash("Tu cuenta está bloqueada. Contacta al administrador.", "warning")
            return render_template('auth/index.html')

        if not usuario.Activo:
            flash("Tu cuenta ha sido desactivada.", "warning")
            return render_template('auth/index.html')

        if not check_password_hash(usuario.PasswordHash, password):
            usuario.IntentosFallidos = (usuario.IntentosFallidos or 0) + 1
            if usuario.IntentosFallidos >= 3:
                usuario.Bloqueado = True
                usuario.FechaBloqueo = datetime.utcnow()
                db.session.commit()
                _registrar_log("CUENTA_BLOQUEADA", usuario_id=usuario.UsuarioId,
                                detalle="3 intentos fallidos", nivel="WARNING")
                flash("Cuenta bloqueada por 3 intentos fallidos. Contacta al administrador.", "danger")
            else:
                db.session.commit()
                restantes = 3 - usuario.IntentosFallidos
                flash(f"Contraseña incorrecta. Te quedan {restantes} intento(s).", "danger")
                _registrar_log("LOGIN_FALLIDO", usuario_id=usuario.UsuarioId,
                                detalle=f"intento {usuario.IntentosFallidos}", nivel="WARNING")
            return render_template('auth/index.html')

        usuario.IntentosFallidos = 0

        # ── VERIFICACIÓN DE EXPIRACIÓN PERIÓDICA ──────────────────────────
        # Se ejecuta antes de RequiereCambioPassword para que una contraseña
        # expirada también active el flujo de cambio obligatorio.
        _verificar_expiracion_password(usuario)
        # ──────────────────────────────────────────────────────────────────

        if usuario.RequiereCambioPassword:
            db.session.commit()
            _completar_login(usuario)
            flash("Por seguridad, debes cambiar tu contraseña.", "warning")
            return redirect(url_for('auth.cambiar_password'))

        # Siempre enviar 2FA si no requiere cambio de contraseña (ignorando TwoFactorHabilitado)
        token = _generar_token_2fa()
        usuario.Token2FA = token
        usuario.Token2FAExpiracion = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()

        session['pre_auth_user_id'] = usuario.UsuarioId
        session['pre_auth_user_username'] = usuario.Username

        _enviar_correo_2fa(usuario.Email, token)
        _registrar_log("2FA_ENVIADO", usuario_id=usuario.UsuarioId)

        flash("Hemos enviado un código de verificación a tu correo.", "info")
        return redirect(url_for('auth.verificar_2fa'))

    session['captcha_text'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return render_template('auth/index.html')


# ---------------------------------------------------------------------------
# RUTA: VERIFICACIÓN 2FA
# ---------------------------------------------------------------------------
@auth_bp.route('/verificar-acceso', methods=['GET', 'POST'])
def verificar_2fa():
    user_id = session.get('pre_auth_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    usuario = Usuario.query.get(user_id)
    if not usuario:
        session.clear()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        token_ingresado = request.form.get('token', '').strip()

        if not token_ingresado:
            flash("Ingresa el código de verificación.", "danger")
            return render_template('auth/two_factor.html')

        # if usuario.Token2FAExpiracion < datetime.utcnow():
        #     _registrar_log("2FA_EXPIRADO", usuario_id=user_id, nivel="WARNING")
        #     flash("El código expiró. Inicia sesión nuevamente.", "warning")
        #     session.pop('pre_auth_user_id', None)
        #     session.pop('pre_auth_user_username', None)
        #     return redirect(url_for('auth.login'))
        
        if not usuario.Token2FAExpiracion or usuario.Token2FAExpiracion < datetime.utcnow():
            _registrar_log("2FA_EXPIRADO", usuario_id=user_id, nivel="WARNING")
            flash("El código expiró o no es válido. Inicia sesión nuevamente.", "warning")
            session.pop('pre_auth_user_id', None)
            session.pop('pre_auth_user_username', None)
            return redirect(url_for('auth.login'))

        if usuario.Token2FA != token_ingresado:
            _registrar_log("2FA_FALLIDO", usuario_id=user_id, nivel="WARNING")
            flash("Código incorrecto.", "danger")
            return render_template('auth/two_factor.html')

        usuario.Token2FA = None
        usuario.Token2FAExpiracion = None
        session.pop('pre_auth_user_id', None)
        session.pop('pre_auth_user_username', None)
        db.session.commit()

        _completar_login(usuario)
        return redirect_by_role(usuario)

    return render_template('auth/two_factor.html',
                           username=session.get('pre_auth_user_username', ''))


# ---------------------------------------------------------------------------
# RUTA: REGISTRO PÚBLICO
# ---------------------------------------------------------------------------
@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == 'POST':
        nombre   = request.form.get('nombre', '').strip()
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not all([nombre, username, email, password, confirm]):
            flash("Completa todos los campos.", "danger")
            return render_template('auth/registro.html')

        if password != confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template('auth/registro.html')

        valida, msg = _validar_password_segura(password)
        if not valida:
            flash(msg, "danger")
            return render_template('auth/registro.html')

        if Usuario.query.filter_by(Username=username).first():
            flash("El nombre de usuario ya está en uso.", "warning")
            return render_template('auth/registro.html')
        if Usuario.query.filter_by(Email=email).first():
            flash("El correo ya está registrado.", "warning")
            return render_template('auth/registro.html')

        password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        nuevo_usuario = Usuario(
            Nombre=nombre,
            Username=username,
            Email=email,
            PasswordHash=password_hash,
            Salt='',
            FechaCambioPassword=datetime.utcnow(),
            RequiereCambioPassword=False,
            Activo=True
        )
        db.session.add(nuevo_usuario)
        db.session.flush()

        rol_usuario = Rol.query.filter_by(Nombre='Usuario').first()
        if rol_usuario:
            ur = UsuariosRoles(
                UsuarioId=nuevo_usuario.UsuarioId,
                RolId=rol_usuario.RolId,
                FechaAsignacion=datetime.utcnow(),
                Activo=True
            )
            db.session.add(ur)

        db.session.commit()

        _registrar_log("REGISTRO_USUARIO", usuario_id=nuevo_usuario.UsuarioId,
                       detalle=f"username={username} email={email}")
        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/registro.html')


# ---------------------------------------------------------------------------
# RUTA: CAMBIAR CONTRASEÑA
# ---------------------------------------------------------------------------
@auth_bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    if request.method == 'POST':
        password_actual = request.form.get('password_actual', '')
        nueva_password  = request.form.get('nueva_password', '')
        confirmar       = request.form.get('confirmar_password', '')

        if not current_user.RequiereCambioPassword:
            if not check_password_hash(current_user.PasswordHash, password_actual):
                flash("La contraseña actual es incorrecta.", "danger")
                return render_template('auth/cambiar_password.html')

        if nueva_password != confirmar:
            flash("Las contraseñas nuevas no coinciden.", "danger")
            return render_template('auth/cambiar_password.html')

        valida, msg = _validar_password_segura(nueva_password)
        if not valida:
            flash(msg, "danger")
            return render_template('auth/cambiar_password.html')

        usuario = Usuario.query.get(current_user.UsuarioId)
        usuario.PasswordHash = generate_password_hash(nueva_password, method='pbkdf2:sha256', salt_length=16)
        usuario.FechaCambioPassword = datetime.utcnow()
        usuario.RequiereCambioPassword = False
        usuario.IntentosFallidos = 0
        db.session.commit()

        _registrar_log("CAMBIO_PASSWORD", usuario_id=usuario.UsuarioId)
        flash("Contraseña actualizada correctamente.", "success")
        return redirect_by_role(usuario)

    return render_template('auth/cambiar_password.html')


# ---------------------------------------------------------------------------
# RUTA: OLVIDÉ MI CONTRASEÑA
# ---------------------------------------------------------------------------
@auth_bp.route('/recuperar-acceso', methods=['GET', 'POST'])
def olvide_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()

        if email:
            usuario = Usuario.query.filter_by(Email=email, Activo=True).first()
            if usuario:
                token = _generar_token_recuperacion()
                usuario.TokenRecuperacion = token
                usuario.TokenRecuperacionExp = datetime.utcnow() + timedelta(hours=1)
                db.session.commit()

                link = url_for('auth.reset_password', token=token, _external=True)
                _enviar_correo_recuperacion(email, link)
                _registrar_log("PASSWORD_RESET_SOLICITADO", usuario_id=usuario.UsuarioId)

        flash("Si el correo existe en nuestro sistema, recibirás un enlace para restablecer tu contraseña.", "info")
        return redirect(url_for('auth.login'))

    return render_template('auth/olvide_password.html')


# ---------------------------------------------------------------------------
# RUTA: RESTABLECER CONTRASEÑA CON TOKEN
# ---------------------------------------------------------------------------
@auth_bp.route('/nueva-contrasena/<token>', methods=['GET', 'POST'])
def reset_password(token):
    usuario = Usuario.query.filter_by(TokenRecuperacion=token).first()
    if not usuario or usuario.TokenRecuperacionExp < datetime.utcnow():
        flash("El enlace no es válido o ha expirado.", "danger")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if password != confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template('auth/reset_password.html', token=token)

        valida, msg = _validar_password_segura(password)
        if not valida:
            flash(msg, "danger")
            return render_template('auth/reset_password.html', token=token)

        usuario.PasswordHash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        usuario.TokenRecuperacion = None
        usuario.TokenRecuperacionExp = None
        usuario.IntentosFallidos = 0
        usuario.Bloqueado = False
        usuario.FechaBloqueo = None
        usuario.FechaCambioPassword = datetime.utcnow()
        usuario.RequiereCambioPassword = False
        db.session.commit()

        _registrar_log("PASSWORD_RESETEADO", usuario_id=usuario.UsuarioId)
        flash("Contraseña actualizada exitosamente.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)


# ---------------------------------------------------------------------------
# RUTA: LOGOUT
# ---------------------------------------------------------------------------
@auth_bp.route('/salir')
@login_required
def logout():
    _registrar_log("LOGOUT", usuario_id=getattr(current_user, 'UsuarioId', None))
    logout_user()
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for('auth.login'))
