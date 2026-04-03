from flask import Blueprint

# Creamos el blueprint
productos_bp = Blueprint(
    'productos',
    __name__,
    url_prefix='/productos'  # todas las rutas empiezan con /productos
)

# Importamos las rutas
from . import routes