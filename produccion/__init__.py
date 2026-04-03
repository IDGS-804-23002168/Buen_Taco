from flask import Blueprint

produccion_bp = Blueprint("produccion", __name__)

from . import routes