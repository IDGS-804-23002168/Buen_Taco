from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
from models import db, Producto, CategoriaProducto
from productos.forms import FormProducto

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

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

@productos_bp.route('/')
@login_required
@roles_required('Administrador', 'Cocinero')
def index():
    productos = Producto.query.all()
    categorias = CategoriaProducto.query.all()
    form = FormProducto()
    form.categoria_id.choices = [(c.CategoriaId, c.Nombre) for c in categorias]
    return render_template('productos/index.html', productos=productos, categorias=categorias, form=form, abrir_modal=False)

@productos_bp.route('/nuevo-producto', methods=['POST'])
@login_required
@roles_required('Administrador', 'Cocinero')
def nuevo_producto():
    categorias = CategoriaProducto.query.all()
    form = FormProducto()
    form.categoria_id.choices = [(c.CategoriaId, c.Nombre) for c in categorias]

    if form.validate_on_submit():
        try:
            nombre_producto = form.nombre.data.strip()
            p = Producto(
                Nombre=nombre_producto,
                Descripcion=form.descripcion.data.strip() if form.descripcion.data else '',
                CategoriaId=form.categoria_id.data,
                Precio=form.precio.data or 0,
                Activo=True,
                imagen_url=None
            )
            db.session.add(p)
            db.session.flush() # Para obtener el ProductoId

            # Guardar imagen si se subió
            if form.imagen.data and form.imagen.data.filename:
                import os
                from werkzeug.utils import secure_filename
                archivo = form.imagen.data
                filename = secure_filename(archivo.filename)
                _, ext = os.path.splitext(filename)
                
                # Formato: {id}_{nombre}{extension}
                nombre_seguro = secure_filename(nombre_producto.replace(' ', '_').lower())
                nuevo_nombre = f"{p.ProductoId}_{nombre_seguro}{ext}"
                
                carpeta = os.path.join(current_app.root_path, 'static', 'img', 'productos')
                os.makedirs(carpeta, exist_ok=True)
                archivo.save(os.path.join(carpeta, nuevo_nombre))
                
                p.imagen_url = f"img/productos/{nuevo_nombre}"
            
            db.session.commit()
            flash('Producto creado correctamente.', 'success')
            return redirect(url_for('productos.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el producto: {str(e)}', 'danger')

    # Si hay errores vuelve al index re-abriendo el modal
    productos = Producto.query.all()
    return render_template('productos/index.html', productos=productos, categorias=categorias, form=form, abrir_modal=True)

@productos_bp.route('/editar-producto/<int:producto_id>', methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Cocinero')
def editar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    categorias = CategoriaProducto.query.all()
    form = FormProducto()
    form.categoria_id.choices = [(c.CategoriaId, c.Nombre) for c in categorias]

    if request.method == 'GET':
        form.nombre.data = producto.Nombre
        form.descripcion.data = producto.Descripcion
        form.categoria_id.data = producto.CategoriaId
        form.precio.data = producto.Precio

    if form.validate_on_submit():
        try:
            nombre_producto = form.nombre.data.strip()
            producto.Nombre = nombre_producto
            producto.Descripcion = form.descripcion.data.strip() if form.descripcion.data else ''
            producto.CategoriaId = form.categoria_id.data
            producto.Precio = form.precio.data or 0

            # Update image if uploaded
            if form.imagen.data and form.imagen.data.filename:
                import os
                from werkzeug.utils import secure_filename
                archivo = form.imagen.data
                filename = secure_filename(archivo.filename)
                _, ext = os.path.splitext(filename)
                
                nombre_seguro = secure_filename(nombre_producto.replace(' ', '_').lower())
                nuevo_nombre = f"{producto.ProductoId}_{nombre_seguro}{ext}"
                
                carpeta = os.path.join(current_app.root_path, 'static', 'img', 'productos')
                os.makedirs(carpeta, exist_ok=True)
                
                # Delete old image if it exists to keep directory clean
                if producto.imagen_url:
                    vieja_ruta = os.path.join(current_app.root_path, 'static', producto.imagen_url)
                    if os.path.exists(vieja_ruta):
                        try:
                            os.remove(vieja_ruta)
                        except Exception:
                            pass
                
                archivo.save(os.path.join(carpeta, nuevo_nombre))
                producto.imagen_url = f"img/productos/{nuevo_nombre}"

            db.session.commit()
            flash('Producto actualizado correctamente.', 'success')
            return redirect(url_for('productos.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el producto: {str(e)}', 'danger')

    return render_template('productos/editar_producto.html', form=form, producto=producto)
