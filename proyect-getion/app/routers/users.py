from fastapi import APIRouter, HTTPException, status, Request
from models.usuario import Usuario, UsuarioDB
from schemas.usuario import  usuario_schema_db
from db.conexion import get_connection, close_connection
from routers.gestores import current_me

from mysql.connector import Error


# Define un router con el prefijo "/users" y un tag para la API
router = APIRouter(prefix="/users", 
                   tags=["users"],
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

# Verifica si un usuario está asociado a una empresa
async def search_usuario_empresa(id_persona, nombre_empresa):
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT id_usuario_empresa FROM `usuarioempresa` ue 
                       JOIN `empresa` e ON ue.id_empresa = e.id_empresa 
                       WHERE e.nombre = %s AND ue.id_person = %s"""
            cursor.execute(query, (nombre_empresa, id_persona))
            result = cursor.fetchone()
            
            if result:
                return False  # El usuario ya está asociado a la empresa
            else:
                return True  # El usuario no está asociado a la empresa

        except Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al buscar el usuario")

        finally:
            close_connection(conn)  # Asegura que la conexión se cierre

# Inserta una asociación entre un usuario y una empresa
async def insert_usuario_empresa(nombre_empresa, id_person):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO `usuarioempresa`(`id_person`, `id_empresa`) 
                SELECT %s, id_empresa 
                FROM `empresa` 
                WHERE nombre = %s
            """
            cursor.execute(query, (id_person, nombre_empresa))
            conn.commit()
        except Error as e:
            conn.rollback()  # Deshacer la transacción en caso de error
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"No se pudo crear la relación entre la empresa y el usuario: {str(e)}")
        finally:
            cursor.close()
            close_connection(conn)  # Asegura que la conexión se cierre

# Elimina la asociación entre un usuario y una empresa
async def del_user(id: int):
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor()
            query = """
                DELETE FROM `usuarioempresa` WHERE id_person = %s
            """
            cursor.execute(query, (id,))
            conn.commit()
        except Error as e:
            conn.rollback()  # Deshacer la transacción en caso de error
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"No se pudo eliminar la relación entre la empresa y el usuario: {str(e)}")
        finally:
            cursor.close()
            close_connection(conn)  # Asegura que la conexión se cierre

# Endpoint para obtener las empresas asociadas a una gestión
@router.get("/getEmpresas-usuarios/{id_gestion}")
async def get_empresas_usuarios(id_gestion: int):
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT e.nombre FROM `empresa` e 
                       JOIN `gestionempresas` g ON e.id_empresa = g.id_empresa 
                       WHERE g.id_gestion = %s"""
            cursor.execute(query, (id_gestion,))
            empresas = [row['nombre'] for row in cursor.fetchall()]  # Obtiene los nombres de las empresas
            
            return {"empresas": empresas} 
                
        except Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al buscar las empresas para el usuario")
        finally:
            close_connection(conn)  # Asegura que la conexión se cierre

# Endpoint para crear un nuevo usuario y asociarlo a una empresa
@router.post("/crearUsuario/{id_gestion}", status_code=status.HTTP_201_CREATED)
async def crear_usuario(id_gestion: int, usuario: UsuarioDB):
    user = search_usuario(usuario.dni, usuario.email, usuario.nombre_usuario)

    if type(user) != Usuario:
        conn = get_connection()

        if conn:
            try:
                cursor = conn.cursor()
                cursor.callproc("AddUsuario", (usuario.nombre, usuario.apellidos, usuario.dni, usuario.email, usuario.nombre_usuario))
                conn.commit()

                # Obtener el ID de la persona recién insertada
                for result in cursor.stored_results():
                    user_id = result.fetchone()[0]
                
                cursor.close()
            except Error as e:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"No se pudo crear el usuario: {str(e)}")
            finally:
                close_connection(conn)
    else:
        user_id = user.id_person

    if (await search_usuario_empresa(user_id, usuario.user_company)):
        await insert_usuario_empresa(usuario.user_company, user_id)
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya está asociado a la empresa")

# Endpoint para eliminar múltiples usuarios
@router.post("/eliminar", status_code=status.HTTP_200_OK)
async def del_usuarios(request: Request):
    ids = await request.json()
    users_ids = ids.get("ids", [])

    for id in users_ids:
        await del_user(id)
