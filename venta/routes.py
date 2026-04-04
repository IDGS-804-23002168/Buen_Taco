from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from . import ventas_bp

from models import (
    db,
    Producto,
    CategoriaProducto,
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
            flash("No tienes permiso para ver esta página.", "danger")
            return redirect(url_for("index"))

        return decorated_view

    return wrapper


@ventas_bp.route("/ventas", methods=["GET", "POST"])
@login_required
@roles_required("Administrador", "Vendedor", "Cajero")
def index():
    if request.method == "POST":
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

                for detalle in solicitud.detalles:
                    producto = detalle.producto
                    cantidad = detalle.CantidadSolicitada
                    precio = float(producto.Precio) if producto.Precio else 0.0
                    subtotal = precio * cantidad
                    total_venta += subtotal

                    items_a_vender.append(
                        {
                            "producto_id": producto.ProductoId,
                            "cantidad": cantidad,
                            "precio": precio,
                            "subtotal": subtotal,
                        }
                    )

            nueva_venta = Venta(
                EsEnLinea=False,
                Fecha=datetime.now(),
                Total=total_venta,
            )
            db.session.add(nueva_venta)
            db.session.flush()

            for item in items_a_vender:
                venta_detalle = VentaDetalle(
                    VentaId=nueva_venta.VentaId,
                    ProductoId=item["producto_id"],
                    Cantidad=item["cantidad"],
                    PrecioUnitario=item["precio"],
                    Subtotal=item["subtotal"],
                )
                db.session.add(venta_detalle)

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


@ventas_bp.route("/ventas/historial")
@login_required
@roles_required("Administrador", "Vendedor", "Cajero")
def historial():
    """Historial de ventas con filtros por fecha, tipo y agrupación."""
    # Parámetros de filtro
    vista = request.args.get('vista', 'dia')  # dia o mes
    tipo = request.args.get('tipo', 'todos')    # todos, fisico, linea
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')

    query = Venta.query

    # Filtrar por tipo
    if tipo == 'fisico':
        query = query.filter_by(EsEnLinea=False)
    elif tipo == 'linea':
        query = query.filter_by(EsEnLinea=True)

    # Filtrar por fechas
    if fecha_desde:
        try:
            desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Venta.Fecha >= desde)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Venta.Fecha < hasta)
        except ValueError:
            pass

    ventas = query.order_by(Venta.Fecha.desc()).all()

    # Agrupar ventas
    agrupado = {}
    for v in ventas:
        if v.Fecha:
            if vista == 'mes':
                key = v.Fecha.strftime('%Y-%m')
                label = v.Fecha.strftime('%B %Y')
            else:
                key = v.Fecha.strftime('%Y-%m-%d')
                label = v.Fecha.strftime('%d/%m/%Y')
        else:
            key = 'sin-fecha'
            label = 'Sin fecha'

        if key not in agrupado:
            agrupado[key] = {'label': label, 'ventas': [], 'total': 0.0,
                             'total_fisico': 0.0, 'total_linea': 0.0,
                             'count_fisico': 0, 'count_linea': 0}
        agrupado[key]['ventas'].append(v)
        total_venta = float(v.Total or 0)
        agrupado[key]['total'] += total_venta
        if v.EsEnLinea:
            agrupado[key]['total_linea'] += total_venta
            agrupado[key]['count_linea'] += 1
        else:
            agrupado[key]['total_fisico'] += total_venta
            agrupado[key]['count_fisico'] += 1

    # Totales generales
    total_general = sum(float(v.Total or 0) for v in ventas)
    total_fisico = sum(float(v.Total or 0) for v in ventas if not v.EsEnLinea)
    total_linea = sum(float(v.Total or 0) for v in ventas if v.EsEnLinea)

    return render_template(
        "venta/historial.html",
        agrupado=agrupado,
        vista=vista,
        tipo=tipo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        total_general=total_general,
        total_fisico=total_fisico,
        total_linea=total_linea,
        count_ventas=len(ventas),
    )


@ventas_bp.route("/ventas/detalle/<int:venta_id>")
@login_required
@roles_required("Administrador", "Vendedor", "Cajero")
def detalle(venta_id):
    """Ver detalles de una venta específica."""
    venta = Venta.query.get_or_404(venta_id)
    detalles = VentaDetalle.query.filter_by(VentaId=venta_id).all()

    # Enriquecer detalles con nombre del producto
    for d in detalles:
        producto = Producto.query.get(d.ProductoId)
        d.producto_nombre = producto.Nombre if producto else "Producto eliminado"

    return render_template("venta/detalle.html", venta=venta, detalles=detalles)
