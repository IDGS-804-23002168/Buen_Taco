from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField, FloatField, StringField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class FormProducto(FlaskForm):
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es obligatorio.'),
            Length(max=150, message='Máximo 150 caracteres.')
        ]
    )
    descripcion = TextAreaField(
        'Descripción',
        validators=[Optional(), Length(max=500)]
    )
    categoria_id = SelectField(
        'Categoría',
        coerce=int,
        validators=[DataRequired(message='Selecciona una categoría.')]
    )
    precio = FloatField(
        'Precio de Venta',
        validators=[Optional(), NumberRange(min=0, message='El precio no puede ser negativo.')],
        default=0
    )
    imagen = FileField(
        'Imagen del producto',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo imágenes (jpg, png, webp).')
        ]
    )
