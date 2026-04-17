from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from . import inventario_bp
from forms import MateriaPrimaForm, PresentacionForm  # <-- Importado correctamente desde la raíz
from models import db, MateriaPrima, UnidadMedida, UsuariosRoles, Rol, MateriaPrimaPresentacion

# --- DECORADOR PARA LOS ROLES ---
def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            ur = UsuariosRoles.query.filter_by(UsuarioId=current_user.UsuarioId, Activo=True).first()
            if ur:
                rol = Rol.query.get(ur.RolId)
                if rol and rol.Nombre in roles:
                    return fn(*args, **kwargs)
            
            flash("No tienes permiso para ver esta página.", "danger")
            return redirect(url_for('index'))
        return decorated_view
    return wrapper


# --- RUTA PRINCIPAL DEL INVENTARIO ---
@inventario_bp.route('/almacen/materias-primas', methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Encargado_Almacen', 'Cocinero')
def materias_primas():
    form = MateriaPrimaForm()
    
    # Llenamos el select con las unidades de medida de la base de datos
    form.unidad_id.choices = [(u.UnidadId, f"{u.Nombre} ({u.Abreviatura})") for u in UnidadMedida.query.all()]
    
    # Verificar si el usuario puede editar (Administrador o Encargado_Almacen)
    roles_usuario = [ur.rol.Nombre for ur in current_user.roles if ur.Activo]
    puede_editar = ('Administrador' in roles_usuario or 'Encargado_Almacen' in roles_usuario)

    if form.validate_on_submit() and request.method == 'POST':
        if not puede_editar:
            flash('No tienes permiso para agregar materias primas.', 'danger')
            return redirect(url_for('inventario.materias_primas'))
            
        nueva_materia = MateriaPrima(
            Nombre=form.nombre.data,
            UnidadBaseId=form.unidad_id.data,
            PorcentajeMerma=form.merma.data,
            Activo=True
        )
        db.session.add(nueva_materia)
        db.session.commit()
        flash('Materia prima agregada correctamente.', 'success')
        return redirect(url_for('inventario.materias_primas'))
    
    # Consultamos las materias para mostrarlas en la tabla
    lista_materias = MateriaPrima.query.filter_by(Activo=True).all()
    
    return render_template('inventario/materias_primas.html', form=form, materias=lista_materias, puede_editar=puede_editar)


# --- GESTIÓN DE PRESENTACIONES ---
@inventario_bp.route('/almacen/materias-primas/<int:materia_id>/presentaciones', methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Encargado_Almacen')
def presentaciones(materia_id):
    materia = MateriaPrima.query.get_or_404(materia_id)
    form = PresentacionForm()
    
    if form.validate_on_submit():
        nueva_pres = MateriaPrimaPresentacion(
            MateriaPrimaId=materia_id,
            Nombre=form.nombre.data,
            CantidadBase=form.cantidad_base.data
        )
        db.session.add(nueva_pres)
        db.session.commit()
        flash(f'Presentación "{form.nombre.data}" agregada para {materia.Nombre}.', 'success')
        return redirect(url_for('inventario.presentaciones', materia_id=materia_id))
    
    lista_presentaciones = MateriaPrimaPresentacion.query.filter_by(MateriaPrimaId=materia_id, Activo=True).all()
    
    return render_template('inventario/presentaciones.html', 
                         materia=materia, 
                         form=form, 
                         presentaciones=lista_presentaciones)


@inventario_bp.route('/almacen/presentaciones/eliminar/<int:pres_id>', methods=['POST'])
@login_required
@roles_required('Administrador', 'Encargado_Almacen')
def eliminar_presentacion(pres_id):
    pres = MateriaPrimaPresentacion.query.get_or_404(pres_id)
    materia_id = pres.MateriaPrimaId
    pres.Activo = False
    db.session.commit()
    flash('Presentación eliminada correctamente.', 'warning')
    return redirect(url_for('inventario.presentaciones', materia_id=materia_id))