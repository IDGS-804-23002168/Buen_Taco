from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps
from flask import redirect, url_for, flash
from datetime import datetime, date
from sqlalchemy import func
from models import db, Venta, VentaDetalle, Producto, MovimientoMateriaPrima, MateriaPrima

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            roles_usuario = [ur.rol.Nombre for ur in current_user.roles if ur.Activo]
            if not any(r in roles_usuario for r in roles):
                flash('No tienes permiso para acceder a esta sección.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated
    return decorator


@dashboard_bp.route('/')
@login_required
@roles_required('Administrador')
def index():
    hoy   = date.today()
    ahora = datetime.now()

    # ── Ventas del día ──────────────────────────────────────────────
    ventas_hoy = db.session.query(
        func.coalesce(func.sum(Venta.Total), 0)
    ).filter(
        func.date(Venta.Fecha) == hoy
    ).scalar() or 0

    transacciones_hoy = Venta.query.filter(
        func.date(Venta.Fecha) == hoy
    ).count()

    # ── Ventas del mes ──────────────────────────────────────────────
    ventas_mes = db.session.query(
        func.coalesce(func.sum(Venta.Total), 0)
    ).filter(
        func.year(Venta.Fecha)  == ahora.year,
        func.month(Venta.Fecha) == ahora.month
    ).scalar() or 0

    # ── Productos más vendidos del día (top 5) ──────────────────────
    productos_top = db.session.query(
        Producto.Nombre,
        func.sum(VentaDetalle.Cantidad).label('total_vendido'),
        func.sum(VentaDetalle.Subtotal).label('total_monto')
    ).join(VentaDetalle, Producto.ProductoId == VentaDetalle.ProductoId)\
     .join(Venta, Venta.VentaId == VentaDetalle.VentaId)\
     .filter(func.date(Venta.Fecha) == hoy)\
     .group_by(Producto.ProductoId, Producto.Nombre)\
     .order_by(func.sum(VentaDetalle.Cantidad).desc())\
     .limit(5).all()

    # ── Ventas por hora del día (gráfica de barras) ─────────────────
    ventas_por_hora_raw = db.session.query(
        func.hour(Venta.Fecha).label('hora'),
        func.sum(Venta.Total).label('total')
    ).filter(
        func.date(Venta.Fecha) == hoy
    ).group_by(func.hour(Venta.Fecha)).all()

    horas_labels = [f"{h:02d}:00" for h in range(6, 23)]
    horas_data   = {row.hora: float(row.total) for row in ventas_por_hora_raw}
    ventas_horas = [horas_data.get(h, 0) for h in range(6, 23)]

    # ── Materias primas más consumidas del mes ──────────────────────
    materias_top = db.session.query(
        MateriaPrima.Nombre,
        func.abs(func.sum(MovimientoMateriaPrima.Cantidad)).label('total_consumido')
    ).join(MovimientoMateriaPrima, MateriaPrima.MateriaPrimaId == MovimientoMateriaPrima.MateriaPrimaId)\
     .filter(
        MovimientoMateriaPrima.TipoMovimiento == 'PRODUCCION',
        func.year(MovimientoMateriaPrima.Fecha)  == ahora.year,
        func.month(MovimientoMateriaPrima.Fecha) == ahora.month
     ).group_by(MateriaPrima.MateriaPrimaId, MateriaPrima.Nombre)\
      .order_by(func.abs(func.sum(MovimientoMateriaPrima.Cantidad)).desc())\
      .limit(5).all()

    # ── Alertas de stock bajo ───────────────────────────────────────
    # Stock actual por materia prima
    stocks = db.session.query(
        MateriaPrima.MateriaPrimaId,
        MateriaPrima.Nombre,
        func.coalesce(func.sum(MovimientoMateriaPrima.Cantidad), 0).label('stock')
    ).outerjoin(MovimientoMateriaPrima)\
     .filter(MateriaPrima.Activo == True)\
     .group_by(MateriaPrima.MateriaPrimaId, MateriaPrima.Nombre)\
     .all()

    alertas_stock = [s for s in stocks if float(s.stock) <= 0]

    return render_template('dashboard/index.html',
        ventas_hoy        = float(ventas_hoy),
        ventas_mes        = float(ventas_mes),
        transacciones_hoy = transacciones_hoy,
        productos_top     = productos_top,
        horas_labels      = horas_labels,
        ventas_horas      = ventas_horas,
        materias_top      = materias_top,
        alertas_stock     = alertas_stock,
        fecha_hoy         = hoy.strftime('%d/%m/%Y'),
        mes_actual        = ahora.strftime('%B %Y'),
    )