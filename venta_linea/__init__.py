from flask import Blueprint

# Creamos el blueprint
venta_linea_bp = Blueprint(
    'venta_linea',
    __name__,
    url_prefix='/venta_linea'  # todas las rutas empiezan con /venta_linea
)

# Importamos las rutas
from . import routes