from datetime import datetime

class Transformer:
    def __init__(self, nombre, tipo, descripcion, habilidades, imagen_url, creador_id):
        self.nombre = nombre
        self.tipo = tipo
        self.descripcion = descripcion
        self.habilidades = habilidades
        self.imagen_url = imagen_url
        self.creador_id = creador_id
        self.fecha_creacion = datetime.now()
        self.eliminado = False  # Nuevo campo para marcar si está eliminado
        self._id = None
        self._id_str = None
    
    @property
    def id(self):
        """Devuelve el ID del transformer como string"""
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
        """Guardar el transformer en la base de datos"""
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
        Marca el transformer como eliminado en lugar de eliminarlo físicamente
        """
        self.eliminado = True
        self.save(srp)
        print(f"Transformer marcado como eliminado: {self._id}")
        return True
    
    def delete(self, srp):
        """Método antiguo para mantener compatibilidad"""
        return self.eliminar(srp)
    
    @staticmethod
    def find(srp, transformer_id):
        """Encontrar un transformer por su ID"""
        transformers = list(srp.load_all(Transformer))
        
        # Buscar por _id_str
        for t in transformers:
            if hasattr(t, '_id_str') and t._id_str == transformer_id:
                return t
                
        # Buscar por conversión directa de ID
        for t in transformers:
            if str(t._id) == str(transformer_id):
                return t
                
        return None
    
    @staticmethod
    def find_all(srp):
        """Obtener todos los transformers no eliminados"""
        transformers = list(srp.load_all(Transformer))
        # Filtrar solo los transformers que no están eliminados
        return [t for t in transformers if not hasattr(t, 'eliminado') or not t.eliminado]
    
    @staticmethod
    def find_by_creador(srp, creador_id):
        """Encontrar transformers creados por un usuario específico"""
        transformers = list(srp.load_all(Transformer))
        # Filtrar solo transformers no eliminados
        return [t for t in transformers if str(t.creador_id) == str(creador_id) and 
                (not hasattr(t, 'eliminado') or not t.eliminado)]
    
    @staticmethod
    def find_by_tipo(srp, tipo):
        """Encontrar transformers por tipo"""
        transformers = list(srp.load_all(Transformer))
        # Filtrar solo transformers no eliminados
        return [t for t in transformers if t.tipo.lower() == tipo.lower() and 
                (not hasattr(t, 'eliminado') or not t.eliminado)] 