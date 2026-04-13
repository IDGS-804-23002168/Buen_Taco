from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func
from . import disponibilidad_bp
from models import db, Producto, MovimientoProducto, CategoriaProducto
from utils.stock_util import obtener_disponibilidad_producto


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
            flash("No tienes permiso para ver esta página.", "danger")
            return redirect(url_for("index"))

        return decorated_view

    return wrapper


def _get_roles_usuario():
    """Obtiene la lista de roles del usuario actual."""
    if not current_user.is_authenticated:
        return []
    return [ur.rol.Nombre for ur in current_user.roles if ur.Activo]


@disponibilidad_bp.route("/disponibilidad", methods=["GET"])
@login_required
@roles_required("Administrador", "Vendedor", "Cocinero")
def index():
    # Mostrar TODOS los productos (activos e inactivos) para Admin y Cocinero
    roles = _get_roles_usuario()
    puede_toggle = ('Administrador' in roles or 'Cocinero' in roles)

    if puede_toggle:
        productos = Producto.query.all()
    else:
        # Vendedor solo ve los activos
        productos = Producto.query.filter_by(Activo=True).all()

    categorias = CategoriaProducto.query.all()

    productos_en_mostrador = []

    # for p in productos:
    #     stock = (
    #         db.session.query(func.coalesce(func.sum(MovimientoProducto.Cantidad), 0))
    #         .filter_by(ProductoId=p.ProductoId)
    #         .scalar()
    #     )
    #     p.stock_actual = int(stock)
    #     productos_en_mostrador.append(p)
    
    for p in productos:
        p.stock_actual = obtener_disponibilidad_producto(p.ProductoId)
        productos_en_mostrador.append(p)

    return render_template(
        "disponibilidadProductos/index.html",
        productos=productos_en_mostrador,
        categorias=categorias,
        puede_toggle=puede_toggle,
    )


@disponibilidad_bp.route("/disponibilidad/toggle/<int:producto_id>", methods=["POST"])
@login_required
@roles_required("Administrador", "Cocinero")
def toggle_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    try:
        producto.Activo = not producto.Activo
        db.session.commit()
        estado = "activado" if producto.Activo else "desactivado"
        flash(f'Producto "{producto.Nombre}" {estado} correctamente.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error al cambiar el estado del producto.', 'danger')
    return redirect(url_for("disponibilidad.index"))
