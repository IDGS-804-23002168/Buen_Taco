from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime
from decimal import Decimal # <--- IMPORTANTE: Herramienta para sumar valores exactos
import traceback # <--- Herramienta para imprimir los errores en la terminal

from models import db, Proveedor, MateriaPrima, Compra, CompraDetalle, MovimientoMateriaPrima
from . import compras

@compras.route("/compras/nueva", methods=['GET', 'POST'])
@login_required
def nueva_compra():
    if request.method == 'POST':
        try:
            # 1. Cachar los datos generales y convertirlos a Decimal
            proveedor_id = request.form.get('proveedor_id')
            total_compra = Decimal(request.form.get('total_compra'))

            # 2. Crear el "Ticket" general
            nueva_compra = Compra(
                ProveedorId=proveedor_id,
                Total=total_compra
            )
            db.session.add(nueva_compra)
            db.session.flush() # Para que nos dé el ID antes de guardar

            # 3. Cachar las listas del carrito oculto
            materias_ids = request.form.getlist('materia_id[]')
            cantidades = request.form.getlist('cantidad[]')
            precios_unitarios = request.form.getlist('precio_unitario[]')
            subtotales = request.form.getlist('subtotal[]')

            # 4. Recorrer el carrito producto por producto
            for i in range(len(materias_ids)):
                materia_id = int(materias_ids[i])
                
                # ¡AQUÍ ESTABA EL TRUCO! Usamos Decimal en vez de float
                cantidad = Decimal(cantidades[i])
                precio_u = Decimal(precios_unitarios[i])
                subtotal = Decimal(subtotales[i])

                # A) Guardar Detalle
                detalle = CompraDetalle(
                    CompraId=nueva_compra.CompraId,
                    MateriaPrimaId=materia_id,
                    Cantidad=cantidad,
                    PrecioUnitario=precio_u,
                    Subtotal=subtotal
                )
                db.session.add(detalle)

                # B) Registrar movimiento (Historial)
                movimiento = MovimientoMateriaPrima(
                    MateriaPrimaId=materia_id,
                    TipoMovimiento='COMPRA',
                    Cantidad=cantidad,
                    ReferenciaId=nueva_compra.CompraId
                )
                db.session.add(movimiento)

                # C) Sumar al Stock
                materia = MateriaPrima.query.get(materia_id)
                if materia:
                    # Nos aseguramos de que ambos sean Decimal para que no explote
                    stock_actual = Decimal(str(materia.stock if materia.stock else 0))
                    materia.stock = stock_actual + cantidad

            # 5. Sellar los cambios
            db.session.commit()
            flash('¡Compra registrada y stock actualizado con éxito!', 'success')
            return redirect(url_for('compras.nueva_compra'))

        except Exception as e:
            db.session.rollback()
            # ESTO MOSTRARÁ EL ERROR REAL EN TU TERMINAL NEGRA
            print("\n" + "="*50)
            print("ERROR AL GUARDAR LA COMPRA")
            traceback.print_exc() 
            print("="*50 + "\n")
            flash(f'Ocurrió un error al guardar: {str(e)}', 'danger')

    # GET: Cargar listas para la vista
    proveedores = Proveedor.query.filter_by(Activo=True).order_by(Proveedor.Nombre.asc()).all()
    materias = MateriaPrima.query.filter_by(Activo=True).order_by(MateriaPrima.Nombre.asc()).all()

    return render_template(
        'compras/nueva_compra.html',
        proveedores=proveedores,
        materias=materias
    )