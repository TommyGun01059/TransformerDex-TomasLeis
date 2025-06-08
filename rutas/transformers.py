from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from extensions import srp
from modelos.transformer import Transformer
from modelos.comentario import Comentario
from modelos.puntuacion import Puntuacion

transformers_bp = Blueprint('transformers', __name__)

# Configuración para subida de imágenes
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Asegurarse de que existe el directorio de uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@transformers_bp.route('/')
def index():
    transformers = Transformer.find_all(srp)
    return render_template('index.html', transformers=transformers)

@transformers_bp.route('/transformer/<transformer_id>')
def detail(transformer_id):
    transformer = Transformer.find(srp, transformer_id)
    if not transformer:
        flash('Transformer no encontrado', 'danger')
        return redirect(url_for('transformers.index'))
    
    # Obtener comentarios directamente sin filtrado adicional
    comentarios = Comentario.find_by_transformer(srp, transformer_id)
    
    # Obtener puntuación promedio
    puntuacion_promedio = Puntuacion.calcular_promedio(srp, transformer_id)
    
    # Obtener puntuación del usuario actual si está autenticado
    puntuacion_usuario = None
    if current_user.is_authenticated:
        puntuacion_usuario = Puntuacion.find_by_usuario_and_transformer(
            srp, current_user.id, transformer_id
        )
    
    return render_template(
        'transformer_detail.html',
        transformer=transformer,
        comentarios=comentarios,
        puntuacion_promedio=puntuacion_promedio,
        puntuacion_usuario=puntuacion_usuario
    )

@transformers_bp.route('/transformer/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo = request.form.get('tipo')
        descripcion = request.form.get('descripcion')
        habilidades = request.form.get('habilidades')
        
        # Validaciones básicas
        if not nombre or not tipo or not descripcion:
            flash('Los campos Nombre, Tipo y Descripción son obligatorios', 'danger')
            return render_template('create_transformer.html')
        
        # Procesar imagen si se proporciona
        imagen_url = ''
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generar nombre único para evitar colisiones
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                imagen_url = f"/{file_path}"  # Ruta relativa para la URL
        
        # Crear y guardar el nuevo transformer
        transformer = Transformer(
            nombre=nombre,
            tipo=tipo,
            descripcion=descripcion,
            habilidades=habilidades,
            imagen_url=imagen_url,
            creador_id=current_user.id
        )
        transformer.save(srp)
        
        flash('Transformer creado exitosamente', 'success')
        return redirect(url_for('transformers.detail', transformer_id=transformer.id))
    
    return render_template('create_transformer.html')

@transformers_bp.route('/transformer/<transformer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(transformer_id):
    transformer = Transformer.find(srp, transformer_id)
    if not transformer:
        flash('Transformer no encontrado', 'danger')
        return redirect(url_for('transformers.index'))
    
    # Verificar que el usuario actual es el creador o un administrador
    if transformer.creador_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para editar este Transformer', 'danger')
        return redirect(url_for('transformers.detail', transformer_id=transformer_id))
    
    if request.method == 'POST':
        transformer.nombre = request.form.get('nombre')
        transformer.tipo = request.form.get('tipo')
        transformer.descripcion = request.form.get('descripcion')
        transformer.habilidades = request.form.get('habilidades')
        
        # Procesar imagen si se proporciona una nueva
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generar nombre único para evitar colisiones
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                transformer.imagen_url = f"/{file_path}"  # Ruta relativa para la URL
        
        transformer.save(srp)
        flash('Transformer actualizado exitosamente', 'success')
        return redirect(url_for('transformers.detail', transformer_id=transformer.id))
    
    return render_template('edit_transformer.html', transformer=transformer)

@transformers_bp.route('/transformer/<transformer_id>/delete', methods=['POST'])
@login_required
def delete(transformer_id):
    transformer = Transformer.find(srp, transformer_id)
    if not transformer:
        flash('Transformer no encontrado', 'danger')
        return redirect(url_for('transformers.index'))
    
    # Verificar que el usuario actual es el creador o un administrador
    if transformer.creador_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para eliminar este Transformer', 'danger')
        return redirect(url_for('transformers.detail', transformer_id=transformer_id))
    
    # Marcar comentarios relacionados como eliminados
    comentarios = Comentario.find_by_transformer(srp, transformer_id)
    for comentario in comentarios:
        comentario.eliminar(srp)
    
    # Marcar puntuaciones relacionadas como eliminadas
    puntuaciones = Puntuacion.find_by_transformer(srp, transformer_id)
    for puntuacion in puntuaciones:
        puntuacion.eliminar(srp)
    
    # Marcar el transformer como eliminado
    if transformer.eliminar(srp):
        flash('Transformer eliminado exitosamente', 'success')
    else:
        flash('Hubo un problema al eliminar el Transformer', 'danger')
    
    return redirect(url_for('transformers.index')) 