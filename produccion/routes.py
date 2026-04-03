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


# ── Lista de solicitudes pendientes (vista cocinero) ────────────────────────
@produccion_bp.route("/produccion", methods=["GET"])
@login_required
@roles_required("Administrador", "Cocinero")
def index():
    """
    El cocinero ve todas las solicitudes Pendientes y En Produccion.
    """
    solicitudes = (
        SolicitudProduccion.query
        .filter(SolicitudProduccion.Estado.in_(["Pendiente", "En Produccion"]))
        .order_by(SolicitudProduccion.Fecha.desc())
        .all()
    )
    return render_template("produccion/index.html", solicitudes=solicitudes)


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
    Llama a sp_iniciar_produccion:
      - Valida stock
      - Crea OrdenProduccion
      - Descuenta materia prima
      - Cambia solicitud a 'En Produccion'
    """
    try:
        resultado = db.session.execute(
            text("CALL sp_iniciar_produccion(:sid, @res)"),
            {"sid": solicitud_id}
        )
        # Leer el OUT parameter
        out = db.session.execute(text("SELECT @res")).fetchone()[0]

        if out and out.startswith("OK:"):
            orden_id = out.split(":")[1]
            db.session.commit()
            flash(f"Producción iniciada. Orden #{orden_id} creada.", "success")
        else:
            db.session.rollback()
            flash(out or "Error desconocido al iniciar producción.", "danger")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al iniciar producción: {str(e)}", "danger")

    return redirect(url_for("produccion.index"))


# ── Finalizar producción (llama al SP) ──────────────────────────────────────
@produccion_bp.route("/produccion/finalizar/<int:orden_id>", methods=["POST"])
@login_required
@roles_required("Administrador", "Cocinero")
def finalizar(orden_id):
    """
    Llama a sp_finalizar_produccion:
      - Marca OrdenProduccion como Finalizado
      - Agrega MovimientoProducto (alta de producto terminado)
      - Marca la SolicitudProduccion como Realizada
    """
    try:
        db.session.execute(
            text("CALL sp_finalizar_produccion(:oid, @res)"),
            {"oid": orden_id}
        )
        out = db.session.execute(text("SELECT @res")).fetchone()[0]

        if out and out.startswith("OK:"):
            db.session.commit()
            flash(f"Orden #{orden_id} finalizada. Producto en disponibilidad.", "success")
        else:
            db.session.rollback()
            flash(out or "Error desconocido al finalizar.", "danger")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al finalizar orden: {str(e)}", "danger")

    return redirect(url_for("produccion.index"))



@produccion_bp.route("/produccion/detalle/<int:orden_id>")
@login_required
@roles_required("Administrador", "Cocinero")
def detalle(orden_id):
    orden = OrdenProduccion.query.get_or_404(orden_id)
    return render_template("produccion/detalle.html", orden=orden)