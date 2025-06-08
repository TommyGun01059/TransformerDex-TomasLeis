from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import srp
from modelos.comentario import Comentario
from modelos.transformer import Transformer

comentarios_bp = Blueprint('comentarios', __name__)

@comentarios_bp.route('/transformer/<transformer_id>/comentario', methods=['POST'])
@login_required
def create(transformer_id):
    transformer = Transformer.find(srp, transformer_id)
    if not transformer:
        flash('Transformer no encontrado', 'danger')
        return redirect(url_for('transformers.index'))
    
    texto = request.form.get('texto')
    if not texto:
        flash('El comentario no puede estar vacío', 'danger')
        return redirect(url_for('transformers.detail', transformer_id=transformer_id))
    
    comentario = Comentario(
        texto=texto,
        usuario_id=current_user.id,
        transformer_id=transformer_id
    )
    comentario.save(srp)
    
    flash('Comentario añadido exitosamente', 'success')
    return redirect(url_for('transformers.detail', transformer_id=transformer_id))

@comentarios_bp.route('/comentario/<comentario_id>/delete', methods=['POST'])
@login_required
def delete(comentario_id):
    print(f"Intentando marcar como eliminado el comentario con ID: {comentario_id}")
    
    # Buscar el comentario específico
    comentario = Comentario.find(srp, comentario_id)
    if not comentario:
        flash('Comentario no encontrado', 'danger')
        return redirect(url_for('transformers.index'))
    
    # Verificar que el usuario actual es el autor o un administrador
    if comentario.usuario_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para eliminar este comentario', 'danger')
        return redirect(url_for('transformers.detail', transformer_id=comentario.transformer_id))
    
    transformer_id = comentario.transformer_id
    
    # Marcar el comentario como eliminado
    if comentario.eliminar(srp):
        flash('Comentario eliminado exitosamente', 'success')
    else:
        flash('No se pudo eliminar el comentario', 'danger')
    
    return redirect(url_for('transformers.detail', transformer_id=transformer_id)) 