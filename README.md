# Gestión de Usuarios - Proyecto de Práctica

Este proyecto personal está diseñado para practicar y mejorar mis habilidades de desarrollo web, enfocándose en la gestión de usuarios. Implementa funcionalidades básicas y avanzadas como la creación, edición y eliminación de perfiles, con un énfasis en la seguridad de datos.  Integra diversas tecnologías y herramientas para comprender mejor los flujos de trabajo completos.


## Características del Proyecto

* **Gestión de Usuarios:** Creación, edición y eliminación de usuarios.
* **Validación de Tokens:** Sistema de autenticación mediante JWT (JSON Web Tokens) para proteger las rutas sensibles.
* **Búsqueda Dinámica:** Búsqueda por ID, nombre y empresa.
* **Seguridad Básica:**  Implementación de medidas de seguridad como validación de tokens y verificación de autenticidad.
* **Soporte para Acciones Masivas:** Selección múltiple de usuarios para eliminación o actualización.
* **Integración de Base de Datos:**  MySQL para gestionar la información de usuarios.


## Tecnologías Utilizadas

* **Frontend:** HTML5, CSS3, JavaScript (ES6+)
* **Backend:** Python (FastAPI)
* **Base de Datos:** MySQL
* **Autenticación:** JWT (JSON Web Tokens)
* **Otros:** SQL


## Instalación

1. **Clona el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   ```

2. **Instala las dependencias del backend:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura la base de datos:**
   * Crea una base de datos MySQL local llamada `gestion_usuarios`.
   * Configura tus credenciales de MySQL en el archivo de configuración (especificar el archivo).

4. **Ejecuta el servidor:**
   ```bash
   uvicorn app:app --reload
   ```
   Esto lanzará el servidor FastAPI en `http://127.0.0.1:8000`.

5. **Accede a la aplicación:** Abre `http://127.0.0.1:8000` en tu navegador.


## Uso

* **Pantalla de Inicio:** Navegación a las secciones de Usuarios y Gestión de Empresas.
* **Gestión de Usuarios:** Agregar, editar, eliminar usuarios y buscar por filtros.
* **Gestión de Empresas:** (Describir brevemente la funcionalidad)
* **Acciones Masivas:** Realizar acciones sobre múltiples usuarios seleccionados.


## Funcionalidades Futuras

* Mejora de la seguridad con roles de usuario.
* Optimización de consultas SQL y mejoras de rendimiento.
* Integración con un sistema de notificaciones.
* Soporte para más idiomas.


## Contribución

Este proyecto es personal y está orientado al aprendizaje.  Las contribuciones son bienvenidas.  Realiza un fork del repositorio y envía un pull request con tus sugerencias o mejoras.


## Licencia

Este proyecto está bajo la Licencia MIT.
