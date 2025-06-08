from flask import Blueprint, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import srp
from modelos.puntuacion import Puntuacion
from modelos.transformer import Transformer

puntuaciones_bp = Blueprint('puntuaciones', __name__)

@puntuaciones_bp.route('/transformer/<transformer_id>/puntuacion', methods=['POST'])
@login_required
def create(transformer_id):
    transformer = Transformer.find(srp, transformer_id)
    if not transformer:
        flash('Transformer no encontrado', 'danger')
        return redirect(url_for('transformers.index'))
    
    try:
        valor = int(request.form.get('valor', 0))
        if valor < 1 or valor > 5:
            flash('La puntuación debe estar entre 1 y 5', 'danger')
            return redirect(url_for('transformers.detail', transformer_id=transformer_id))
    except ValueError:
        flash('La puntuación debe ser un número', 'danger')
        return redirect(url_for('transformers.detail', transformer_id=transformer_id))
    
    # Verificar si el usuario ya ha puntuado este transformer
    puntuacion_existente = Puntuacion.find_by_usuario_and_transformer(
        srp, current_user.id, transformer_id
    )
    
    if puntuacion_existente:
        # Actualizar puntuación existente
        puntuacion_existente.valor = valor
        puntuacion_existente.save(srp)
        flash('Puntuación actualizada exitosamente', 'success')
    else:
        # Crear nueva puntuación
        puntuacion = Puntuacion(
            valor=valor,
            usuario_id=current_user.id,
            transformer_id=transformer_id
        )
        puntuacion.save(srp)
        flash('Puntuación añadida exitosamente', 'success')
    
    return redirect(url_for('transformers.detail', transformer_id=transformer_id))

@puntuaciones_bp.route('/puntuacion/<puntuacion_id>/delete', methods=['POST'])
@login_required
def delete(puntuacion_id):
    puntuacion = Puntuacion.find(srp, puntuacion_id)
    if not puntuacion:
        flash('Puntuación no encontrada', 'danger')
        return redirect(url_for('transformers.index'))
    
    # Verificar que el usuario actual es el autor o un administrador
    if puntuacion.usuario_id != current_user.id and not current_user.is_admin:
        flash('No tienes permiso para eliminar esta puntuación', 'danger')
        return redirect(url_for('transformers.detail', transformer_id=puntuacion.transformer_id))
    
    transformer_id = puntuacion.transformer_id
    
    # Marcar la puntuación como eliminada
    if puntuacion.eliminar(srp):
        flash('Puntuación eliminada exitosamente', 'success')
    else:
        flash('Hubo un problema al eliminar la puntuación', 'danger')
    
    return redirect(url_for('transformers.detail', transformer_id=transformer_id)) 