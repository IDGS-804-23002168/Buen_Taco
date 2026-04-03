from flask import Blueprint


disponibilidad_bp = Blueprint("disponibilidad", __name__)

from . import routes
