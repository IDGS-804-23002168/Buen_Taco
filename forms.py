from flask_wtf import FlaskForm
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