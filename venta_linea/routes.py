from flask import (
    render_template, redirect, url_for,
    flash, session, request
)
from flask_login import login_required, current_user
from functools import wraps
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from . import venta_linea_bp
from models import (
    db, Producto, CategoriaProducto, MovimientoProducto,
    Pedido, PedidoDetalle, Venta, VentaDetalle, Pago, Direccion,
    OrdenProduccion, MateriaPrima, Receta, MovimientoMateriaPrima
)
from utils.stock_util import obtener_disponibilidad_producto
from forms import (
    AgregarProductoForm, EliminarItemForm,
    ActualizarCantidadForm, DireccionForm, PagoForm, FiltroCategoriaForm
)

CARRITO_KEY = 'carrito_linea'
IVA_TASA    = Decimal('0.16')

# --------------------- Helpers ---------------------

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

def _get_carrito():
    return session.get(CARRITO_KEY, [])

def _save_carrito(carrito):
    session[CARRITO_KEY] = carrito
    session.modified = True

def _totales(carrito, entrega=None):
    subtotal = sum(Decimal(str(i['precio_unitario'])) * i['cantidad'] for i in carrito)

    envio = Decimal('0.00')

    if entrega and entrega.get('tipo') == 'domicilio':
        envio = Decimal('30.00')

    iva = ((subtotal + envio) * IVA_TASA).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = subtotal + envio + iva

    return subtotal, envio, iva, total



# --------------------- RUTA PRINCIPAL ---------------------

@venta_linea_bp.route('/', methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Usuario')
def index():
    filtro_form   = FiltroCategoriaForm(request.form if request.method == 'POST' else None)
    agregar_form  = AgregarProductoForm()
    eliminar_form = EliminarItemForm()
    actualizar_form = ActualizarCantidadForm()

    categoria_sel = request.args.get('categoria', 'Todo')
    busqueda      = request.args.get('busqueda', '').strip()

    # ---------------- POST ----------------
    if request.method == 'POST':

        # 🟢 AGREGAR PRODUCTO
        if 'add-submit' in request.form:
            agregar_form = AgregarProductoForm(request.form)

            if agregar_form.validate():
                pid = int(agregar_form.producto_id.data)
                cantidad = agregar_form.cantidad.data
                notas = agregar_form.notas.data or ''

                producto = Producto.query.filter_by(ProductoId=pid, Activo=True).first()

                if not producto:
                    flash('Producto no existe.', 'danger')
                    return redirect(url_for('venta_linea.index'))

                # --- VALIDACIÓN DE STOCK ---
                disponible = obtener_disponibilidad_producto(pid)
                if cantidad > disponible:
                    flash(f'No hay suficiente stock disponible para {producto.Nombre}. Máximo: {disponible}', 'warning')
                    return redirect(url_for('venta_linea.index'))
                # ---------------------------

                carrito = _get_carrito()
                existe = next(
                (i for i in carrito if i['producto_id'] == pid and i['notas'] == notas),
                None
                )        

                if existe:
                    # Validar también la suma si ya existe en el carrito
                    if existe['cantidad'] + cantidad > disponible:
                        flash(f'Ya tienes este producto en el carrito. El total supera el stock disponible ({disponible}).', 'warning')
                        return redirect(url_for('venta_linea.index'))
                    existe['cantidad'] += cantidad
                else:
                    carrito.append({
                    'producto_id': pid,
                    'nombre': producto.Nombre,
                    'precio_unitario': float(producto.Precio),
                    'cantidad': cantidad,
                    'notas': notas
                })
                    
                _save_carrito(carrito)

                

            return redirect(url_for('venta_linea.index', categoria=categoria_sel, busqueda=busqueda))

        # 🔴 ELIMINAR ITEM
        elif 'del-submit' in request.form:
            carrito = _get_carrito()

            idx = int(request.form.get('item_index', -1))

            if 0 <= idx < len(carrito):
             eliminado = carrito.pop(idx)
            _save_carrito(carrito)

            return redirect(url_for('venta_linea.index', categoria=categoria_sel, busqueda=busqueda))

        # 🔵 ACTUALIZAR CANTIDAD
        elif 'upd-submit' in request.form:
            actualizar_form = ActualizarCantidadForm(request.form)

            if actualizar_form.validate():
                idx = int(actualizar_form.item_index.data)
                cantidad = actualizar_form.cantidad.data
                carrito = _get_carrito()

                if 0 <= idx < len(carrito):
                    item = carrito[idx]
                    item['cantidad'] = cantidad
                    _save_carrito(carrito)

            return redirect(url_for('venta_linea.index', categoria=categoria_sel, busqueda=busqueda))

    # ---------------- GET ----------------
    query = Producto.query.filter_by(Activo=True)

    if categoria_sel != 'Todo':
        cat = CategoriaProducto.query.filter_by(Nombre=categoria_sel).first()
        if cat:
            query = query.filter_by(CategoriaId=cat.CategoriaId)

    if busqueda:
        query = query.filter(Producto.Nombre.ilike(f'%{busqueda}%'))

    productos = query.order_by(Producto.Nombre).all()
    for p in productos:
        p.disponibilidad = obtener_disponibilidad_producto(p.ProductoId)

   

    categorias = CategoriaProducto.query.order_by(CategoriaProducto.Nombre).all()

    carrito = _get_carrito()
    subtotal, envio, iva, total = _totales(carrito, None)

    return render_template(
        'venta_linea/index.html',
        productos=productos,
        categorias=categorias,
        categoria_sel=categoria_sel,
        busqueda=busqueda,
        carrito=carrito,
        subtotal=subtotal,
        envio=envio,
        iva=iva,
        total=total,
        agregar_form=AgregarProductoForm(),
        eliminar_form=EliminarItemForm(),
        actualizar_form=ActualizarCantidadForm(),
        filtro_form=filtro_form,
    )

@venta_linea_bp.route('/pedido/<int:pedido_id>')
@login_required
@roles_required('Administrador', 'Usuario')
def ver_pedido(pedido_id):
    # Obtener el pedido solo si pertenece al usuario actual
    pedido = Pedido.query.filter_by(PedidoId=pedido_id, UsuarioId=current_user.UsuarioId).first_or_404()

    # Obtener los detalles de los productos de ese pedido
    detalles = PedidoDetalle.query.filter_by(PedidoId=pedido.PedidoId).all()

    return render_template('venta_linea/ver_pedido.html', pedido=pedido, detalles=detalles)

# --------------------- PEDIDOS ---------------------
@venta_linea_bp.route('/mis-pedidos')
@login_required
@roles_required('Administrador', 'Usuario')
def mis_pedidos():
    # Obtener todos los pedidos del usuario actual
    pedidos = Pedido.query.filter_by(UsuarioId=current_user.UsuarioId).order_by(Pedido.PedidoId.desc()).all()

    return render_template('venta_linea/pedidos.html', pedidos=pedidos)

# --------------------- VACIAR ---------------------

@venta_linea_bp.route('/vaciar')
@login_required
@roles_required('Administrador', 'Usuario')
def vaciar():
    session.pop(CARRITO_KEY, None)
    return redirect(url_for('venta_linea.index'))
# ---------------------------------------------------------------------------
# PASO 2 – Dirección de entrega
# ---------------------------------------------------------------------------
@venta_linea_bp.route('/direccion', methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Usuario')
def direccion():
    carrito = _get_carrito()
    subtotal, envio, iva, total = _totales(carrito, session.get('entrega'))

    if not carrito:
        flash('Tu carrito está vacío. Agrega productos antes de continuar.', 'warning')
        return redirect(url_for('venta_linea.index'))

    form = DireccionForm()

    direcciones_guardadas = Direccion.query.filter_by(
        UsuarioId=current_user.UsuarioId,
        Activa=True
    ).all()

    if form.validate_on_submit():
        session['entrega'] = {
            'tipo': form.tipo_entrega.data,
            'calle': form.calle.data,
            'numero': form.numero.data,
            'colonia': form.colonia.data,
            'ciudad': 'León, Guanajuato',  # 🔥 FIJO
            'codigo_postal': form.codigo_postal.data,
            'referencias': form.referencias.data,
            'horario': request.form.get('horario')
        }

        session.modified = True
        return redirect(url_for('venta_linea.pago'))

    return render_template(
        'venta_linea/direccion.html',
        form=form,
        carrito=carrito,
        subtotal=subtotal,
        envio=envio,
        iva=iva,
        total=total,
        direcciones_guardadas=direcciones_guardadas
    )
# ---------------------------------------------------------------------------
# PASO 3 – Pago
# ---------------------------------------------------------------------------
@venta_linea_bp.route('/pago', methods=['GET', 'POST'])
@login_required
@roles_required('Administrador', 'Usuario')
def pago():
    carrito = _get_carrito()

    if not carrito:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('venta_linea.index'))

    entrega = session.get('entrega')

    if not entrega:
        flash('Por favor confirma tu dirección de entrega primero.', 'warning')
        return redirect(url_for('venta_linea.direccion'))
    
    subtotal, envio, iva, total = _totales(carrito, entrega)


    form = PagoForm()

    if form.validate_on_submit():
        # Validación de fecha de expiración
        anio_exp = int(form.anio_expiracion.data)
        mes_exp  = int(form.mes_expiracion.data)
        hoy      = datetime.utcnow()
        if (anio_exp, mes_exp) < (hoy.year, hoy.month):
            flash('La tarjeta está vencida. Verifica la fecha de expiración.', 'danger')
            return render_template(
                'venta_linea/pago.html', form=form, carrito=carrito,
                subtotal=subtotal, envio=envio, iva=iva, total=total, entrega=entrega
            )

        # ---- Simulación de pasarela de pagos --------------------------------
        # En producción aquí se llamaría a Stripe / Conekta / etc.
        # NUNCA se almacena el número de tarjeta en la BD (PCI-DSS).
        numero_limpio = form.numero_tarjeta.data.replace(" ", "")
        pago_exitoso = _simular_pasarela_pago(
            numero=numero_limpio,
            monto=float(total)
            )


        if not pago_exitoso:
            flash(
                'La tarjeta fue declinada. Verifica los datos o intenta con otro medio de pago.',
                'danger'
            )
            return render_template(
                'venta_linea/pago.html', form=form, carrito=carrito,
                subtotal=subtotal,envio=envio, iva=iva, total=total, entrega=entrega
            )

        # ---- Crear dirección si es a domicilio ------------------------------
        direccion_id = None
        if entrega['tipo'] == 'domicilio':
            nueva_dir = Direccion(
                UsuarioId    = current_user.UsuarioId,
                Calle        = entrega['calle'],
                Numero       = entrega.get('numero', ''),
                Colonia      = entrega['colonia'],
                Ciudad       = 'León, Guanajuato',  # 🔥 FIJO
                CodigoPostal = entrega.get('codigo_postal', ''),
                Referencias  = entrega.get('referencias', ''),
                Activa       = True,
            )
            db.session.add(nueva_dir)
            db.session.flush()
            direccion_id = nueva_dir.DireccionId

        # ---- REGISTRO FINAL DE PEDIDO (VALIDACIÓN FINAL DE STOCK) ----
        for item in carrito:
            stock_f = obtener_disponibilidad_producto(item['producto_id'])
            if item['cantidad'] > stock_f:
                db.session.rollback()
                flash(f'Lo sentimos, el stock de "{item["nombre"]}" cambió mientras tramitabas el pedido. Disponible: {stock_f}', 'danger')
                return redirect(url_for('venta_linea.index'))

        # ---- Crear Pedido ---------------------------------------------------
        # Usamos DireccionId = 0 como placeholder cuando es recolección
        pedido = Pedido(
            UsuarioId    = current_user.UsuarioId,
            DireccionId = direccion_id,
            Estado       = 'Pagado',
            Total        = float(total),
            Observaciones= f"Tipo entrega: {entrega['tipo']}",
        )
        db.session.add(pedido)
        db.session.flush()

        for item in carrito:
            detalle = PedidoDetalle(
                PedidoId      = pedido.PedidoId,
                ProductoId    = item['producto_id'],
                Cantidad      = item['cantidad'],
                PrecioUnitario= item['precio_unitario'],
                Subtotal      = item['precio_unitario'] * item['cantidad'],
            )
            db.session.add(detalle)

        # ---- Crear Venta vinculada al Pedido --------------------------------
        venta = Venta(
            PedidoId = pedido.PedidoId,
            EsEnLinea= True,
            Total    = float(total),
        )
        db.session.add(venta)
        db.session.flush()

        for item in carrito:
            vd = VentaDetalle(
                VentaId       = venta.VentaId,
                ProductoId    = item['producto_id'],
                Cantidad      = item['cantidad'],
                PrecioUnitario= item['precio_unitario'],
            )
            db.session.add(vd)

        # ---- Descuento de Materias Primas y Envío Directo a Producción -------------
        for item in carrito:
            # Descuento manual de MateriaPrima según Receta
            recetas = Receta.query.filter_by(ProductoId=item['producto_id']).all()
            for receta in recetas:
                mp = MateriaPrima.query.get(receta.MateriaPrimaId)
                if mp:
                    cantidad_a_descontar = receta.CantidadBase * item['cantidad']
                    mp.stock = float(mp.stock) - float(cantidad_a_descontar)

                    mov_mp = MovimientoMateriaPrima(
                        MateriaPrimaId=mp.MateriaPrimaId,
                        TipoMovimiento='Salida - Venta Linea',
                        Cantidad=cantidad_a_descontar,
                        ReferenciaId=None  # No hay SolicitudId
                    )
                    db.session.add(mov_mp)

            # Crear directamente la OrdenProduccion
            # Al no tener SolicitudId, podemos dejarlo como NULL o vacío
            op = OrdenProduccion(
                ProductoId=item['producto_id'],
                CantidadProducir=item['cantidad'],
                Estado='En Produccion'
            )
            db.session.add(op)

        # ---- Registrar Pago (sin datos sensibles) ---------------------------
        registro_pago = Pago(
            VentaId   = venta.VentaId,
            MetodoPago= 'Tarjeta',
            Monto     = float(total),
        )
        db.session.add(registro_pago)

        db.session.commit()

        # Limpiar sesión
        session.pop(CARRITO_KEY, None)
        session.pop('entrega', None)

        flash(
            f'Pedido realizado con éxito.',
            'success'
        )
        return redirect(url_for('venta_linea.confirmacion', pedido_id=pedido.PedidoId))

    return render_template(
        'venta_linea/pago.html',
        form     = form,
        carrito  = carrito,
        subtotal = subtotal,
        envio=envio,
        iva      = iva,
        total    = total,
        entrega  = entrega,
    )


# ---------------------------------------------------------------------------
# PASO 4 – Confirmación
# ---------------------------------------------------------------------------
@venta_linea_bp.route('/confirmacion/<int:pedido_id>')
@login_required
@roles_required('Administrador', 'Usuario')
def confirmacion(pedido_id):
    pedido = Pedido.query.filter_by(
        PedidoId  = pedido_id,
        UsuarioId = current_user.UsuarioId
    ).first_or_404()

    detalles = PedidoDetalle.query.filter_by(PedidoId=pedido_id).all()
    for item in detalles:
        producto = Producto.query.get(item.ProductoId)
        item.nombre = producto.Nombre if producto else "Producto eliminado"

    return render_template('venta_linea/confirmacion.html', pedido=pedido, detalles=detalles)


# ---------------------------------------------------------------------------
# Utilidad: Simulador de pasarela de pagos
# ---------------------------------------------------------------------------
def _simular_pasarela_pago(numero: str, monto: float) -> bool:
    """
    Simulación de pasarela.  En producción reemplazar por llamada real
    a Stripe / Conekta / OpenPay usando HTTPS.
    Nunca se persiste el número de tarjeta.
    Tarjeta de prueba para FALLO: 4000000000000002
    """
    TARJETA_DECLINADA = '4000000000000002'
    return numero != TARJETA_DECLINADA
