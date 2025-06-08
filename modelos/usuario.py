from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class Usuario(UserMixin):
    def __init__(self, username, email, password=None, password_hash=None, is_admin=False):
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.fecha_registro = datetime.now()
        self._id = None
        self._id_str = None
        
        # Si se proporciona una contraseña en texto plano, la hasheamos
        if password:
            self.password_hash = generate_password_hash(password)
        # Si se proporciona un hash directamente, lo usamos
        elif password_hash:
            self.password_hash = password_hash
    
    @property
    def id(self):
        """Devuelve el ID del usuario como string"""
        if hasattr(self, '_id_str') and self._id_str:
            return self._id_str
            
        if self._id:
            if isinstance(self._id, str):
                return self._id
            elif hasattr(self._id, 'bytes'):
                self._id_str = self._id.bytes.hex()
                return self._id_str
            
        return str(self._id) if self._id else None
    
    def check_password(self, password):
        """Verificar si la contraseña proporcionada coincide con el hash almacenado"""
        return check_password_hash(self.password_hash, password)
    
    def save(self, srp):
        """Guardar el usuario en la base de datos"""
        if not self._id:
            self._id = srp.save(self)
            # Guardar la representación en string del ID
            if hasattr(self._id, 'bytes'):
                self._id_str = self._id.bytes.hex()
            srp.save(self)  # Guardar de nuevo para actualizar el _id_str
        else:
            srp.save(self)
        return self
    
    @staticmethod
    def find(srp, user_id):
        """Encontrar un usuario por su ID"""
        usuarios = list(srp.load_all(Usuario))
        
        # Buscar por _id_str
        for u in usuarios:
            if hasattr(u, '_id_str') and u._id_str == user_id:
                return u
                
        # Buscar por conversión directa de ID
        for u in usuarios:
            if str(u._id) == str(user_id):
                return u
                
        return None
    
    @staticmethod
    def find_by_username(srp, username):
        """Encontrar un usuario por su nombre de usuario"""
        usuarios = list(srp.load_all(Usuario))
        for u in usuarios:
            if u.username.lower() == username.lower():
                return u
        return None
    
    @staticmethod
    def find_by_email(srp, email):
        """Encontrar un usuario por su correo electrónico"""
        usuarios = list(srp.load_all(Usuario))
        for u in usuarios:
            if u.email.lower() == email.lower():
                return u
        return None 