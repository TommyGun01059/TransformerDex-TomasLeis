from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import srp
from modelos.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('transformers.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.find_by_username(srp, username)
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(next_page or url_for('transformers.index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('transformers.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validaciones básicas
        if not username or not email or not password:
            flash('Todos los campos son obligatorios', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html')
            
        # Verificar si el usuario ya existe
        if Usuario.find_by_username(srp, username):
            flash('El nombre de usuario ya está en uso', 'danger')
            return render_template('register.html')
            
        if Usuario.find_by_email(srp, email):
            flash('El correo electrónico ya está registrado', 'danger')
            return render_template('register.html')
        
        # Crear el nuevo usuario
        # El primer usuario será administrador
        is_admin = len(list(srp.load_all(Usuario))) == 0
        
        user = Usuario(username, email, password, is_admin=is_admin)
        user.save(srp)
        
        flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('transformers.index')) 