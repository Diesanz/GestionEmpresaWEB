Gestión de Usuarios - Proyecto de Práctica
Este es un proyecto personal diseñado para practicar y mejorar mis habilidades de desarrollo web, centrado en la gestión de usuarios. Aquí implemento funcionalidades básicas y avanzadas como creación, edición, eliminación de perfiles y seguridad de datos. Además, integro tecnologías y herramientas para entender mejor los flujos de trabajo completos.

Características del Proyecto
Gestión de Usuarios: Permite la creación, edición y eliminación de usuarios.
Validación de Tokens: Se incluye un sistema de autenticación mediante tokens para proteger las rutas sensibles.
Búsqueda Dinámica: Funcionalidad de búsqueda por ID, nombre y empresa para facilitar la administración de usuarios.
Seguridad Básica: Implementación de medidas iniciales de seguridad como validación de tokens y verificación de autenticidad.
Soporte para Acciones Masivas: Capacidad para seleccionar múltiples usuarios y realizar acciones como eliminación o actualización.
Integración de Base de Datos: Se utiliza una base de datos relacional (MySQL) para gestionar la información de los usuarios y las gestiones.
Tecnologías Utilizadas
Frontend: HTML5, CSS3, JavaScript (ES6+)
Backend: Python (FastAPI)
Base de Datos: MySQL
Autenticación: JWT (JSON Web Tokens) para la validación de usuarios
Otros: SQL para gestión de datos, transacciones y consultas complejas

Instalación
Clona el repositorio

Instala las dependencias del backend:
Desde la carpeta del proyecto, ejecuta:
pip install -r requirements.txt

Configura la base de datos:
Crea una base de datos MySQL local llamada gestion_usuarios.
Configura tus credenciales de MySQL en el archivo de configuración.

Ejecuta el servidor:
uvicorn app:app --reload
Esto lanzará el servidor FastAPI en http://127.0.0.1:8000.

Accede a la aplicación en el navegador:
Abre http://127.0.0.1:8000 para comenzar a interactuar con la aplicación.

Uso
Pantalla de Inicio: Desde aquí puedes navegar a las secciones de "Usuarios" y "Gestión de Empresas".
Gestión de Usuarios: Permite agregar, editar y eliminar usuarios. También incluye funcionalidades de búsqueda por distintos filtros.
Gestión de Empresas: Crea y asocia empresas a gestiones específicas.
Acciones Masivas: Selecciona varios usuarios y realiza acciones sobre ellos.
Funcionalidades Futuras
Mejora de la seguridad con roles de usuario.
Optimización de consultas SQL y mejoras de rendimiento.
Integración con un sistema de notificaciones.
Soporte para más idiomas.
Contribución
Este proyecto es personal y está orientado al aprendizaje, pero si te interesa contribuir, ¡eres bienvenido! Puedes realizar un fork del repositorio y enviar un pull request con tus sugerencias o mejoras.

Licencia
Este proyecto está bajo la Licencia MIT.
