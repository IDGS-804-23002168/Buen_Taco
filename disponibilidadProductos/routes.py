from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from . import productos_bp
from models import Producto, CategoriaProducto

# Formularios (simples para filtro)
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField

class FiltroCategoriaForm(FlaskForm):
    categoria = SelectField('Categoría', choices=[])
    buscar = StringField('Buscar')
    submit = SubmitField('Filtrar')

@productos_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # Formularios
    filtro_form = FiltroCategoriaForm(request.form if request.method == 'POST' else None)

    # Filtrado inicial
    categoria_sel = request.args.get('categoria', 'Todo')
    busqueda = request.args.get('busqueda', '').strip()

    # Configurar choices dinámicamente
    filtro_form.categoria.choices = [('Todo','Todas')] + [(c.Nombre,c.Nombre) for c in CategoriaProducto.query.order_by(CategoriaProducto.Nombre).all()]

    # POST: si se envía formulario de filtro
    if request.method == 'POST' and filtro_form.validate():
        categoria_sel = filtro_form.categoria.data
        busqueda = filtro_form.buscar.data or ''
        return redirect(url_for('productos.index', categoria=categoria_sel, busqueda=busqueda))

    # Query de productos
    query = Producto.query.filter_by(Activo=True)
    if categoria_sel != 'Todo':
        cat = CategoriaProducto.query.filter_by(Nombre=categoria_sel).first()
        if cat:
            query = query.filter_by(CategoriaId=cat.CategoriaId)
    if busqueda:
        query = query.filter(Producto.Nombre.ilike(f'%{busqueda}%'))

    productos = query.order_by(Producto.Nombre).all()
    categorias = CategoriaProducto.query.order_by(CategoriaProducto.Nombre).all()

    return render_template(
        'disponibilidadProductos/index.html',
        productos=productos,
        categorias=categorias,
        categoria_sel=categoria_sel,
        busqueda=busqueda,
        filtro_form=filtro_form
    )