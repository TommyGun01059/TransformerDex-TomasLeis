#!/usr/bin/env python
"""
Script para vaciar completamente la base de datos Redis.
Esto eliminará todos los datos de TransformerDex.
"""

import redis
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def reset_database():
    """Vaciar completamente la base de datos Redis"""
    
    # Configuración de Redis (por defecto localhost:6379)
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_db = int(os.getenv('REDIS_DB', 0))
    
    # Conectar a Redis
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True
    )
    
    try:
        # Verificar la conexión
        r.ping()
        print("Conexión a Redis establecida correctamente.")
        
        # Obtener todas las claves
        keys = r.keys("*")
        total_keys = len(keys)
        
        if total_keys == 0:
            print("La base de datos ya está vacía. No hay claves para eliminar.")
            return
        
        # Mostrar información antes de eliminar
        print(f"Se encontraron {total_keys} claves en la base de datos.")
        
        # Confirmar la eliminación
        confirmation = input(f"¿Estás seguro de que quieres eliminar TODAS las claves de la base de datos? (s/n): ")
        
        if confirmation.lower() != 's':
            print("Operación cancelada.")
            return
        
        # Eliminar todas las claves
        deleted = r.delete(*keys)
        
        print(f"Se han eliminado {deleted} claves de la base de datos.")
        print("La base de datos ha sido vaciada correctamente.")
        
    except redis.ConnectionError:
        print("Error: No se pudo conectar a Redis. Verifica que el servidor Redis esté en ejecución.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    print("=== RESET DE BASE DE DATOS DE TRANSFORMERDEX ===")
    print("¡ADVERTENCIA! Este script eliminará TODOS los datos de la aplicación.")
    reset_database() 