import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
from decimal import Decimal
from werkzeug.utils import secure_filename
from models import db, Receta, Producto, MateriaPrima, CategoriaProducto, CompraDetalle
from recetas.forms import FormAgregarIngrediente, FormEditarIngrediente

recetas_bp = Blueprint('recetas', __name__, url_prefix='/recetas')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

def _guardar_imagen(archivo):
    """Guarda la imagen en static/img/productos/ y devuelve la ruta relativa."""
    if archivo and archivo.filename:
        filename = secure_filename(archivo.filename)
        # Agregar timestamp para evitar colisiones
        import time
        nombre, ext = os.path.splitext(filename)
        filename = f"{nombre}_{int(time.time())}{ext}"
        carpeta = os.path.join(current_app.root_path, 'static', 'img', 'productos')
        os.makedirs(carpeta, exist_ok=True)
        archivo.save(os.path.join(carpeta, filename))
        return f"img/productos/{filename}"
    return None


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
    """Costo del lote considerando merma. Usa el precio más reciente de cada materia prima."""
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


def calcular_unidades_producibles(producto_id):
    """Calcula cuántas unidades se pueden producir con el stock actual."""
    from models import MovimientoMateriaPrima
    from sqlalchemy import func
    recetas = Receta.query.filter_by(ProductoId=producto_id).all()
    if not recetas:
        return 0
    minimo = None
    for r in recetas:
        stock = db.session.query(
            func.coalesce(func.sum(MovimientoMateriaPrima.Cantidad), 0)
        ).filter_by(MateriaPrimaId=r.MateriaPrimaId).scalar() or 0
        cantidad_real = float(r.CantidadBase) * (1 + float(r.materia_prima.PorcentajeMerma or 0) / 100)
        if cantidad_real <= 0:
            continue
        unidades = int(float(stock) / cantidad_real)
        if minimo is None or unidades < minimo:
            minimo = unidades
    return minimo if minimo is not None else 0


@recetas_bp.route('/')
@login_required
@roles_required('Administrador', 'Cocinero')
def index():
    productos  = Producto.query.all()
    categorias = CategoriaProducto.query.all()
    costos     = {p.ProductoId: calcular_costo_lote(p.ProductoId) for p in productos}
    return render_template('recetas/index.html', productos=productos,
                           costos=costos, categorias=categorias)


@recetas_bp.route('/ver/<int:producto_id>')
@login_required
@roles_required('Administrador', 'Cocinero')
def ver(producto_id):
    producto             = Producto.query.get_or_404(producto_id)
    recetas              = Receta.query.filter_by(ProductoId=producto_id).all()
    costo                = calcular_costo_lote(producto_id)
    unidades_producibles = calcular_unidades_producibles(producto_id)
    return render_template('recetas/ver.html', producto=producto,
                           recetas=recetas, costo=costo,
                           unidades_producibles=unidades_producibles)





@recetas_bp.route('/agregar/<int:producto_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Cocinero')
def agregar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    materias = MateriaPrima.query.filter_by(Activo=True).all()
    form     = FormAgregarIngrediente()
    form.materia_prima_id.choices = [
        (m.MateriaPrimaId, f"{m.Nombre} ({m.unidad.Abreviatura})") for m in materias
    ]

    if request.method == 'POST':
        if form.validate_on_submit():
            existe = Receta.query.filter_by(
                ProductoId=producto_id,
                MateriaPrimaId=form.materia_prima_id.data
            ).first()
            if existe:
                flash('Esa materia prima ya está en la receta.', 'warning')
            else:
                try:
                    nueva = Receta(
                        ProductoId=producto_id,
                        MateriaPrimaId=form.materia_prima_id.data,
                        CantidadBase=form.cantidad_base.data
                    )
                    db.session.add(nueva)
                    db.session.commit()
                    flash('Ingrediente agregado correctamente.', 'success')
                    return redirect(url_for('recetas.ver', producto_id=producto_id))
                except Exception:
                    db.session.rollback()
                    flash('Error al guardar. Intenta de nuevo.', 'danger')

    return render_template('recetas/form.html', form=form, producto=producto)


@recetas_bp.route('/editar/<int:producto_id>/<int:materia_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Cocinero')
def editar(producto_id, materia_id):
    receta = Receta.query.get_or_404((producto_id, materia_id))
    form   = FormEditarIngrediente()

    if request.method == 'GET':
        form.cantidad_base.data = float(receta.CantidadBase)

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                receta.CantidadBase = form.cantidad_base.data
                db.session.commit()
                flash('Ingrediente actualizado.', 'success')
                return redirect(url_for('recetas.ver', producto_id=producto_id))
            except Exception:
                db.session.rollback()
                flash('Error al actualizar.', 'danger')

    return render_template('recetas/form.html', form=form,
                           producto=receta.producto, receta=receta)


@recetas_bp.route('/eliminar/<int:producto_id>/<int:materia_id>', methods=['POST'])
@login_required
@roles_required('Administrador', 'Cocinero')
def eliminar(producto_id, materia_id):
    receta = Receta.query.get_or_404((producto_id, materia_id))
    try:
        db.session.delete(receta)
        db.session.commit()
        flash('Ingrediente eliminado de la receta.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error al eliminar.', 'danger')
    return redirect(url_for('recetas.ver', producto_id=producto_id))