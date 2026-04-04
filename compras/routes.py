from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from decimal import Decimal
import traceback

from models import db, Proveedor, MateriaPrima, Compra, CompraDetalle, MovimientoMateriaPrima
from . import compras


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


@compras.route("/compras", methods=['GET'])
@login_required
@roles_required('Administrador', 'Encargado_Almacen')
def index():
    """Vista principal de compras con historial filtrable."""
    # Filtros
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')
    proveedor_id = request.args.get('proveedor_id', '')

    query = Compra.query

    if fecha_desde:
        try:
            desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Compra.Fecha >= desde)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Compra.Fecha < hasta)
        except ValueError:
            pass

    if proveedor_id:
        try:
            query = query.filter(Compra.ProveedorId == int(proveedor_id))
        except ValueError:
            pass

    compras_list = query.order_by(Compra.Fecha.desc()).all()
    proveedores = Proveedor.query.filter_by(Activo=True).order_by(Proveedor.Nombre.asc()).all()

    # Calcular total filtrado
    total_filtrado = sum(float(c.Total or 0) for c in compras_list)

    return render_template(
        'compras/index.html',
        compras=compras_list,
        proveedores=proveedores,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        proveedor_id=proveedor_id,
        total_filtrado=total_filtrado,
    )


@compras.route("/compras/nueva", methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Encargado_Almacen')
def nueva_compra():
    if request.method == 'POST':
        try:
            proveedor_id = request.form.get('proveedor_id')
            total_compra = Decimal(request.form.get('total_compra'))

            nueva_compra = Compra(
                ProveedorId=proveedor_id,
                Total=total_compra
            )
            db.session.add(nueva_compra)
            db.session.flush()

            materias_ids = request.form.getlist('materia_id[]')
            cantidades = request.form.getlist('cantidad[]')
            precios_unitarios = request.form.getlist('precio_unitario[]')
            subtotales = request.form.getlist('subtotal[]')

            for i in range(len(materias_ids)):
                materia_id = int(materias_ids[i])
                cantidad = Decimal(cantidades[i])
                precio_u = Decimal(precios_unitarios[i])
                subtotal = Decimal(subtotales[i])

                detalle = CompraDetalle(
                    CompraId=nueva_compra.CompraId,
                    MateriaPrimaId=materia_id,
                    Cantidad=cantidad,
                    PrecioUnitario=precio_u,
                    Subtotal=subtotal
                )
                db.session.add(detalle)

                movimiento = MovimientoMateriaPrima(
                    MateriaPrimaId=materia_id,
                    TipoMovimiento='COMPRA',
                    Cantidad=cantidad,
                    ReferenciaId=nueva_compra.CompraId
                )
                db.session.add(movimiento)

                materia = MateriaPrima.query.get(materia_id)
                if materia:
                    stock_actual = Decimal(str(materia.stock if materia.stock else 0))
                    materia.stock = stock_actual + cantidad

            db.session.commit()
            flash('¡Compra registrada y stock actualizado con éxito!', 'success')
            return redirect(url_for('compras.index'))

        except Exception as e:
            db.session.rollback()
            print("\n" + "="*50)
            print("ERROR AL GUARDAR LA COMPRA")
            traceback.print_exc()
            print("="*50 + "\n")
            flash(f'Ocurrió un error al guardar: {str(e)}', 'danger')

    proveedores = Proveedor.query.filter_by(Activo=True).order_by(Proveedor.Nombre.asc()).all()
    materias = MateriaPrima.query.filter_by(Activo=True).order_by(MateriaPrima.Nombre.asc()).all()

    return render_template(
        'compras/nueva_compra.html',
        proveedores=proveedores,
        materias=materias
    )