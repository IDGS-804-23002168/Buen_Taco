from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from . import solicitudes_bp
from models import db, Producto, SolicitudProduccion, SolicitudDetalle, CategoriaProducto


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


@solicitudes_bp.route("/solicitudes", methods=["GET", "POST"])
@login_required
@roles_required("Administrador", "Vendedor")
def index():
    if request.method == "POST":
        hubo_pedidos = False
        try:
            # Recopilar los productos seleccionados
            items = []
            for key, value in request.form.items():
                if key.startswith("prod_"):
                    producto_id = int(key.split("_")[1])
                    cantidad = int(value)
                    if cantidad > 0:
                        items.append((producto_id, cantidad))

            if items:
                # Crear UNA solicitud (encabezado)
                nueva_solicitud = SolicitudProduccion(Estado="Pendiente")
                db.session.add(nueva_solicitud)
                db.session.flush()  # Obtener el SolicitudId

                # Crear un detalle por cada producto
                for producto_id, cantidad in items:
                    detalle = SolicitudDetalle(
                        SolicitudId=nueva_solicitud.SolicitudId,
                        ProductoId=producto_id,
                        CantidadSolicitada=cantidad,
                    )
                    db.session.add(detalle)

                db.session.commit()
                flash(
                    f"¡Solicitud #{nueva_solicitud.SolicitudId} enviada a la cocina con {len(items)} producto(s)!",
                    "success",
                )
            else:
                flash(
                    "El carrito estaba vacío. Selecciona al menos un producto.",
                    "warning",
                )

        except Exception as e:
            db.session.rollback()
            flash("Error al procesar la solicitud.", "danger")

        return redirect(url_for("solicitudes.index"))

    productos = Producto.query.filter_by(Activo=True).all()
    categorias = CategoriaProducto.query.all()
    return render_template(
        "solicitudProduccion/index.html", productos=productos, categorias=categorias
    )


@solicitudes_bp.route("/solicitudes/historial")
@login_required
@roles_required("Administrador", "Vendedor")
def historial():
    """Vista de historial: todas las solicitudes con todos los estados."""
    solicitudes = (
        SolicitudProduccion.query
        .order_by(SolicitudProduccion.Fecha.desc())
        .all()
    )
    return render_template(
        "solicitudProduccion/historial.html", solicitudes=solicitudes
    )
