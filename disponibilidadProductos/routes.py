from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func
from . import disponibilidad_bp
from models import db, Producto, MovimientoProducto, CategoriaProducto


# --- DECORADOR PARA LOS ROLES ---
def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            roles_usuario = [ur.rol.Nombre for ur in current_user.roles if ur.Activo]
            if any(rol in roles_usuario for rol in roles):
                return fn(*args, **kwargs)
            return redirect(url_for("index"))

        return decorated_view

    return wrapper


@disponibilidad_bp.route("/disponibilidad", methods=["GET"])
@login_required
@roles_required("Administrador", "Vendedor")  # Ajusta según necesites
def index():
    productos = Producto.query.filter_by(Activo=True).all()
    categorias = CategoriaProducto.query.all()

    # Lista para guardar solo los productos que la cocina ya preparó (stock > 0)
    productos_en_mostrador = []

    for p in productos:
        # Sumamos todos los movimientos de este producto (Entradas de la cocina - Salidas de ventas)
        stock = (
            db.session.query(func.coalesce(func.sum(MovimientoProducto.Cantidad), 0))
            .filter_by(ProductoId=p.ProductoId)
            .scalar()
        )

        # Le asignamos temporalmente el valor al objeto para usarlo en el HTML
        p.stock_actual = int(stock)

        # Opcional: Si solo quieres mostrar los que SÍ tienen existencias, descomenta la siguiente línea:
        # if p.stock_actual > 0:
        productos_en_mostrador.append(p)

    return render_template(
        "disponibilidadProductos/index.html",
        productos=productos_en_mostrador,
        categorias=categorias,
    )
