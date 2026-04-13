import os
import logging
import logging.handlers
from datetime import datetime
from flask_login import current_user
from mongo_client import logs_col

# Configuración del logger similar al módulo Auth
if not os.path.exists('logs'):
    os.makedirs('logs')

# Intentar obtener el logger 'auth' para reutilizar configuración si ya existe
logger = logging.getLogger('auth')
if not logger.handlers:
    handler = logging.handlers.RotatingFileHandler(
        'logs/auth.log',
        maxBytes=1_000_000,
        backupCount=10
    )
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

def registrar_movimiento(accion, detalle="", nivel="INFO"):
    """
    Registra un movimiento en el log de archivos y en MongoDB.
    Captura automáticamente el UsuarioId y Nombre del current_user si está disponible.
    """
    usuario_id = None
    nombre_usuario = "Sistema"
    
    try:
        if current_user and current_user.is_authenticated:
            usuario_id = current_user.UsuarioId
            nombre_usuario = getattr(current_user, 'Nombre', 'Usuario')
    except Exception:
        pass

    mensaje = f"accion={accion} usuario_id={usuario_id} nombre={nombre_usuario} detalle={detalle}"
    
    if nivel == "WARNING":
        logger.warning(mensaje)
    elif nivel == "ERROR":
        logger.error(mensaje)
    else:
        logger.info(mensaje)

    # Auditoría en MongoDB
    try:
        logs_col.insert_one({
            "accion"        : accion,
            "usuario_id"    : usuario_id,
            "nombre_usuario": nombre_usuario,
            "detalle"       : detalle,
            "nivel"         : nivel,
            "timestamp"     : datetime.utcnow()
        })
    except Exception as e:
        print(f"Error al registrar log en MongoDB: {e}")
