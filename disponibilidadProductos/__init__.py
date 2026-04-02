from flask import Blueprint

# Definimos el Blueprint
disponibilidad_bp = Blueprint("disponibilidad", __name__)

from . import routes
