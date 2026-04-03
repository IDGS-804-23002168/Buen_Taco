from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from . import solicitudes_bp
from models import db, Producto, SolicitudProduccion, CategoriaProducto


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


@solicitudes_bp.route("/solicitudes", methods=["GET", "POST"])
@login_required
@roles_required("Administrador", "Vendedor")  # Ajusta los roles según necesites
def index():
    if request.method == "POST":
        hubo_pedidos = False
        try:
            # Iteramos sobre todos los campos enviados desde el formulario (carrito)
            for key, value in request.form.items():
                if key.startswith("prod_"):
                    producto_id = int(key.split("_")[1])
                    cantidad = int(value)

                    # Solo guardamos si el usuario pidió 1 o más de este producto
                    if cantidad > 0:
                        nueva_solicitud = SolicitudProduccion(
                            ProductoId=producto_id,
                            CantidadSolicitada=cantidad,
                            Estado="Pendiente",
                        )
                        db.session.add(nueva_solicitud)
                        hubo_pedidos = True

            if hubo_pedidos:
                db.session.commit()
                flash("¡Solicitud enviada a la cocina exitosamente!", "success")
            else:
                flash(
                    "El carrito estaba vacío. Selecciona al menos un producto.",
                    "warning",
                )

        except Exception as e:
            db.session.rollback()
            flash("Error al procesar la solicitud.", "danger")

        return redirect(url_for("solicitudes.index"))

    productos = Producto.query.filter_by(Activo=True).all()
    categorias = CategoriaProducto.query.all()
    return render_template(
        "solicitudProduccion/index.html", productos=productos, categorias=categorias
    )
