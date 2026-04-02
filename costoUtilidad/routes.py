from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from functools import wraps
from flask import redirect, url_for, flash, Response
from decimal import Decimal
import csv
import io
from models import db, Producto, CategoriaProducto, Receta, CompraDetalle

costo_utilidad_bp = Blueprint('costo_utilidad', __name__, url_prefix='/finanzas/costo-utilidad')


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


def calcular_costo_lote(producto_id):
    """Reutiliza la lógica de Recetas para calcular costo con merma."""
    recetas     = Receta.query.filter_by(ProductoId=producto_id).all()
    costo_total = Decimal('0')
    for r in recetas:
        ultimo = (
            CompraDetalle.query
            .filter_by(MateriaPrimaId=r.MateriaPrimaId)
            .order_by(CompraDetalle.CompraDetalleId.desc())
            .first()
        )
        if not ultimo or not ultimo.PrecioUnitario:
            continue
        precio        = Decimal(str(ultimo.PrecioUnitario))
        cantidad      = Decimal(str(r.CantidadBase))
        merma         = Decimal(str(r.materia_prima.PorcentajeMerma or 0)) / Decimal('100')
        cantidad_real = cantidad * (1 + merma)
        costo_total  += cantidad_real * precio
    return round(costo_total, 2)


def obtener_datos_productos(solo_activos=True):
    """Obtiene todos los productos con su análisis financiero."""
    query = Producto.query
    if solo_activos:
        query = query.filter_by(Activo=True)
    productos = query.order_by(Producto.CategoriaId).all()

    datos = []
    for p in productos:
        costo  = calcular_costo_lote(p.ProductoId)
        precio = Decimal(str(p.Precio or 0))
        if precio > 0:
            margen_pesos      = precio - costo
            margen_porcentaje = round((margen_pesos / precio) * 100, 1)
        else:
            margen_pesos      = Decimal('0')
            margen_porcentaje = Decimal('0')

        # Semáforo
        if precio == 0:
            semaforo = 'sin-precio'
        elif margen_porcentaje < 0:
            semaforo = 'negativo'
        elif margen_porcentaje < 20:
            semaforo = 'bajo'
        else:
            semaforo = 'bueno'

        datos.append({
            'producto'          : p,
            'costo'             : costo,
            'margen_pesos'      : margen_pesos,
            'margen_porcentaje' : margen_porcentaje,
            'semaforo'          : semaforo,
        })

    return datos


@costo_utilidad_bp.route('/')
@login_required
@roles_required('Administrador')
def index():
    categorias  = CategoriaProducto.query.all()
    datos       = obtener_datos_productos(solo_activos=True)

    # Resumen general
    con_precio  = [d for d in datos if d['semaforo'] != 'sin-precio']
    mas_rentable   = max(con_precio, key=lambda d: d['margen_porcentaje']) if con_precio else None
    menos_rentable = min(con_precio, key=lambda d: d['margen_porcentaje']) if con_precio else None
    promedio_margen = round(
        sum(d['margen_porcentaje'] for d in con_precio) / len(con_precio), 1
    ) if con_precio else 0

    return render_template('costoUtilidad/index.html',
                           datos=datos,
                           categorias=categorias,
                           mas_rentable=mas_rentable,
                           menos_rentable=menos_rentable,
                           promedio_margen=promedio_margen)


@costo_utilidad_bp.route('/exportar-csv')
@login_required
@roles_required('Administrador')
def exportar_csv():
    datos = obtener_datos_productos(solo_activos=False)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Producto', 'Categoría', 'Precio Venta', 'Costo Producción',
                     'Margen ($)', 'Margen (%)', 'Estado'])

    for d in datos:
        writer.writerow([
            d['producto'].Nombre,
            d['producto'].categoria.Nombre,
            float(d['producto'].Precio or 0),
            float(d['costo']),
            float(d['margen_pesos']),
            float(d['margen_porcentaje']),
            'Activo' if d['producto'].Activo else 'Inactivo'
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=costo_utilidad.csv'}
    )