from flask import Blueprint

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

from usuarios import routes