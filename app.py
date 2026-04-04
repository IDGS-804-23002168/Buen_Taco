from dotenv import load_dotenv

load_dotenv()

import logging
import logging.handlers
import os
from datetime import timedelta

from flask import Flask, render_template, session, redirect, url_for, request
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

    with app.app_context():
        db.create_all()

    csrf.init_app(app)
    mail.init_app(app)

    # ---- Flask-Login ----
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # A01 - redirigir si no autenticado
    login_manager.login_message = "Inicia sesión para acceder."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # ---- Tiempo de sesión (A07 - máximo 10 minutos de inactividad) ----
    @app.before_request
    def renovar_sesion():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=10)
        
        if current_user.is_authenticated and current_user.RequiereCambioPassword:
            # Endpoints permitidos cuando urge el cambio
            if request.endpoint not in ('static', 'auth.cambiar_password', 'auth.logout'):
                return redirect(url_for('auth.cambiar_password'))

    # ---- Registrar Blueprints ----
    from auth import auth_bp 
    app.register_blueprint(auth_bp)

    from disponibilidadProductos import (disponibilidad_bp)
    app.register_blueprint(disponibilidad_bp)


    from proveedores import proveedores      # Módulo 4 - Proveedores
    app.register_blueprint(proveedores) 

    from venta_linea import (venta_linea_bp)   # Módulo 14 - Ventas en linea
    app.register_blueprint(venta_linea_bp)

    from recetas import recetas_bp          # Módulo 7 - Recetas
    app.register_blueprint(recetas_bp)
    
    from produccion import produccion_bp
    app.register_blueprint(produccion_bp)
    
    
    from usuarios import usuarios_bp

    app.register_blueprint(usuarios_bp)

    from dashboard import dashboard_bp  # Módulo 3 - Dashboard

    app.register_blueprint(dashboard_bp)


    from inventario import inventario_bp

    app.register_blueprint(inventario_bp)

    from costoUtilidad import costo_utilidad_bp  # Módulo 11 - Costo y Utilidad

    app.register_blueprint(costo_utilidad_bp)

    from compras import compras as compras_bp

    app.register_blueprint(compras_bp)

    from solicitudProduccion import solicitudes_bp

    app.register_blueprint(solicitudes_bp)


    from venta import ventas_bp

    app.register_blueprint(ventas_bp)

    # ---- Manejadores de error (A05 - no exponer información interna) ----
    @app.errorhandler(404)
    def pagina_no_encontrada(error):
        return render_template("404.html"), 404

    @app.context_processor
    def inject_roles():
        """Inyecta los roles del usuario actual en todas las plantillas."""
        roles = []
        if current_user.is_authenticated:
            roles = [ur.rol.Nombre for ur in current_user.roles if ur.Activo]
        return dict(user_roles=roles)

    # ---- Rutas principales ----
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            roles = [ur.rol.Nombre for ur in current_user.roles if ur.Activo]
            if "Administrador" in roles:
                return redirect(url_for("dashboard.index"))
            elif "Usuario" in roles:
                return redirect(url_for("venta_linea.index"))
            else:
                return render_template("index.html")
        return redirect(url_for("auth.login"))

    return app


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # debug=False en producción (A05)
