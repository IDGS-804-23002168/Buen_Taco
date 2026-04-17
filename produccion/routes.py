from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import text

from . import produccion_bp
from models import db, SolicitudProduccion, OrdenProduccion, Producto


# ── decorador de roles ──────────────────────────────────────────────────────
def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            roles_usuario = [ur.rol.Nombre for ur in current_user.roles if ur.Activo]
            if any(r in roles_usuario for r in roles):
                return fn(*args, **kwargs)
            flash("No tienes permiso para ver esta página.", "danger")
            return redirect(url_for("index"))
        return decorated_view
    return wrapper


# ── Lista de solicitudes pendientes / en producción (vista cocinero) ────────
@produccion_bp.route("/produccion", methods=["GET"])
@login_required
@roles_required("Administrador", "Cocinero")
def index():
    """
    El cocinero ve todas las solicitudes Pendientes y En Produccion,
    ahora con sus detalles (múltiples productos por solicitud).
    """
    solicitudes = (
        SolicitudProduccion.query
        .filter(SolicitudProduccion.Estado.in_(["Pendiente", "En Produccion"]))
        .order_by(SolicitudProduccion.Fecha.desc())
        .all()
    )
    
    from models import Pedido
    
    # Obtener los PedidoId únicos de las órdenes activas en línea
    pedidos_linea_ids = [row.PedidoId for row in db.session.query(OrdenProduccion.PedidoId).filter(
        OrdenProduccion.PedidoId.isnot(None),
        OrdenProduccion.Estado.in_(["Pendiente", "En Produccion"])
    ).distinct().all()]
    
    pedidos_linea = []
    if pedidos_linea_ids:
        pedidos_linea = Pedido.query.filter(Pedido.PedidoId.in_(pedidos_linea_ids)).order_by(Pedido.Fecha.desc()).all()
    
    return render_template("produccion/index.html", solicitudes=solicitudes, pedidos_linea=pedidos_linea)


# ── Rechazar solicitud ───────────────────────────────────────────────────────
@produccion_bp.route("/produccion/rechazar/<int:solicitud_id>", methods=["POST"])
@login_required
@roles_required("Administrador", "Cocinero")
def rechazar(solicitud_id):
    solicitud = SolicitudProduccion.query.get_or_404(solicitud_id)

    if solicitud.Estado != "Pendiente":
        flash("Solo se pueden rechazar solicitudes en estado Pendiente.", "warning")
        return redirect(url_for("produccion.index"))

    solicitud.Estado = "Rechazada"
    db.session.commit()
    flash(f"Solicitud #{solicitud_id} rechazada.", "warning")
    return redirect(url_for("produccion.index"))


# ── Iniciar producción (llama al SP) ────────────────────────────────────────
@produccion_bp.route("/produccion/iniciar/<int:solicitud_id>", methods=["POST"])
@login_required
@roles_required("Administrador", "Cocinero")
def iniciar(solicitud_id):
    """
    Llama a sp_iniciar_produccion que ahora:
      - Itera sobre SolicitudDetalle
      - Valida stock de materias primas para cada producto
      - Crea una OrdenProduccion por cada producto
      - Descuenta materia prima
      - Cambia solicitud a 'En Produccion'
    """
    try:
        db.session.execute(
            text("CALL sp_iniciar_produccion(:sid, @res)"),
            {"sid": solicitud_id}
        )
        out = db.session.execute(text("SELECT @res")).fetchone()[0]

        if out and out.startswith("OK:"):
            db.session.commit()
            flash(f"Producción iniciada para solicitud #{solicitud_id}.", "success")
        else:
            db.session.rollback()
            flash(out or "Error desconocido al iniciar producción.", "danger")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al iniciar producción: {str(e)}", "danger")

    return redirect(url_for("produccion.index"))


# ── Finalizar producción (llama al SP) ──────────────────────────────────────
@produccion_bp.route("/produccion/finalizar/<int:solicitud_id>", methods=["POST"])
@login_required
@roles_required("Administrador", "Cocinero")
def finalizar(solicitud_id):
    """
    Llama a sp_finalizar_produccion que ahora:
      - Recibe SolicitudId
      - Finaliza TODAS las OrdeneProduccion vinculadas
      - Agrega MovimientoProducto para cada producto
      - Marca la SolicitudProduccion como 'Realizada'
    """
    try:
        db.session.execute(
            text("CALL sp_finalizar_produccion(:sid, @res)"),
            {"sid": solicitud_id}
        )
        out = db.session.execute(text("SELECT @res")).fetchone()[0]

        if out and out.startswith("OK:"):
            db.session.commit()
            flash(f"Solicitud #{solicitud_id} finalizada. Productos disponibles para venta.", "success")
        else:
            db.session.rollback()
            flash(out or "Error desconocido al finalizar.", "danger")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al finalizar producción: {str(e)}", "danger")

    return redirect(url_for("produccion.index"))


# ── Detalle de solicitud ────────────────────────────────────────────────────
@produccion_bp.route("/produccion/detalle/<int:solicitud_id>")
@login_required
@roles_required("Administrador", "Cocinero")
def detalle(solicitud_id):
    solicitud = SolicitudProduccion.query.get_or_404(solicitud_id)
    return render_template("produccion/detalle.html", solicitud=solicitud)


# ── Historial de producción ─────────────────────────────────────────────────
@produccion_bp.route("/produccion/historial")
@login_required
@roles_required("Administrador", "Cocinero")
def historial():
    """Historial completo de solicitudes y órdenes (todos los estados)."""
    solicitudes = (
        SolicitudProduccion.query
        .order_by(SolicitudProduccion.Fecha.desc())
        .all()
    )
    return render_template("produccion/historial.html", solicitudes=solicitudes)


# ── Finalizar Pedido Completo (Ventas en línea) ──────────────────────────────
@produccion_bp.route("/produccion/finalizar_pedido_linea/<int:pedido_id>", methods=["POST"])
@login_required
@roles_required("Administrador", "Cocinero")
def finalizar_pedido_linea(pedido_id):
    try:
        from datetime import datetime
        ordenes = OrdenProduccion.query.filter_by(PedidoId=pedido_id).filter(OrdenProduccion.Estado.in_(["Pendiente", "En Produccion"])).all()
        
        for orden in ordenes:
            orden.Estado = 'Finalizada'
            orden.FechaFin = datetime.utcnow()
        
        db.session.commit()
        flash(f"Pedido en línea #{pedido_id} terminado y listo para entrega.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al finalizar el pedido en línea: {str(e)}", "danger")

    return redirect(url_for("produccion.index"))

# ── Detalle Pedido Línea ───────────────────────────────────────────────────
@produccion_bp.route("/produccion/detalle_pedido_linea/<int:pedido_id>")
@login_required
@roles_required("Administrador", "Cocinero")
def detalle_pedido_linea(pedido_id):
    from models import Pedido
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template("produccion/detalle_pedido.html", pedido=pedido)