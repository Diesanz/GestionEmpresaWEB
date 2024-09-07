from fastapi import APIRouter, HTTPException, status, Depends
from models.gestion import Gestion, Gestion_Empresas
from models.gestor import Gestor
from schemas.gestion import gestion_schema, gestion_empresas_schema
from db.conexion import get_connection, close_connection
from routers.gestores import current_me
from mysql.connector import Error
from typing import List

# Define un router con el prefijo "/gestiones" y un tag para la API
router = APIRouter(prefix="/gestiones", 
                   tags=["gestiones"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found in database"}})

# Función para buscar una gestión por nombre, descripción e ID de persona
def search_gestion(nombre: str, desc: str, id: int ) -> Gestion:
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT g.id_gestion, g.descripcion, g.fecha_creacion, g.nombre_gestion FROM 
                        `gestion` g  JOIN `gestionar` ge ON ge.id_gestion = g.id_gestion WHERE (nombre_gestion = %s OR descripcion = %s) AND ge.id_person = %s"""
            cursor.execute(query, (nombre, desc, id))
            result = cursor.fetchone()
            if result:
                return Gestion(**gestion_schema(result))  # Convierte el resultado en una instancia de Gestion
        except Error as e:
            return None
        finally:
            close_connection(conn)  # Asegura que la conexión se cierre

# Función para añadir una empresa a una gestión
def add_empresa(empresa: str, gestion_id: int, id_person: int ) -> bool:
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.callproc("InsertGestionEmpresas", (empresa, gestion_id, id_person))
            conn.commit()
        except Error as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"Error general al insertar gestion empresa: {str(e)}")
        finally:
            close_connection(conn)
    
    return True

# Función asíncrona para obtener las empresas asociadas a una gestión
async def get_empresas(id_gestion: int):
    conn = get_connection()

    empresas = []  
    
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """SELECT id_empresa FROM `gestionempresas` WHERE id_gestion = %s """
            cursor.execute(query, (id_gestion,))
            
            for row in cursor.fetchall():
                empresas.append(row['id_empresa'])
            
            return empresas 
                
        except Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"Error al buscar las empresas: {str(e)}")
        finally:
            if conn:
                close_connection(conn)  # Asegura que la conexión se cierre

# Función para eliminar una gestión
def delete_gestion(gestion_id: int):
    conn = get_connection()
    
    if conn:    
        try:
            cursor = conn.cursor()
            cursor.callproc("DeleteGestion", (gestion_id,))
            affected_rows = cursor.rowcount  # Número de filas afectadas
            
            conn.commit()
            cursor.close()
            
            if affected_rows == 0:
                return False  # No se eliminaron filas
            
            return True

        except Error as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"Error general al eliminar gestion: {str(e)}")
        finally:
            close_connection(conn)

    return False  # No se pudo abrir la conexión

# Función asíncrona para eliminar empresas asociadas a una gestión
async def delete_empresas(empresas_id: int) -> bool:
    conn = get_connection()

    if conn:
        try:
            with conn.cursor() as cursor:
                # Elimina las relaciones de empresas
                query = """DELETE FROM `gestorEmpresas` WHERE id_empresa = %s"""
                cursor.execute(query, (empresas_id,))

                query1 = """DELETE FROM `usuarioempresa` WHERE id_empresa = %s"""
                cursor.execute(query1, (empresas_id,))

                query2 = """DELETE FROM `empresa` WHERE id_empresa = %s"""
                cursor.execute(query2, (empresas_id,))

            conn.commit()  # Confirma la transacción
            return True  # Operación exitosa

        except Error as e:
            conn.rollback()  # Realiza rollback en caso de error
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Error general al eliminar las empresas: {str(e)}"
            )
        finally:
            close_connection(conn)

    return False  # No se pudo abrir la conexión

# Endpoint para crear una nueva gestión
@router.post("/crear", status_code=status.HTTP_201_CREATED)
async def create_gestion(gestion: Gestion_Empresas, current_gestor: Gestor = Depends(current_me)):
    if type(search_gestion(gestion.nombre_gestion, gestion.descripcion, current_gestor.id_person)) == Gestion:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Gestion ya existente!")
    
    conn = get_connection()
    gestion_id = 0

    if conn:
        try:
            cursor = conn.cursor()
            cursor.callproc("AddGestion", (gestion.descripcion, gestion.nombre_gestion, current_gestor.id_person))
            for result in cursor.stored_results():
                gestion_id = result.fetchone()[0]
            conn.commit()
        except Error as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"Error general al insertar gestion: {str(e)}")
        finally:
            close_connection(conn)

    for empresa in gestion.empresas:
        if(add_empresa(empresa, gestion_id, current_gestor.id_person)):
            continue
        else:
            if(delete_gestion(gestion_id)):  # Si alguna empresa no se añade, borra la gestión completa
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="No se pudo crear la gestión debido a que algunas empresas ya están gestionadas")
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                    detail="Error!")

# Endpoint para visualizar gestiones del gestor actual
@router.get("/visualizar", response_model=List[Gestion], status_code=status.HTTP_202_ACCEPTED)
async def get_gestiones(current_gestor: Gestor = Depends(current_me)):
    conn = get_connection()
    gestiones = []

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("GetGestionesPorGestor", (current_gestor.id_person,))
            
            for result in cursor.stored_results():
                gestiones = result.fetchall()
        except Error as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                detail=f"Error al buscar gestiones: {str(e)}")
        finally:
            close_connection(conn)
    
    return gestiones

# Endpoint para eliminar una gestión por ID
@router.delete("/borrar/{gestion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gestion_by_id(gestion_id: int, current_gestor: Gestor = Depends(current_me)):
    empresas = await get_empresas(gestion_id)
    
    if not empresas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron empresas para la gestión.")
    
    gestion_eliminada = delete_gestion(gestion_id)

    if not gestion_eliminada:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo eliminar la gestión.")
    
    for empresa in empresas:
        await delete_empresas(empresa)
    
    return {"message": "Gestión eliminada con éxito"}

# Endpoint para actualizar una gestión existente
@router.put("/modificar/{gestion_id}", status_code=status.HTTP_201_CREATED)
async def update_gestion(gestion: Gestion, gestion_id: int, current_gestor: Gestor = Depends(current_me)):
    if type(search_gestion(gestion.nombre_gestion, gestion.descripcion, current_gestor.id_person)) == Gestion:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
                            detail="Ya existe una gestión con ese nombre/descripción!")
    
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.callproc("UpdateGestion", (gestion_id, gestion.nombre_gestion, gestion.descripcion, current_gestor.id_person))
            conn.commit()
        except Error as e:
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f"No modificado: {str(e)}")
        finally:
            close_connection(conn)
    
    return True
