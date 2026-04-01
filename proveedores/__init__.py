from flask import Blueprint

# Creamos el blueprint
proveedores = Blueprint(
    'proveedores',
    __name__,
    url_prefix='/proveedores'  # todas las rutas empiezan con /proveedores
)

# Importamos las rutas
from . import routes