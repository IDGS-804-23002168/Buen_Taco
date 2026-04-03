from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func
from datetime import datetime  # <-- Importamos esto para generar la fecha y hora exacta
from . import ventas_bp

# Asegúrate de importar los nombres exactos de tus modelos: Ventas y VentaDetalle
from models import (
    db,
    Producto,
    CategoriaProducto,
    MovimientoProducto,
    Venta,
    VentaDetalle,
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
        # El método de pago lo recibimos del HTML, pero como no tienes columna para guardarlo,
        # por ahora solo lo ignoraremos en la base de datos.

        hubo_ventas = False
        total_venta = 0.0
        items_a_vender = []

        # 1. Leer el carrito y validar existencias antes de cobrar
        for key, value in request.form.items():
            if key.startswith("prod_") and int(value) > 0:
                producto_id = int(key.split("_")[1])
                cantidad = int(value)
                producto = Producto.query.get(producto_id)

                stock_actual = (
                    db.session.query(
                        func.coalesce(func.sum(MovimientoProducto.Cantidad), 0)
                    )
                    .filter_by(ProductoId=producto_id)
                    .scalar()
                )

                if stock_actual < cantidad:
                    flash(
                        f"Error: Stock insuficiente para {producto.Nombre}. Solo quedan {stock_actual}.",
                        "danger",
                    )
                    return redirect(url_for("ventas.index"))

                precio = float(producto.Precio) if producto.Precio else 0.0
                subtotal = precio * cantidad
                total_venta += subtotal

                items_a_vender.append(
                    {
                        "producto_id": producto_id,
                        "cantidad": cantidad,
                        "precio": precio,
                        "subtotal": subtotal,
                    }
                )
                hubo_ventas = True

        if not hubo_ventas:
            flash("El carrito está vacío.", "warning")
            return redirect(url_for("ventas.index"))

        # 2. Procesar la transacción adaptada a TUS tablas
        try:
            # A) Crear la cabecera en la tabla 'Ventas'
            nueva_venta = Venta(
                EsEnLinea=0,  # Es venta de mostrador, así que es falso (0)
                Fecha=datetime.now(),  # Mandamos la hora exacta
                Total=total_venta,
                # ClienteId y PedidoId quedan como NULL temporalmente
            )
            db.session.add(nueva_venta)
            db.session.flush()  # Guardamos para que MySQL nos devuelva el VentaId autoincrementable

            # B) Crear los detalles en la tabla 'VentaDetalle' y descontar Inventario
            for item in items_a_vender:
                detalle = VentaDetalle(
                    VentaId=nueva_venta.VentaId,
                    ProductoId=item["producto_id"],
                    Cantidad=item["cantidad"],
                    PrecioUnitario=item["precio"],
                    Subtotal=item["subtotal"],
                )
                db.session.add(detalle)

                # Descontar de Disponibilidad
                mov_salida = MovimientoProducto(
                    ProductoId=item["producto_id"],
                    TipoMovimiento="Salida por Venta",
                    Cantidad=-item["cantidad"],  # Negativo para restar
                )
                db.session.add(mov_salida)

            db.session.commit()
            flash(f"¡Venta cobrada con éxito! Total: ${total_venta:.2f}", "success")

        except Exception as e:
            db.session.rollback()
            flash("Error de base de datos al procesar la venta.", "danger")
            print(
                f"Error técnico: {e}"
            )  # Así veremos el problema en la terminal si algo más falla

        return redirect(url_for("ventas.index"))

    # GET: Mostrar la interfaz de ventas
    productos = Producto.query.filter_by(Activo=True).all()
    categorias = CategoriaProducto.query.all()

    productos_disponibles = []
    for p in productos:
        stock = (
            db.session.query(func.coalesce(func.sum(MovimientoProducto.Cantidad), 0))
            .filter_by(ProductoId=p.ProductoId)
            .scalar()
        )

        if stock > 0:
            p.stock_actual = int(stock)
            productos_disponibles.append(p)

    return render_template(
        "venta/index.html", productos=productos_disponibles, categorias=categorias
    )
