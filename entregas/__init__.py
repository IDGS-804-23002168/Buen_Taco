from flask import Blueprint

entregas_bp = Blueprint('entregas', __name__)

from . import routes
