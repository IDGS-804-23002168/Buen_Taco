from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, SubmitField, BooleanField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Email, Length, ValidationError, Optional
import re
from models import Proveedor

from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, DecimalField,
    TextAreaField, SelectField, HiddenField, SubmitField
)
from wtforms.validators import (
    DataRequired, Email, Length, NumberRange,
    Optional, Regexp
)


from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, IntegerField, HiddenField,
    TextAreaField, SubmitField, RadioField
)
from wtforms.validators import DataRequired, Email, Length, Regexp, NumberRange, Optional


class AgregarProductoForm(FlaskForm):
    producto_id = HiddenField('ProductoId', validators=[DataRequired()])
    cantidad = IntegerField(
        'Cantidad',
        default=1,
        validators=[
            DataRequired(),
            NumberRange(min=1, max=50, message='La cantidad debe estar entre 1 y 50.')
        ]
    )
    notas = StringField(
        'Notas / Modificaciones',
        validators=[
            Optional(),
            Length(max=200, message='Las notas no pueden superar 200 caracteres.')
        ]
    )
    submit = SubmitField('Agregar al carrito')


class EliminarItemForm(FlaskForm):

    item_index = HiddenField('ItemIndex', validators=[DataRequired()])
    submit = SubmitField('Eliminar')

class ActualizarCantidadForm(FlaskForm):

    item_index = HiddenField('ItemIndex', validators=[DataRequired()])
    cantidad = IntegerField(
        'Cantidad',
        validators=[DataRequired(), NumberRange(min=1, max=50)]
    )
    submit = SubmitField('Actualizar')



class DireccionForm(FlaskForm):
    tipo_entrega = RadioField(
        'Tipo de entrega',
        choices=[('domicilio', 'Envío a domicilio'), ('sucursal', 'Recoger en sucursal')],
        default='domicilio',
        validators=[DataRequired()]
    )

    calle = StringField('Calle', validators=[Optional(), Length(max=150)])
    numero = StringField('Número', validators=[Optional(), Length(max=20)])
    colonia = StringField('Colonia', validators=[Optional(), Length(max=100)])

    codigo_postal = StringField(
    'Código Postal',
    validators=[
        Optional(),
        Regexp(r'^\d{5}$', message='El código postal debe tener 5 dígitos.')
    ]
)

    referencias = TextAreaField('Referencias', validators=[Optional(), Length(max=255)])

    # 🔥 NUEVO CAMPO HORARIO
    horario = SelectField(
        'Horario de recolección',
        choices=[
            ('', 'Selecciona un horario'),
            ('6:00-6:30', '6:00 - 6:30'),
            ('6:30-7:00', '6:30 - 7:00'),
            ('7:00-7:30', '7:00 - 7:30'),
            ('7:30-8:00', '7:30 - 8:00'),
            ('8:00-8:30', '8:00 - 8:30'),
            ('8:30-9:00', '8:30 - 9:00'),
            ('9:00-9:30', '9:00 - 9:30'),
            ('9:30-10:00', '9:30 - 10:00'),
            ('10:00-10:30', '10:00 - 10:30'),
            ('10:30-11:00', '10:30 - 11:00'),
            ('11:00-11:30', '11:00 - 11:30'),
            ('11:30-12:00', '11:30 - 12:00'),
        ],
        validators=[Optional()]
    )

    submit = SubmitField('Continuar')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if self.tipo_entrega.data == "domicilio":
            valid = True

            if not self.calle.data:
                self.calle.errors.append("La calle es obligatoria.")
                valid = False

            if not self.numero.data:
                self.numero.errors.append("El número es obligatorio.")
                valid = False

            if not self.colonia.data:
                self.colonia.errors.append("La colonia es obligatoria.")
                valid = False

            return valid

        # 🔥 VALIDAR HORARIO SI ES SUCURSAL
        if self.tipo_entrega.data == "sucursal":
            if not self.horario.data:
                self.horario.errors.append("Selecciona un horario de recolección.")
                return False

        return True


class PagoForm(FlaskForm):
    nombre_titular = StringField(
        'Nombre en la tarjeta',
        validators=[
            DataRequired(message='El nombre del titular es obligatorio.'),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres.')
        ]
    )
    numero_tarjeta = StringField(
    'Número de tarjeta',
    validators=[
        DataRequired(message='El número de tarjeta es obligatorio.'),
        Regexp(
            r'^(\d{4}\s){3}\d{4}$',
            message='Formato inválido. Usa: 1234 5678 9012 3456'
        )
    ]
)
    mes_expiracion = SelectField(
        'Mes',
        choices=[(str(i).zfill(2), str(i).zfill(2)) for i in range(1, 13)],
        validators=[DataRequired()]
    )
    anio_expiracion = SelectField(
        'Año',
        choices=[(str(a), str(a)) for a in range(2025, 2036)],
        validators=[DataRequired()]
    )
    cvv = StringField(
        'CVV',
        validators=[
            DataRequired(message='El CVV es obligatorio.'),
            Regexp(r'^\d{3,4}$', message='El CVV debe tener 3 o 4 dígitos.')
        ]
    )
    submit = SubmitField('Pagar ahora')


class FiltroCategoriaForm(FlaskForm):
    categoria = HiddenField('Categoria', default='Todo')
    busqueda  = StringField('Buscar producto', validators=[Optional(), Length(max=100)])
    submit    = SubmitField('Buscar')



# ---------------------------------------------------------------------------
# FORMULARIO MATERIA PRIMA 
# ---------------------------------------------------------------------------
class MateriaPrimaForm(FlaskForm):
    nombre = StringField('Nombre del Insumo', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=2, max=100, message="El nombre debe tener entre 2 y 100 caracteres.")
    ])
    unidad_id = SelectField('Unidad de Medida', coerce=int, validators=[
        DataRequired(message="Selecciona una unidad de medida válida.")
    ])
    merma = DecimalField('Porcentaje de Merma (%)', default=0.0, validators=[
        NumberRange(min=0, max=80, message="Para evitar desperdicios severos, la merma máxima permitida es del 80%.")
    ])
    submit = SubmitField('Guardar')

# ---------------------------------------------------------------------------
# VALIDADORES PERSONALIZADOS 
# ---------------------------------------------------------------------------
def validar_rfc(form, field):
    if not field.data:
        return
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
        validators=[DataRequired(message='El nombre del proveedor es obligatorio.'),
                    Length(max=150, message='El nombre no puede exceder 150 caracteres.')]
    )
    RFC = StringField(
        'RFC',
        validators=[DataRequired(message='El RFC es obligatorio.'),
                    Length(min=12, max=13, message='El RFC debe tener 12 o 13 caracteres.'),
                    validar_rfc]
    )
    Categoria = StringField(
        'Categoría de Productos',
        validators=[DataRequired(message='La categoría es obligatoria.'),
                    Length(max=100, message='La categoría no puede exceder 100 caracteres.')]
    )
    Direccion = TextAreaField(
        'Dirección',
        validators=[DataRequired(message='La dirección es obligatoria.'),
                    Length(max=255, message='La dirección no puede exceder 255 caracteres.')]
    )
    ContactoPrincipal = StringField(
        'Contacto Principal',
        validators=[DataRequired(message='El contacto principal es obligatorio.'),
                    Length(max=150, message='El nombre del contacto no puede exceder 150 caracteres.')]
    )
    Telefono = StringField(
        'Teléfono',
        validators=[DataRequired(message='El teléfono es obligatorio.'), validar_telefono]
    )
    Email = StringField(
        'Correo Electrónico',
        validators=[DataRequired(message='El correo electrónico es obligatorio.'),
                    Email(message='Formato de correo electrónico inválido.'),
                    Length(max=150, message='El correo no puede exceder 150 caracteres.')]
    )
    Banco = StringField(
        'Banco',
        validators=[DataRequired(message='El banco es obligatorio.'),
                    Length(max=100, message='El nombre del banco no puede exceder 100 caracteres.')]
    )
    CuentaBancaria = StringField(
        'Número de Cuenta',
        validators=[DataRequired(message='La cuenta bancaria es obligatoria.'), validar_cuenta_bancaria]
    )
    CLABE = StringField(
        'CLABE Interbancaria',
        validators=[DataRequired(message='La CLABE es obligatoria.'), validar_clabe]
    )
    Activo = BooleanField('Proveedor activo', default=True)
    Notas = TextAreaField(
        'Notas adicionales',
        validators=[DataRequired(message='Las notas son obligatorias.'),
                    Length(max=500, message='Las notas no pueden exceder 500 caracteres.')]
    )

    # VALIDACIONES DE DUPLICADOS
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