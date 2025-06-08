from datetime import datetime

class Puntuacion:
    def __init__(self, valor, usuario_id, transformer_id):
        self.valor = valor  # Valor de 1 a 5
        self.usuario_id = usuario_id
        self.transformer_id = transformer_id
        self.fecha_creacion = datetime.now()
        self.eliminado = False  # Nuevo campo para marcar si está eliminado
        self._id = None
        self._id_str = None
    
    @property
    def id(self):
        """Devuelve el ID de la puntuación como string"""
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
        """Guardar la puntuación en la base de datos"""
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
        Marca la puntuación como eliminada en lugar de eliminarla físicamente
        """
        self.eliminado = True
        self.save(srp)
        print(f"Puntuación marcada como eliminada: {self._id}")
        return True
    
    def delete(self, srp):
        """Método antiguo para mantener compatibilidad"""
        return self.eliminar(srp)
    
    @staticmethod
    def find(srp, puntuacion_id):
        """Encontrar una puntuación por su ID"""
        puntuaciones = list(srp.load_all(Puntuacion))
        
        # Buscar por _id_str
        for p in puntuaciones:
            if hasattr(p, '_id_str') and p._id_str == puntuacion_id:
                return p
                
        # Buscar por conversión directa de ID
        for p in puntuaciones:
            if str(p._id) == str(puntuacion_id):
                return p
                
        return None
    
    @staticmethod
    def find_by_transformer(srp, transformer_id):
        """Encontrar puntuaciones para un transformer específico"""
        puntuaciones = list(srp.load_all(Puntuacion))
        # Filtrar solo puntuaciones no eliminadas
        return [p for p in puntuaciones if str(p.transformer_id) == str(transformer_id) and 
                (not hasattr(p, 'eliminado') or not p.eliminado)]
    
    @staticmethod
    def find_by_usuario(srp, usuario_id):
        """Encontrar puntuaciones hechas por un usuario específico"""
        puntuaciones = list(srp.load_all(Puntuacion))
        # Filtrar solo puntuaciones no eliminadas
        return [p for p in puntuaciones if str(p.usuario_id) == str(usuario_id) and 
                (not hasattr(p, 'eliminado') or not p.eliminado)]
    
    @staticmethod
    def find_by_usuario_and_transformer(srp, usuario_id, transformer_id):
        """Encontrar la puntuación de un usuario para un transformer específico"""
        puntuaciones = list(srp.load_all(Puntuacion))
        for p in puntuaciones:
            if (str(p.usuario_id) == str(usuario_id) and 
                str(p.transformer_id) == str(transformer_id) and
                (not hasattr(p, 'eliminado') or not p.eliminado)):
                return p
        return None
    
    @staticmethod
    def calcular_promedio(srp, transformer_id):
        """Calcular la puntuación promedio para un transformer"""
        puntuaciones = Puntuacion.find_by_transformer(srp, transformer_id)
        if not puntuaciones:
            return 0
        
        total = sum(p.valor for p in puntuaciones)
        return round(total / len(puntuaciones), 1) 