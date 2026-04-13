from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import event
from utils.logger_util import registrar_movimiento

db = SQLAlchemy()



# ---------------------------------------------------------------------------
# CATÁLOGOS BASE
# ---------------------------------------------------------------------------
class CategoriaProducto(db.Model):
    __tablename__ = 'CategoriasProducto'

    CategoriaId = db.Column(db.Integer, primary_key=True)
    Nombre      = db.Column(db.String(100), nullable=False)

    productos = db.relationship('Producto', backref='categoria', lazy=True)


class UnidadMedida(db.Model):
    __tablename__ = 'UnidadesMedida'

    UnidadId    = db.Column(db.Integer, primary_key=True)
    Nombre      = db.Column(db.String(50), nullable=False)
    Abreviatura = db.Column(db.String(10), nullable=False)


class Proveedor(db.Model):
    __tablename__ = 'Proveedores'

    ProveedorId = db.Column(db.Integer, primary_key=True)

    Nombre = db.Column(db.String(150), nullable=False, unique=True)
    RFC = db.Column(db.String(13), nullable=False, unique=True)
    Categoria = db.Column(db.String(100), nullable=False)
    Direccion = db.Column(db.String(255), nullable=False)
    ContactoPrincipal = db.Column(db.String(150), nullable=False)
    Telefono = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(150), nullable=False, unique=True)

    Banco = db.Column(db.String(100))
    CuentaBancaria = db.Column(db.String(18), unique=True, nullable=False)
    CLABE = db.Column(db.String(18), unique=True, nullable=False)

    Activo = db.Column(db.Boolean, default=True)
    Notas = db.Column(db.String(500))

    compras = db.relationship('Compra', backref='proveedor', lazy=True)


# ---------------------------------------------------------------------------
# COMPRAS
# ---------------------------------------------------------------------------
class Compra(db.Model):
    __tablename__ = 'Compras'

    CompraId    = db.Column(db.Integer, primary_key=True)
    ProveedorId = db.Column(db.Integer, db.ForeignKey('Proveedores.ProveedorId'), nullable=False)
    Fecha       = db.Column(db.DateTime, default=datetime.utcnow)
    Total       = db.Column(db.Numeric(10, 2))

    detalles = db.relationship('CompraDetalle', backref='compra', lazy=True)


class CompraDetalle(db.Model):
    __tablename__ = 'CompraDetalle'

    CompraDetalleId = db.Column(db.Integer, primary_key=True)
    CompraId        = db.Column(db.Integer, db.ForeignKey('Compras.CompraId'), nullable=False)
    MateriaPrimaId  = db.Column(db.Integer, db.ForeignKey('MateriasPrimas.MateriaPrimaId'), nullable=False)
    Cantidad        = db.Column(db.Numeric(10, 2), nullable=False)
    PrecioUnitario  = db.Column(db.Numeric(10, 2))
    Subtotal        = db.Column(db.Numeric(10, 2))

    materia_prima = db.relationship('MateriaPrima')


# ---------------------------------------------------------------------------
# MATERIAS PRIMAS
# ---------------------------------------------------------------------------
class MateriaPrima(db.Model):
    __tablename__ = 'MateriasPrimas'

    MateriaPrimaId   = db.Column(db.Integer, primary_key=True)
    Nombre           = db.Column(db.String(150), nullable=False)
    UnidadBaseId     = db.Column(db.Integer, db.ForeignKey('UnidadesMedida.UnidadId'), nullable=False)
    PorcentajeMerma  = db.Column(db.Numeric(5, 2), default=0)
    stock            = db.Column(db.Numeric(7, 2), nullable=False, default=0.00)
    Activo           = db.Column(db.Boolean, default=True)
    stock            = db.Column(db.Numeric(7, 2), nullable=False, default=0.00)

    unidad = db.relationship('UnidadMedida')


class MovimientoMateriaPrima(db.Model):
    __tablename__ = 'MovimientoMateriaPrima'

    MovimientoId   = db.Column(db.Integer, primary_key=True)
    MateriaPrimaId = db.Column(db.Integer, db.ForeignKey('MateriasPrimas.MateriaPrimaId'), nullable=False)
    TipoMovimiento = db.Column(db.String(50))
    Cantidad       = db.Column(db.Numeric(10, 2), nullable=False)
    Fecha          = db.Column(db.DateTime, default=datetime.utcnow)
    ReferenciaId   = db.Column(db.Integer)

    materia_prima = db.relationship('MateriaPrima')


# ---------------------------------------------------------------------------
# PRODUCTOS Y RECETAS
# ---------------------------------------------------------------------------
class Producto(db.Model):
    __tablename__ = 'Productos'

    ProductoId               = db.Column(db.Integer, primary_key=True)
    CategoriaId              = db.Column(db.Integer, db.ForeignKey('CategoriasProducto.CategoriaId'), nullable=False)
    Nombre                   = db.Column(db.String(150), nullable=False)
    Descripcion              = db.Column(db.Text)
    Precio                   = db.Column(db.Numeric(10, 2), nullable=False)
    CostoUltimaActualizacion = db.Column(db.DateTime)
    Activo                   = db.Column(db.Boolean, default=True)

    imagen_url = db.Column(db.String(255))

    recetas = db.relationship('Receta', backref='producto', lazy=True)


class Receta(db.Model):
    __tablename__ = 'Recetas'

    ProductoId     = db.Column(db.Integer, db.ForeignKey('Productos.ProductoId'), primary_key=True)
    MateriaPrimaId = db.Column(db.Integer, db.ForeignKey('MateriasPrimas.MateriaPrimaId'), primary_key=True)
    CantidadBase   = db.Column(db.Numeric(10, 2), nullable=False)

    materia_prima = db.relationship('MateriaPrima')


# ---------------------------------------------------------------------------
# PRODUCCIÓN
# ---------------------------------------------------------------------------
class SolicitudProduccion(db.Model):
    __tablename__ = 'SolicitudProduccion'

    SolicitudId = db.Column(db.Integer, primary_key=True)
    Fecha       = db.Column(db.DateTime, default=datetime.utcnow)
    Estado      = db.Column(db.String(50))

    detalles = db.relationship('SolicitudDetalle', backref='solicitud', lazy=True)
    ordenes  = db.relationship('OrdenProduccion', backref='solicitud', lazy=True)


class SolicitudDetalle(db.Model):
    __tablename__ = 'SolicitudDetalle'

    SolicitudDetalleId = db.Column(db.Integer, primary_key=True)
    SolicitudId        = db.Column(db.Integer, db.ForeignKey('SolicitudProduccion.SolicitudId'), nullable=False)
    ProductoId         = db.Column(db.Integer, db.ForeignKey('Productos.ProductoId'), nullable=False)
    CantidadSolicitada = db.Column(db.Integer, nullable=False)

    producto = db.relationship('Producto')


class OrdenProduccion(db.Model):
    __tablename__ = 'OrdenProduccion'

    OrdenProduccionId = db.Column(db.Integer, primary_key=True)
    SolicitudId       = db.Column(db.Integer, db.ForeignKey('SolicitudProduccion.SolicitudId'))
    ProductoId        = db.Column(db.Integer, db.ForeignKey('Productos.ProductoId'), nullable=False)
    CantidadProducir  = db.Column(db.Integer, nullable=False)
    FechaInicio       = db.Column(db.DateTime, default=datetime.utcnow)
    FechaFin          = db.Column(db.DateTime)
    Estado            = db.Column(db.String(50))

    producto = db.relationship('Producto')


class MovimientoProducto(db.Model):
    __tablename__ = 'MovimientoProducto'

    MovimientoId   = db.Column(db.Integer, primary_key=True)
    ProductoId     = db.Column(db.Integer, db.ForeignKey('Productos.ProductoId'), nullable=False)
    TipoMovimiento = db.Column(db.String(50))
    Cantidad       = db.Column(db.Integer, nullable=False)
    Fecha          = db.Column(db.DateTime, default=datetime.utcnow)
    ReferenciaId   = db.Column(db.Integer)

    producto = db.relationship('Producto')


# ---------------------------------------------------------------------------
# CLIENTES Y PEDIDOS
# ---------------------------------------------------------------------------
class Cliente(db.Model):
    __tablename__ = 'Clientes'

    ClienteId      = db.Column(db.Integer, primary_key=True)
    Nombre         = db.Column(db.String(150))
    Telefono       = db.Column(db.String(20))
    Email          = db.Column(db.String(150))
    FechaRegistro  = db.Column(db.DateTime, default=datetime.utcnow)


class Pedido(db.Model):
    __tablename__ = 'Pedidos'

    PedidoId      = db.Column(db.Integer, primary_key=True)
    UsuarioId     = db.Column(db.Integer, db.ForeignKey('Usuarios.UsuarioId'), nullable=False)
    DireccionId   = db.Column(db.Integer, db.ForeignKey('Direcciones.DireccionId'), nullable=True)
    Fecha         = db.Column(db.DateTime, default=datetime.utcnow)
    Estado        = db.Column(db.String(50))
    Total         = db.Column(db.Numeric(10, 2))
    Observaciones = db.Column(db.String(255))

    detalles = db.relationship('PedidoDetalle', backref='pedido', lazy=True)


class PedidoDetalle(db.Model):
    __tablename__ = 'PedidoDetalle'

    PedidoDetalleId = db.Column(db.Integer, primary_key=True)
    PedidoId        = db.Column(db.Integer, db.ForeignKey('Pedidos.PedidoId'), nullable=False)
    ProductoId      = db.Column(db.Integer, db.ForeignKey('Productos.ProductoId'), nullable=False)
    Cantidad        = db.Column(db.Integer, nullable=False)
    PrecioUnitario  = db.Column(db.Numeric(10, 2))
    Subtotal        = db.Column(db.Numeric(10, 2))

    producto = db.relationship('Producto')


# ---------------------------------------------------------------------------
# VENTAS
# ---------------------------------------------------------------------------
class Venta(db.Model):
    __tablename__ = 'Ventas'

    VentaId   = db.Column(db.Integer, primary_key=True)
    ClienteId = db.Column(db.Integer, db.ForeignKey('Clientes.ClienteId'))
    PedidoId  = db.Column(db.Integer, db.ForeignKey('Pedidos.PedidoId'))
    EsEnLinea = db.Column(db.Boolean, default=False)
    Fecha     = db.Column(db.DateTime, default=datetime.utcnow)
    Total     = db.Column(db.Numeric(10, 2))

    detalles = db.relationship('VentaDetalle', backref='venta', lazy=True)


class VentaDetalle(db.Model):
    __tablename__ = 'VentaDetalle'

    VentaDetalleId = db.Column(db.Integer, primary_key=True)
    VentaId        = db.Column(db.Integer, db.ForeignKey('Ventas.VentaId'), nullable=False)
    ProductoId     = db.Column(db.Integer, db.ForeignKey('Productos.ProductoId'), nullable=False)
    Cantidad       = db.Column(db.Integer, nullable=False)
    PrecioUnitario = db.Column(db.Numeric(10, 2))
    Subtotal       = db.Column(db.Numeric(10, 2))


class Pago(db.Model):
    __tablename__ = 'Pagos'

    PagoId      = db.Column(db.Integer, primary_key=True)
    VentaId     = db.Column(db.Integer, db.ForeignKey('Ventas.VentaId'), nullable=False)
    MetodoPago  = db.Column(db.String(50))
    Monto       = db.Column(db.Numeric(10, 2))
    Fecha       = db.Column(db.DateTime, default=datetime.utcnow)


class CorteCaja(db.Model):
    __tablename__ = 'CorteCaja'

    CorteId      = db.Column(db.Integer, primary_key=True)
    Fecha        = db.Column(db.Date, nullable=False)
    TotalVentas  = db.Column(db.Numeric(10, 2))
    TotalEfectivo = db.Column(db.Numeric(10, 2))
    TotalSalidas  = db.Column(db.Numeric(10, 2))
    Utilidad      = db.Column(db.Numeric(10, 2))


# ---------------------------------------------------------------------------
# USUARIOS Y SEGURIDAD
# ---------------------------------------------------------------------------
class Rol(db.Model):
    __tablename__ = 'Roles'

    RolId      = db.Column(db.Integer, primary_key=True)
    Nombre     = db.Column(db.String(100), unique=True, nullable=False)
    Descripcion = db.Column(db.String(255))
    Activo     = db.Column(db.Boolean, default=True)


class Usuario(UserMixin, db.Model):
    """
    Modelo de usuario con soporte completo para Flask-Login.
    Incluye campos de seguridad OWASP A07 y recuperación de contraseña.
    """
    __tablename__ = 'Usuarios'

    UsuarioId    = db.Column(db.Integer, primary_key=True)
    Nombre       = db.Column(db.String(150), nullable=False)
    Username     = db.Column(db.String(100), unique=True, nullable=False)
    Email        = db.Column(db.String(150), unique=True, nullable=False)

    PasswordHash = db.Column(db.String(255), nullable=False)
    Salt         = db.Column(db.String(255), nullable=False, default='')

    IntentosFallidos       = db.Column(db.Integer, default=0)
    Bloqueado              = db.Column(db.Boolean, default=False)
    FechaBloqueo           = db.Column(db.DateTime)

    UltimoLogin            = db.Column(db.DateTime)

    FechaCambioPassword    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    RequiereCambioPassword = db.Column(db.Boolean, default=False)

    # 2FA
    Token2FA               = db.Column(db.String(10))
    Token2FAExpiracion     = db.Column(db.DateTime)
    TwoFactorHabilitado    = db.Column(db.Boolean, default=False)

    # Recuperación de contraseña
    TokenRecuperacion      = db.Column(db.String(64))
    TokenRecuperacionExp   = db.Column(db.DateTime)

    Activo = db.Column(db.Boolean, default=True)

    roles     = db.relationship('UsuariosRoles', backref='usuario', lazy=True)
    direcciones = db.relationship('Direccion', backref='usuario', lazy=True)

    # Flask-Login: usar UsuarioId como identificador de sesión
    def get_id(self):
        return str(self.UsuarioId)


class UsuariosRoles(db.Model):
    __tablename__ = 'UsuariosRoles'

    UsuarioId       = db.Column(db.Integer, db.ForeignKey('Usuarios.UsuarioId'), primary_key=True)
    RolId           = db.Column(db.Integer, db.ForeignKey('Roles.RolId'), primary_key=True)
    FechaAsignacion = db.Column(db.DateTime, default=datetime.utcnow)
    Activo          = db.Column(db.Boolean, default=True)

    rol = db.relationship('Rol')


class Direccion(db.Model):
    __tablename__ = 'Direcciones'

    DireccionId  = db.Column(db.Integer, primary_key=True)
    UsuarioId    = db.Column(db.Integer, db.ForeignKey('Usuarios.UsuarioId'), nullable=False)
    Calle        = db.Column(db.String(150))
    Numero       = db.Column(db.String(20))
    Colonia      = db.Column(db.String(100))
    Ciudad       = db.Column(db.String(100))
    Estado       = db.Column(db.String(100))
    CodigoPostal = db.Column(db.String(10))
    Referencias  = db.Column(db.String(255))
    Activa       = db.Column(db.Boolean, default=True)


# ---------------------------------------------------------------------------
# EVENTOS DE AUDITORÍA AUTOMÁTICA
# ---------------------------------------------------------------------------

def setup_audit_logging():
    def get_pk(obj):
        """Helper para obtener la llave primaria como string."""
        from sqlalchemy import inspect
        ins = inspect(obj)
        return ", ".join([str(getattr(obj, key.name)) for key in ins.mapper.primary_key])

    @event.listens_for(db.Session, 'after_flush')
    def after_flush(session, flush_context):
        for obj in session.new:
            if isinstance(obj, db.Model):
                registrar_movimiento(
                    accion=f"INSERT_{obj.__class__.__name__}",
                    detalle=f"Registro creado con ID: {get_pk(obj)}"
                )
        
        for obj in session.dirty:
            if isinstance(obj, db.Model):
                # Solo registrar si realmente cambió algo
                from sqlalchemy import inspect
                ins = inspect(obj)
                if ins.persistent and ins.attrs:
                    changed = [attr.key for attr in ins.attrs if attr.history.has_changes()]
                    if changed:
                        registrar_movimiento(
                            accion=f"UPDATE_{obj.__class__.__name__}",
                            detalle=f"Registro ID {get_pk(obj)} modificado en campos: {', '.join(changed)}"
                        )

        for obj in session.deleted:
            if isinstance(obj, db.Model):
                registrar_movimiento(
                    accion=f"DELETE_{obj.__class__.__name__}",
                    detalle=f"Registro ID {get_pk(obj)} eliminado"
                )

# Llamar a la configuración de eventos
setup_audit_logging()
