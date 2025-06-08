# TransformerDex

TransformerDex es una aplicación web desarrollada con Flask que permite a los usuarios gestionar una base de datos de Transformers. Los usuarios pueden crear, editar, puntuar y comentar diferentes modelos de Transformers, así como visualizar los creados por otros usuarios.

## Requisitos

- Python 3.7+
- Redis Server
- Dependencias de Python (ver `requirements.txt`)

## Instalación

1. Clonar el repositorio:

```bash
git clone <url-del-repositorio>
cd ProyectoALS
```

2. Crear y activar un entorno virtual (opcional pero recomendado):

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

4. Asegurarse de que Redis está instalado y en ejecución:

```bash
# Verificar que Redis está en ejecución
redis-cli ping
# Debería responder con "PONG"
```

5. Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
SECRET_KEY=tu_clave_secreta_aqui
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Ejecución

Para iniciar la aplicación:

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`.

## Estructura del Proyecto

- `app.py`: Punto de entrada de la aplicación
- `extensions.py`: Configuración de extensiones (Sirope, Flask-Login, etc.)
- `rutas/`: Controladores de la aplicación
- `modelos/`: Definición de las entidades de negocio
- `templates/`: Plantillas HTML
- `static/`: Recursos estáticos (CSS, imágenes, etc.)
- `documentacion_transformerdex.txt`: Documentación completa del sistema

## Características

- Gestión completa de Transformers (CRUD)
- Sistema de comentarios
- Sistema de puntuaciones (1-5 estrellas)
- Autenticación de usuarios
- Subida de imágenes
- Soft delete para mantener integridad de datos

## Herramientas de Mantenimiento

- El primer usuario creado será el administrador. Recomendable usar algo sencillo como Usuario: admin Contraseña: admin para probar el proyecto.

- `reset_database.py`: Script para vaciar la base de datos

## Documentación

Para una documentación completa del sistema, consultar el archivo `documentacion_transformerdex.pdf`.

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT. 