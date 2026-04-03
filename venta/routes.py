from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func
from datetime import datetime
from . import ventas_bp

from models import (
    db,
    Producto,
    CategoriaProducto,
    MovimientoProducto,
    Venta,
    VentaDetalle,
    SolicitudProduccion,
    SolicitudDetalle,
)


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


@ventas_bp.route("/ventas", methods=["GET", "POST"])
@login_required
@roles_required("Administrador", "Vendedor", "Cajero")
def index():
    if request.method == "POST":
        # Recibir las solicitudes seleccionadas
        solicitud_ids = request.form.getlist("solicitud_ids")
        metodo_pago = request.form.get("metodo_pago", "Efectivo")

        if not solicitud_ids:
            flash("Selecciona al menos una solicitud terminada para vender.", "warning")
            return redirect(url_for("ventas.index"))

        try:
            total_venta = 0.0
            items_a_vender = []
            solicitudes_seleccionadas = []

            for sid in solicitud_ids:
                solicitud = SolicitudProduccion.query.get(int(sid))
                if not solicitud or solicitud.Estado != "Realizada":
                    flash(
                        f"La solicitud #{sid} no está disponible para venta.",
                        "warning",
                    )
                    return redirect(url_for("ventas.index"))

                solicitudes_seleccionadas.append(solicitud)

                # Recopilar detalle de cada solicitud
                for detalle in solicitud.detalles:
                    producto = detalle.producto
                    cantidad = detalle.CantidadSolicitada
                    precio = float(producto.Precio) if producto.Precio else 0.0
                    subtotal = precio * cantidad
                    total_venta += subtotal

                    # Validar stock de producto terminado
                    stock_actual = (
                        db.session.query(
                            func.coalesce(func.sum(MovimientoProducto.Cantidad), 0)
                        )
                        .filter_by(ProductoId=producto.ProductoId)
                        .scalar()
                    )

                    if stock_actual < cantidad:
                        flash(
                            f"Stock insuficiente de {producto.Nombre}. Disponible: {stock_actual}, Necesario: {cantidad}.",
                            "danger",
                        )
                        return redirect(url_for("ventas.index"))

                    items_a_vender.append(
                        {
                            "producto_id": producto.ProductoId,
                            "cantidad": cantidad,
                            "precio": precio,
                            "subtotal": subtotal,
                        }
                    )

            # Crear la venta
            nueva_venta = Venta(
                EsEnLinea=False,
                Fecha=datetime.now(),
                Total=total_venta,
            )
            db.session.add(nueva_venta)
            db.session.flush()

            # Crear detalles y descontar inventario
            for item in items_a_vender:
                venta_detalle = VentaDetalle(
                    VentaId=nueva_venta.VentaId,
                    ProductoId=item["producto_id"],
                    Cantidad=item["cantidad"],
                    PrecioUnitario=item["precio"],
                    Subtotal=item["subtotal"],
                )
                db.session.add(venta_detalle)

                mov_salida = MovimientoProducto(
                    ProductoId=item["producto_id"],
                    TipoMovimiento="VENTA",
                    Cantidad=-item["cantidad"],
                    Fecha=datetime.now(),
                    ReferenciaId=nueva_venta.VentaId,
                )
                db.session.add(mov_salida)

            # Marcar solicitudes como vendidas
            for solicitud in solicitudes_seleccionadas:
                solicitud.Estado = "Vendida"

            db.session.commit()
            flash(
                f"¡Venta #{nueva_venta.VentaId} registrada con éxito! Total: ${total_venta:.2f}",
                "success",
            )

        except Exception as e:
            db.session.rollback()
            flash("Error de base de datos al procesar la venta.", "danger")
            print(f"Error técnico: {e}")

        return redirect(url_for("ventas.index"))

    # GET: Mostrar solicitudes con estado "Realizada"
    solicitudes_terminadas = (
        SolicitudProduccion.query
        .filter_by(Estado="Realizada")
        .order_by(SolicitudProduccion.Fecha.desc())
        .all()
    )

    return render_template(
        "venta/index.html",
        solicitudes=solicitudes_terminadas,
    )
