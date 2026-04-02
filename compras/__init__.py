from flask import Blueprint

# Definimos tu módulo de compras
compras = Blueprint('compras', __name__, template_folder='../templates')

from . import routes