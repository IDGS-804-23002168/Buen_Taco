from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from sqlalchemy import or_
from datetime import datetime, timedelta

from models import db, Proveedor, Compra
from forms import ProveedorForm, BusquedaProveedorForm
from . import proveedores


# ────────────────────────────────────────────────────────────────
# LISTADO 
# ────────────────────────────────────────────────────────────────
@proveedores.route("/")
@login_required
def index():
    form_busqueda = BusquedaProveedorForm(request.args)

    query = Proveedor.query

    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(
            or_(
                Proveedor.Nombre.ilike(f'%{q}%'),
                Proveedor.RFC.ilike(f'%{q}%'),
                Proveedor.ContactoPrincipal.ilike(f'%{q}%'),
            )
        )

    estado = request.args.get('estado', 'todos')
    if estado == 'activo':
        query = query.filter(Proveedor.Activo.is_(True))
    elif estado == 'inactivo':
        query = query.filter(Proveedor.Activo.is_(False))

    categoria = request.args.get('categoria', '').strip()
    if categoria:
        query = query.filter(Proveedor.Categoria.ilike(f'%{categoria}%'))

    lista = query.order_by(Proveedor.Nombre.asc()).all()

    return render_template(
        'proveedores/index.html',
        proveedores=lista,
        form_busqueda=form_busqueda,
        total=len(lista),
    )

# ────────────────────────────────────────────────
# DETALLE PROVEEDOR
# ────────────────────────────────────────────────
@proveedores.route("/<int:id>/detalle")
@login_required
def detalle(id):
    proveedor = Proveedor.query.get_or_404(id)

    return render_template(
        'proveedores/detalles.html',
        proveedor=proveedor
    )

# ────────────────────────────────────────────────
# CREAR
# ────────────────────────────────────────────────
@proveedores.route("/nuevo", methods=['GET', 'POST'])
@login_required
def nuevo():
    form = ProveedorForm()

    if form.validate_on_submit():
        try:
            proveedor = Proveedor(
                Nombre=form.Nombre.data.strip(),
                RFC=form.RFC.data.strip().upper(),
                Categoria=form.Categoria.data.strip(),
                Direccion=form.Direccion.data.strip(),
                ContactoPrincipal=form.ContactoPrincipal.data.strip(),
                Telefono=form.Telefono.data.strip(),
                Email=form.Email.data.strip().lower(),
                Banco=form.Banco.data.strip(),
                CuentaBancaria=form.CuentaBancaria.data.strip(),
                CLABE=form.CLABE.data.strip(),
                Activo=form.Activo.data,
                Notas=form.Notas.data.strip(),
            )

            db.session.add(proveedor)
            db.session.commit()

            flash('Proveedor registrado correctamente.', 'success')
            return redirect(url_for('proveedores.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template(
        'proveedores/formulario.html',
        form=form,
        titulo='Nuevo Proveedor',
        modo='crear'
    )


# ────────────────────────────────────────────────
# EDITAR
# ────────────────────────────────────────────────
@proveedores.route("/<int:id>/editar", methods=['GET', 'POST'])
@login_required
def editar(id):
    proveedor = Proveedor.query.get_or_404(id)

    form = ProveedorForm(obj=proveedor)

    # 🔥 IMPORTANTE (esto arregla duplicados en edición)
    form.proveedor_id.data = str(proveedor.ProveedorId)

    if form.validate_on_submit():
        try:
            proveedor.Nombre = form.Nombre.data.strip()
            proveedor.RFC = form.RFC.data.strip().upper()
            proveedor.Categoria = form.Categoria.data.strip()
            proveedor.Direccion = form.Direccion.data.strip()
            proveedor.ContactoPrincipal = form.ContactoPrincipal.data.strip()
            proveedor.Telefono = form.Telefono.data.strip()
            proveedor.Email = form.Email.data.strip().lower()
            proveedor.Banco = form.Banco.data.strip()
            proveedor.CuentaBancaria = form.CuentaBancaria.data.strip()
            proveedor.CLABE = form.CLABE.data.strip()
            proveedor.Activo = form.Activo.data
            proveedor.Notas = form.Notas.data.strip()

            db.session.commit()

            flash('Proveedor actualizado correctamente.', 'success')
            return redirect(url_for('proveedores.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template(
        'proveedores/formulario.html',
        form=form,
        proveedor=proveedor,
        titulo='Editar Proveedor',
        modo='editar'
    )

# ────────────────────────────────────────────────────────────────
# ACTIVAR / DESACTIVAR 
# ────────────────────────────────────────────────────────────────
@proveedores.route("/<int:id>/toggle", methods=['POST'])
@login_required
def toggle_activo(id):
    proveedor = Proveedor.query.get_or_404(id)

    proveedor.Activo = not proveedor.Activo
    db.session.commit()

    estado = 'activado' if proveedor.Activo else 'desactivado'
    flash(f'Proveedor "{proveedor.Nombre}" {estado}.', 'info')

    return redirect(url_for('proveedores.index'))


# ────────────────────────────────────────────────────────────────
# HISTORIAL 
# ────────────────────────────────────────────────────────────────
@proveedores.route("/<int:id>/historial")
@login_required
def historial(id):
    proveedor = Proveedor.query.get_or_404(id)

    fecha_inicio = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')

    query = Compra.query.filter_by(ProveedorId=id)

    if fecha_inicio:
        try:
            fi = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            query = query.filter(Compra.Fecha >= fi)
        except ValueError:
            pass

    if fecha_fin:
        try:
            ff = datetime.strptime(fecha_fin, '%Y-%m-%d')
            query = query.filter(Compra.Fecha <= ff + timedelta(days=1))
        except ValueError:
            pass

    compras = query.order_by(Compra.Fecha.desc()).all()

    total_compras = sum(float(c.Total or 0) for c in compras)

    return render_template(
        'proveedores/historial.html',
        proveedor=proveedor,
        compras=compras,
        total_compras=total_compras,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )


# ────────────────────────────────────────────────────────────────
# DETALLE COMPRA
# ────────────────────────────────────────────────────────────────
@proveedores.route("/compra/<int:compra_id>")
@login_required
def detalle_compra(compra_id):
    compra = Compra.query.get_or_404(compra_id)

    return render_template(
        'proveedores/detalle_compra.html',
        compra=compra
    )


# ────────────────────────────────────────────────────────────────
# API JSON (autocompletado)
# ────────────────────────────────────────────────────────────────
@proveedores.route("/api/buscar")
@login_required
def api_buscar():
    q = request.args.get('q', '').strip()
    solo_activos = request.args.get('activos', 'true').lower() == 'true'

    query = Proveedor.query

    if solo_activos:
        query = query.filter(Proveedor.Activo.is_(True))

    if q:
        query = query.filter(
            or_(
                Proveedor.Nombre.ilike(f'%{q}%'),
                Proveedor.RFC.ilike(f'%{q}%'),
            )
        )

    resultados = query.limit(20).all()

    return jsonify([
        {
            'id': p.ProveedorId,
            'nombre': p.Nombre,
            'rfc': p.RFC,
            'telefono': p.Telefono,
            'contacto': p.ContactoPrincipal,
            'activo': p.Activo,
        }
        for p in resultados
    ])