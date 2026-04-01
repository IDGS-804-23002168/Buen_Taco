from flask_wtf import FlaskForm
<<<<<<< HEAD
from wtforms import StringField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class MateriaPrimaForm(FlaskForm):
    nombre = StringField('Nombre del Insumo', validators=[
        DataRequired(message="El nombre es obligatorio")
    ])
    unidad_id = SelectField('Unidad de Medida', coerce=int, validators=[
        DataRequired(message="Selecciona una unidad")
    ])
    merma = DecimalField('Porcentaje de Merma (%)', default=0.0, validators=[
        NumberRange(min=0, max=100, message="La merma debe estar entre 0 y 100")
    ])
    submit = SubmitField('Guardar')
=======
from wtforms import StringField, BooleanField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
import re
from models import Proveedor


# ---------------------------------------------------------------------------
# VALIDADORES PERSONALIZADOS
# ---------------------------------------------------------------------------
def validar_rfc(form, field):
    if not field.data:
        return  # deja que DataRequired maneje vacío
    rfc = field.data.strip().upper()
    patron = r'^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$'
    if not re.match(patron, rfc):
        raise ValidationError('RFC inválido. Formato esperado: XAXX010101000 (moral/física).')


def validar_telefono(form, field):
    if not field.data:
        return
    tel = re.sub(r'[\s\-\(\)\+]', '', field.data)
    if not tel.isdigit() or not (10 <= len(tel) <= 15):
        raise ValidationError('Teléfono inválido. Debe contener entre 10 y 15 dígitos.')


def validar_cuenta_bancaria(form, field):
    if not field.data:
        return
    cuenta = re.sub(r'\s', '', field.data)
    if not cuenta.isdigit() or not (10 <= len(cuenta) <= 18):
        raise ValidationError('Número de cuenta inválido. Debe tener entre 10 y 18 dígitos.')


def validar_clabe(form, field):
    if not field.data:
        return
    clabe = re.sub(r'\s', '', field.data)
    if not clabe.isdigit() or len(clabe) != 18:
        raise ValidationError('CLABE inválida. Debe contener exactamente 18 dígitos.')


# ---------------------------------------------------------------------------
# FORMULARIO PROVEEDOR
# ---------------------------------------------------------------------------
class ProveedorForm(FlaskForm):

    proveedor_id = HiddenField()

    Nombre = StringField(
        'Nombre / Razón Social',
        validators=[
            DataRequired(message='El nombre del proveedor es obligatorio.'),
            Length(max=150, message='El nombre no puede exceder 150 caracteres.')
        ]
    )

    RFC = StringField(
        'RFC',
        validators=[
            DataRequired(message='El RFC es obligatorio.'),
            Length(min=12, max=13, message='El RFC debe tener 12 o 13 caracteres.'),
            validar_rfc
        ]
    )

    Categoria = StringField(
        'Categoría de Productos',
        validators=[
            DataRequired(message='La categoría es obligatoria.'),
            Length(max=100, message='La categoría no puede exceder 100 caracteres.')
        ]
    )

    Direccion = TextAreaField(
        'Dirección',
        validators=[
            DataRequired(message='La dirección es obligatoria.'),
            Length(max=255, message='La dirección no puede exceder 255 caracteres.')
        ]
    )

    ContactoPrincipal = StringField(
        'Contacto Principal',
        validators=[
            DataRequired(message='El contacto principal es obligatorio.'),
            Length(max=150, message='El nombre del contacto no puede exceder 150 caracteres.')
        ]
    )

    Telefono = StringField(
        'Teléfono',
        validators=[
            DataRequired(message='El teléfono es obligatorio.'),
            validar_telefono
        ]
    )

    Email = StringField(
        'Correo Electrónico',
        validators=[
            DataRequired(message='El correo electrónico es obligatorio.'),
            Email(message='Formato de correo electrónico inválido.'),
            Length(max=150, message='El correo no puede exceder 150 caracteres.')
        ]
    )

    Banco = StringField(
        'Banco',
        validators=[
            DataRequired(message='El banco es obligatorio.'),
            Length(max=100, message='El nombre del banco no puede exceder 100 caracteres.')
        ]
    )

    CuentaBancaria = StringField(
        'Número de Cuenta',
        validators=[
            DataRequired(message='La cuenta bancaria es obligatoria.'),
            validar_cuenta_bancaria
        ]
    )

    CLABE = StringField(
        'CLABE Interbancaria',
        validators=[
            DataRequired(message='La CLABE es obligatoria.'),
            validar_clabe
        ]
    )

    Activo = BooleanField('Proveedor activo', default=True)

    Notas = TextAreaField(
        'Notas adicionales',
        validators=[
            DataRequired(message='Las notas son obligatorias.'),
            Length(max=500, message='Las notas no pueden exceder 500 caracteres.')
        ]
    )

    # ---------------- VALIDACIONES DE DUPLICADOS ----------------
    def validate_Nombre(self, field):
        proveedor = Proveedor.query.filter_by(Nombre=field.data.strip()).first()
        if proveedor and str(proveedor.ProveedorId) != self.proveedor_id.data:
            raise ValidationError('El nombre del proveedor ya está registrado.')

    def validate_RFC(self, field):
        proveedor = Proveedor.query.filter_by(RFC=field.data.strip().upper()).first()
        if proveedor and str(proveedor.ProveedorId) != self.proveedor_id.data:
            raise ValidationError('El RFC ya existe en la base de datos.')

    def validate_Email(self, field):
        proveedor = Proveedor.query.filter_by(Email=field.data.strip().lower()).first()
        if proveedor and str(proveedor.ProveedorId) != self.proveedor_id.data:
            raise ValidationError('El correo electrónico ya está registrado.')

    def validate_CuentaBancaria(self, field):
        proveedor = Proveedor.query.filter_by(CuentaBancaria=field.data.strip()).first()
        if proveedor and str(proveedor.ProveedorId) != self.proveedor_id.data:
            raise ValidationError('El número de cuenta ya existe.')

    def validate_CLABE(self, field):
        proveedor = Proveedor.query.filter_by(CLABE=field.data.strip()).first()
        if proveedor and str(proveedor.ProveedorId) != self.proveedor_id.data:
            raise ValidationError('La CLABE ya está registrada.')


# ---------------------------------------------------------------------------
# FORMULARIO DE BÚSQUEDA
# ---------------------------------------------------------------------------
class BusquedaProveedorForm(FlaskForm):
    class Meta:
        csrf = False

    q = StringField('Buscar', validators=[Length(max=150)])
    estado = SelectField(
        'Estado',
        choices=[('todos', 'Todos'), ('activo', 'Activos'), ('inactivo', 'Inactivos')],
        default='todos'
    )
    categoria = StringField('Categoría', validators=[Length(max=100)])
>>>>>>> 6a0bd7e (Modulo Proveedores)
