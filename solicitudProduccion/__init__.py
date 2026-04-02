from flask import Blueprint

solicitudes_bp = Blueprint("solicitudes", __name__)

from . import routes
