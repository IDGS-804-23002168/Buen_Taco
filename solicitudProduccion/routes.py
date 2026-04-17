from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime
from flask_login import login_required, current_user
from functools import wraps
from . import solicitudes_bp
from models import db, Producto, SolicitudProduccion, SolicitudDetalle, CategoriaProducto
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
                notas = request.form.get('notas_solicitud', '')
                nueva_solicitud = SolicitudProduccion(Estado="Pendiente", NotasSolicitud=notas)
                db.session.add(nueva_solicitud)
                db.session.flush()  # Obtener el SolicitudId

                # Crear un detalle por cada producto, validando stock nuevamente por seguridad
                for producto_id, cantidad in items:
                    stock_disponible = obtener_disponibilidad_producto(producto_id)
                    if cantidad > stock_disponible:
                        producto = Producto.query.get(producto_id)
                        db.session.rollback()
                        flash(f"Error: No hay suficiente stock para '{producto.Nombre}'. Disponible: {stock_disponible}.", "danger")
                        return redirect(url_for("solicitudes.index"))

                    detalle = SolicitudDetalle(
                        SolicitudId=nueva_solicitud.SolicitudId,
                        ProductoId=producto_id,
                        CantidadSolicitada=cantidad,
                    )
                    db.session.add(detalle)

                db.session.commit()
                
                # Establecer sesión para el modal de éxito
                session['modal_solicitud'] = {
                    'id': nueva_solicitud.SolicitudId,
                    'hora': datetime.utcnow().strftime('%H:%M:%S'),
                    'cantidad': sum(cantidad for _, cantidad in items)
                }

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
    for p in productos:
        p.disponible = obtener_disponibilidad_producto(p.ProductoId) # Inyectar disponibilidad
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
