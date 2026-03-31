import logging
import logging.handlers
import os
from datetime import timedelta

from flask import Flask, render_template, session, redirect, url_for
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

from config import DevelopmentConfig
from models import db, Usuario

# ---------------------------------------------------------------------------
# Instancias de extensiones (se configuran con la app en create_app)
# ---------------------------------------------------------------------------
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()


def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config)

    # ---- Inicializar extensiones ----
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    # ---- Flask-Login ----
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'          # A01 - redirigir si no autenticado
    login_manager.login_message = 'Inicia sesión para acceder.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # ---- Tiempo de sesión (A07 - máximo 10 minutos de inactividad) ----
    @app.before_request
    def renovar_sesion():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=10)

    # ---- Registrar Blueprints ----
    from auth import auth_bp
    app.register_blueprint(auth_bp)



    # ---- Manejadores de error (A05 - no exponer información interna) ----
    @app.errorhandler(404)
    def pagina_no_encontrada(error):
        return render_template("404.html"), 404


    # ---- Rutas principales ----
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            # return redirect(url_for('dashboard.index'))
            return render_template("index.html")
        return redirect(url_for('auth.login'))

    return app


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=False)   # debug=False en producción (A05)
