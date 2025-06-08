from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os
from extensions import srp
from modelos.usuario import Usuario

# Cargar variables de entorno
load_dotenv()

# Inicializar aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave-secreta-por-defecto')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB límite para subidas

# Inicializar protección CSRF
csrf = CSRFProtect(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.find(srp, user_id)

# Ruta para favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Importar y registrar blueprints
from rutas.auth import auth_bp
from rutas.transformers import transformers_bp
from rutas.comentarios import comentarios_bp
from rutas.puntuaciones import puntuaciones_bp

app.register_blueprint(auth_bp)
app.register_blueprint(transformers_bp)
app.register_blueprint(comentarios_bp)
app.register_blueprint(puntuaciones_bp)

if __name__ == '__main__':
    app.run(debug=True) 