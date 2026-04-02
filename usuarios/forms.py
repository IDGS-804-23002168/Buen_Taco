from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional, ValidationError
)
from models import Usuario


# ---------------------------------------------------------------------------
# VALIDADOR PERSONALIZADO: contraseña segura
# ---------------------------------------------------------------------------
def validar_password_segura(form, field):
    password = field.data

    WEAK_PASSWORDS = {
        "password", "12345678", "123456789", "qwerty123", "password1",
        "iloveyou", "admin123", "letmein1", "welcome1", "monkey123",
        "sunshine", "princess", "football", "superman", "batman123",
        "trustno1", "dragon12", "master12", "abc12345", "passw0rd",
    }

    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not any(c.isupper() for c in password):
        raise ValidationError("Debe contener al menos una letra mayúscula.")
    if not any(c.islower() for c in password):
        raise ValidationError("Debe contener al menos una letra minúscula.")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Debe contener al menos un número.")
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        raise ValidationError("Debe contener al menos un carácter especial (!@#$%...).")
    if password.lower() in WEAK_PASSWORDS:
        raise ValidationError("Esa contraseña es demasiado común. Elige una más segura.")


# ---------------------------------------------------------------------------
# FORMULARIO: Crear usuario
# ---------------------------------------------------------------------------
class CrearUsuarioForm(FlaskForm):
    nombre = StringField(
        'Nombre completo',
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=150, message="Máximo 150 caracteres.")
        ]
    )
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="El username es obligatorio."),
            Length(min=3, max=80, message="Entre 3 y 80 caracteres.")
        ]
    )
    email = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingresa un correo válido."),
            Length(max=150)
        ]
    )
    rol_id = SelectField(
        'Rol',
        coerce=int,
        validators=[DataRequired(message="Selecciona un rol.")]
    )
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            validar_password_segura
        ]
    )
    confirm_password = PasswordField(
        'Confirmar contraseña',
        validators=[
            DataRequired(message="Confirma la contraseña."),
            EqualTo('password', message="Las contraseñas no coinciden.")
        ]
    )
    submit = SubmitField('Crear Usuario')

    # Validaciones de unicidad
    def validate_username(self, field):
        if Usuario.query.filter_by(Username=field.data.strip()).first():
            raise ValidationError("El nombre de usuario ya está en uso.")

    def validate_email(self, field):
        if Usuario.query.filter_by(Email=field.data.strip().lower()).first():
            raise ValidationError("El correo ya está registrado.")


# ---------------------------------------------------------------------------
# FORMULARIO: Editar usuario
# ---------------------------------------------------------------------------
class EditarUsuarioForm(FlaskForm):
    nombre = StringField(
        'Nombre completo',
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=150, message="Máximo 150 caracteres.")
        ]
    )
    email = StringField(
        'Correo electrónico',
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingresa un correo válido."),
            Length(max=150)
        ]
    )
    rol_id = SelectField(
        'Rol',
        coerce=int,
        validators=[DataRequired(message="Selecciona un rol.")]
    )
    submit = SubmitField('Guardar Cambios')

    def __init__(self, usuario_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Guardamos el id del usuario que se está editando
        # para poder excluirlo en la validación de unicidad
        self.usuario_id = usuario_id

    def validate_email(self, field):
        existente = Usuario.query.filter(
            Usuario.Email == field.data.strip().lower(),
            Usuario.UsuarioId != self.usuario_id
        ).first()
        if existente:
            raise ValidationError("El correo ya está en uso por otro usuario.")