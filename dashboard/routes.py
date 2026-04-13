from flask import Blueprint, render_template
from flask_login import login_required, current_user
from functools import wraps
from flask import redirect, url_for, flash
from datetime import datetime, date, timedelta
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
    func.coalesce(func.sum(VentaDetalle.Cantidad), 0).label('total_vendido'),
    func.coalesce(func.sum(VentaDetalle.Subtotal), 0).label('total_monto')  # ← aquí
).join(VentaDetalle, Producto.ProductoId == VentaDetalle.ProductoId)\
 .join(Venta, Venta.VentaId == VentaDetalle.VentaId)\
 .filter(func.date(Venta.Fecha) == hoy)\
 .group_by(Producto.ProductoId, Producto.Nombre)\
 .order_by(func.sum(VentaDetalle.Cantidad).desc())\
 .limit(5).all()

    # ── Ventas de los últimos 7 días (gráfica de barras) ──────────────
    siete_dias_atras = hoy - timedelta(days=6)
    
    ventas_por_dia_raw = db.session.query(
        func.date(Venta.Fecha).label('fecha'),
        func.sum(Venta.Total).label('total')
    ).filter(
        func.date(Venta.Fecha) >= siete_dias_atras,
        func.date(Venta.Fecha) <= hoy
    ).group_by(func.date(Venta.Fecha)).all()

    # Generar todos los días del rango para que no haya huecos
    dias_label = []
    ventas_data = []
    datos_dict = {row.fecha.strftime('%Y-%m-%d') if isinstance(row.fecha, date) else row.fecha: float(row.total) for row in ventas_por_dia_raw}

    for i in range(7):
        d = siete_dias_atras + timedelta(days=i)
        d_str = d.strftime('%Y-%m-%d')
        # Etiqueta amigable (ej: "Lun 01")
        dias_label.append(d.strftime('%a %d'))
        ventas_data.append(datos_dict.get(d_str, 0))

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
        dias_label        = dias_label,
        ventas_data       = ventas_data,
        materias_top      = materias_top,
        alertas_stock     = alertas_stock,
        fecha_hoy         = hoy.strftime('%d/%m/%Y'),
        mes_actual        = ahora.strftime('%B %Y'),
    )