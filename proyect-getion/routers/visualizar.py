from fastapi import APIRouter, HTTPException, status, Depends
from models.usuario import Usuario, UsuarioDB
from models.gestor import Gestor
from schemas.usuario import usuario_schema, usuario_schema_db
from db.conexion import get_connection, close_connection
from routers.gestores import current_me
from mysql.connector import Error

# Define un router con el prefijo "/detalles" y un tag para la API
router = APIRouter(prefix="/detalles", 
                   tags=["detalles"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found in database"}})

# Busca un usuario en la base de datos por DNI, email o nombre de usuario
def search_usuario(dni: str, email: str, nombre_usuario: str) -> Usuario:
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT * FROM `usuario` u 
                       JOIN `persona` p ON p.id_person = u.id_person 
                       WHERE p.dni = %s OR p.email = %s OR u.nombre_usuario = %s"""
            cursor.execute(query, (dni, email, nombre_usuario))
            result = cursor.fetchone()
            
            if result:
                return Usuario(**usuario_schema_db(result))  # Convierte el resultado en una instancia de Usuario
            else:
                return None
                # Alternativamente, podrías descomentar la línea siguiente para levantar una excepción si no se encuentra el usuario
                # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el usuario en la base de datos")

        except Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al buscar el usuario")

        finally:
            close_connection(conn)  # Asegura que la conexión se cierre

# Obtiene los usuarios asociados a una gestión específica
@router.get('/get_usuarios/{id_gestion}', status_code=status.HTTP_200_OK)
async def get_usuarios(id_gestion: int, current_gestor: Gestor = Depends(current_me)):
    conn = get_connection()
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("GetUsuariosPorGestion", (id_gestion,))
            
            usuarios = []
            for result in cursor.stored_results():
                rows = result.fetchall()

                if rows:
                    usuarios.extend(rows)  # Usa extend para añadir los elementos individuales a `usuarios`
            conn.close()
            
            if usuarios:
                return usuarios
            return []
        except Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los usuarios: {str(e)}")
        finally:
            close_connection(conn)  # Asegura que la conexión se cierre

# Crea un nuevo usuario en la base de datos
@router.get("/crearUsuario", status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: UsuarioDB):
    if type(search_usuario(usuario.dni, usuario.email, usuario.nombre_usuario)) != Usuario:
        conn = get_connection()

        if conn:
            try:
                cursor = conn.cursor()
                cursor.callproc("AddUsuario", (usuario.nombre, usuario.apellidos, usuario.dni, usuario.email, usuario.nombre_usuario))
                conn.commit()
                cursor.close()
            except Error as e:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No se pudo crear el usuario")
            finally:
                close_connection(conn)  # Asegura que la conexión se cierre
    
# Obtiene los usuarios asociados a una empresa específica dentro de una gestión
@router.get("/get_usuarios_empresa/{id_gestion}/{nombre_empresa}", status_code=status.HTTP_200_OK)
async def get_usuarios_by_empresa(id_gestion: int, nombre_empresa: str):
    conn = get_connection()
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("GetUsuariosPorGestionEmpresa", (id_gestion, nombre_empresa))
            
            usuarios = []
            for result in cursor.stored_results():
                rows = result.fetchall()

                if rows:
                    usuarios.extend(rows)  # Usa extend para añadir los elementos individuales a `usuarios`
            conn.close()
            
            if usuarios:
                return usuarios
            return []
        except Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener los usuarios: {str(e)}")
        finally:
            close_connection(conn)  # Asegura que la conexión se cierre
