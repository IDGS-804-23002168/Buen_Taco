import os
from datetime import timedelta


class Config(object):
    # A02 - Clave secreta fuerte (en producción usar variable de entorno)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'C4mbi@M3EnPr0ducci0n!#2025')

    # A10 - CSRF habilitado
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora de validez del token CSRF

    # A07 - Sesión máxima 10 minutos
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
    SESSION_COOKIE_SECURE   = True     # Solo HTTPS en producción
    SESSION_COOKIE_HTTPONLY = True     # A07 - No accesible desde JS
    SESSION_COOKIE_SAMESITE = 'Lax'   # A10 - Mitigación CSRF

    # A05 - No propagar excepciones al cliente
    PROPAGATE_EXCEPTIONS = False


class DevelopmentConfig(Config):
    DEBUG = True   # A05 - Nunca True en producción

    # Base de datos (A05 - usar usuario con permisos mínimos, NO root)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:1234@localhost/Tacos_Buen_Taco'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Correo (Flask-Mail) - para 2FA y recuperación de contraseña
    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'mreancontl@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'pass')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'El Buen Taco <mreancontl@gmail.com>')

    # A05 - En desarrollo puedes bajar a False para local sin HTTPS
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MAIL_SERVER   = os.environ.get('MAIL_SERVER')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
