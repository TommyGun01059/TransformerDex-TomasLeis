from datetime import datetime

class Comentario:
    def __init__(self, texto, usuario_id, transformer_id):
        self.texto = texto
        self.usuario_id = usuario_id
        self.transformer_id = transformer_id
        self.fecha_creacion = datetime.now()
        self.eliminado = False  # Nuevo campo para marcar si está eliminado
        self._id = None
        self._id_str = None
    
    @property
    def id(self):
        """Devuelve el ID del comentario como string"""
        if hasattr(self, '_id_str') and self._id_str:
            return self._id_str
            
        if self._id:
            if isinstance(self._id, str):
                return self._id
            elif hasattr(self._id, 'bytes'):
                self._id_str = self._id.bytes.hex()
                return self._id_str
            
        return str(self._id) if self._id else None
    
    def save(self, srp):
        """Guardar el comentario en la base de datos"""
        if not self._id:
            self._id = srp.save(self)
            # Guardar la representación en string del ID
            if hasattr(self._id, 'bytes'):
                self._id_str = self._id.bytes.hex()
            srp.save(self)  # Guardar de nuevo para actualizar el _id_str
        else:
            srp.save(self)
        return self
    
    def eliminar(self, srp):
        """
        Marca el comentario como eliminado en lugar de eliminarlo físicamente
        """
        self.eliminado = True
        self.save(srp)
        print(f"Comentario marcado como eliminado: {self._id}")
        return True
    
    def delete(self, srp):
        """Método antiguo para mantener compatibilidad"""
        return self.eliminar(srp)
    
    @staticmethod
    def find(srp, comentario_id):
        """Encontrar un comentario por su ID"""
        comentarios = list(srp.load_all(Comentario))
        
        # Caso especial para IDs en formato "modelos.comentario.Comentario@0"
        if comentario_id.startswith("modelos.comentario.Comentario@"):
            # Extraer el número después del @
            num_part = comentario_id.split('@')[-1]
            for c in comentarios:
                # Comparar con el formato esperado
                if str(c._id) == num_part or str(c._id) == comentario_id:
                    return c
        
        # Buscar por _id_str
        for c in comentarios:
            if hasattr(c, '_id_str') and c._id_str == comentario_id:
                return c
                
        # Buscar por conversión directa de ID
        for c in comentarios:
            if str(c._id) == str(comentario_id):
                return c
                
        # Última opción: buscar comentarios por índice
        # Si hay comentarios y el ID parece ser un índice numérico
        if comentarios and comentario_id.isdigit():
            idx = int(comentario_id)
            if idx < len(comentarios):
                return comentarios[idx]
                
        return None
    
    @staticmethod
    def find_by_transformer(srp, transformer_id):
        """Encontrar comentarios para un transformer específico"""
        comentarios = list(srp.load_all(Comentario))
        
        # Filtrar solo comentarios válidos que tengan todos los atributos necesarios
        # y que no estén marcados como eliminados
        comentarios_validos = []
        for c in comentarios:
            if (hasattr(c, 'texto') and 
                hasattr(c, 'usuario_id') and 
                hasattr(c, 'transformer_id') and 
                hasattr(c, 'fecha_creacion')):
                
                # Verificar si el comentario está eliminado
                if not hasattr(c, 'eliminado') or not c.eliminado:
                    # Verificar que el transformer_id coincide
                    if str(c.transformer_id) == str(transformer_id):
                        comentarios_validos.append(c)
        
        return comentarios_validos
    
    @staticmethod
    def find_by_usuario(srp, usuario_id):
        """Encontrar comentarios hechos por un usuario específico"""
        comentarios = list(srp.load_all(Comentario))
        # Filtrar solo comentarios no eliminados
        return [c for c in comentarios if str(c.usuario_id) == str(usuario_id) and 
                (not hasattr(c, 'eliminado') or not c.eliminado)]
    
    @staticmethod
    def force_delete(srp, comentario_id):
        """
        Método agresivo para forzar la eliminación de un comentario directamente de Redis
        """
        print(f"Forzando eliminación del comentario: {comentario_id}")
        deleted = False
        
        # Intentar encontrar el comentario primero
        comentario = Comentario.find(srp, comentario_id)
        if comentario:
            # Intentar el método normal primero
            try:
                comentario.delete(srp)
                deleted = True
            except Exception as e:
                print(f"Error en eliminación normal: {e}")
        
        # Buscar y eliminar todas las claves que puedan estar relacionadas con este comentario
        if hasattr(srp, '_redis'):
            # Obtener todas las claves de Redis
            all_keys = srp._redis.keys("*")
            deleted_keys = 0
            
            # Patrones para identificar comentarios
            patterns = [
                f"*{comentario_id}*",
                "*comentario*",
                "*Comentario@*"
            ]
            
            # Método 1: Buscar por patrones específicos
            for pattern in patterns:
                try:
                    keys = srp._redis.keys(pattern)
                    for key in keys:
                        if isinstance(key, bytes):
                            key = key.decode('utf-8')
                        
                        # Verificar si la clave parece ser el comentario que buscamos
                        if "comentario" in key.lower() or "Comentario" in key:
                            # Si tenemos el comentario, verificar si es el correcto
                            if comentario_id in key or (comentario and str(comentario._id) in key):
                                result = srp._redis.delete(key)
                                if result > 0:
                                    print(f"Eliminada clave: {key}")
                                    deleted_keys += 1
                                    deleted = True
                except Exception as e:
                    print(f"Error al buscar/eliminar con patrón {pattern}: {e}")
            
            # Método 2: Examinar todas las claves y buscar contenido relacionado con comentarios
            if not deleted:
                for key in all_keys:
                    try:
                        if isinstance(key, bytes):
                            key_str = key.decode('utf-8')
                        else:
                            key_str = str(key)
                        
                        # Si la clave parece ser un comentario
                        if "comentario" in key_str.lower() or "Comentario" in key_str:
                            # Obtener el valor para verificar
                            try:
                                value = srp._redis.get(key)
                                if value:
                                    # Eliminar la clave si parece ser un comentario
                                    srp._redis.delete(key)
                                    print(f"Eliminada clave por contenido: {key_str}")
                                    deleted_keys += 1
                                    deleted = True
                            except:
                                # Si no podemos obtener el valor, intentamos eliminar de todos modos
                                srp._redis.delete(key)
                    except Exception as e:
                        print(f"Error procesando clave {key}: {e}")
            
            print(f"Total de claves eliminadas: {deleted_keys}")
            
            # Método 3: Eliminar directamente usando la clave exacta si la conocemos
            if comentario and hasattr(comentario, '_id'):
                try:
                    exact_key = f"sirope:{comentario._id}"
                    result = srp._redis.delete(exact_key)
                    if result > 0:
                        print(f"Eliminada clave exacta: {exact_key}")
                        deleted = True
                except Exception as e:
                    print(f"Error al eliminar clave exacta: {e}")
        
        # Verificar si aún existe el comentario
        comentario_verificacion = Comentario.find(srp, comentario_id)
        if comentario_verificacion is None:
            deleted = True
            
        return deleted 