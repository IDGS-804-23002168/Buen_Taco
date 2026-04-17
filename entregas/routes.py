from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps

from . import entregas_bp
from models import db, Pedido, Direccion

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


@entregas_bp.route("/entregas", methods=["GET"])
@login_required
@roles_required("Administrador", "Vendedor")
def index():
    # Recuperamos los pedidos pagados
    pedidos = Pedido.query.filter_by(Estado='Pagado').order_by(Pedido.Fecha.asc()).all()

    # Dividir en Domicilio y Recoger
    para_recoger = []
    a_domicilio = []

    for p in pedidos:
        # Se asume que las ventas en línea creadas en 'venta_linea' tienen este formato de observaciones
        if p.DireccionId is None:
            para_recoger.append(p)
        else:
            p.dir_entrega = Direccion.query.get(p.DireccionId)
            a_domicilio.append(p)

    return render_template(
        "entregas/index.html",
        para_recoger=para_recoger,
        a_domicilio=a_domicilio
    )

@entregas_bp.route("/entregas/historial", methods=["GET"])
@login_required
@roles_required("Administrador", "Vendedor")
def historial():
    # Recuperamos los pedidos ya entregados
    pedidos_entregados = Pedido.query.filter_by(Estado='Entregado').order_by(Pedido.Fecha.desc()).all()

    for p in pedidos_entregados:
        if p.DireccionId is not None:
            p.dir_entrega = Direccion.query.get(p.DireccionId)
            
    return render_template("entregas/historial.html", pedidos=pedidos_entregados)


@entregas_bp.route("/entregas/marcar_entregado/<int:pedido_id>", methods=["POST"])
@login_required
@roles_required("Administrador", "Vendedor")
def marcar_entregado(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    
    if pedido.Estado == 'Pagado':
        pedido.Estado = 'Entregado'
        db.session.commit()
        flash(f"Pedido #{pedido.PedidoId} marcado como Entregado exitosamente.", "success")
    else:
        flash("El pedido no se encuentra en un estado válido para entregar.", "warning")

    return redirect(url_for("entregas.index"))
