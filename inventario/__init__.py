from flask import Blueprint

inventario_bp = Blueprint('inventario', __name__, template_folder='templates')

from . import routes