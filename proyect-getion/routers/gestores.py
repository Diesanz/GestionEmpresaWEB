import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status, Depends, Request
from models.gestor import Gestor, GestorDB
from schemas.gestor import gestor_schema, gestor_schema_db
from db.conexion import get_connection, close_connection
from common.secret import access_secret
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta
from mysql.connector import Error

# Carga las variables de entorno desde un archivo .env
load_dotenv()

# Lee las variables de entorno necesarias para la configuración de JWT
ALGORITHM = access_secret('my-secret', 'ALGORITHM')
SECRET = access_secret('my-secret', 'SECRET')
ACCESS_TOKEN_DURATION = int(access_secret('my-secret', 'ACCESS_TOKEN_DURATION'))

# Configura el contexto de cifrado para las contraseñas
crypt = CryptContext(schemes=["bcrypt"])

# Configura el esquema de seguridad OAuth2 con el endpoint de token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define un router con el prefijo "/gestores" y un tag para la API
router = APIRouter(prefix="/gestores", 
                   tags=["gestores"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

# Función para buscar un gestor en la base de datos por un campo y valor específicos
def search_gestor(field: str, value: str) -> Gestor:
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"""SELECT * FROM `gestor` g JOIN `persona` p ON p.id_person = g.id_person WHERE {field} = %s"""
            cursor.execute(query, (value,))
            result = cursor.fetchone()
            if result:
                return Gestor(**gestor_schema(result))  # Convierte el resultado en una instancia de Gestor
        except Error as e:
            return None
        finally:
            close_connection(conn)  # Asegura que la conexión se cierre

# Función para buscar un gestor en la base de datos por un campo y valor específicos, retornando un GestorDB
def search_gestor_db(field: str, value: str) -> GestorDB:
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"""SELECT * FROM `gestor` g JOIN `persona` p ON p.id_person = g.id_person WHERE {field} = %s"""
            cursor.execute(query, (value,))
            result = cursor.fetchone()
            if result:
                return GestorDB(**gestor_schema_db(result))  # Convierte el resultado en una instancia de GestorDB
        except Error as e:
            return None
        finally:
            close_connection(conn)  # Asegura que la conexión se cierre

# Función para validar el login del gestor, llamando a un procedimiento almacenado
def validacion_mayor(email: str, password: str, client_ip: str):
    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.callproc("ValidarLoginGestor", (email, password, client_ip))
            results = []
            for result in cursor.stored_results():
                results.append(result.fetchall())  # Recupera los resultados del procedimiento almacenado

            conn.commit()
            cursor.close()
            return results
        except Error as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"Error al buscar gestor: {str(e)}")
        finally:
            close_connection(conn)  # Asegura que la conexión se cierre
    
# Endpoint para registrar un nuevo gestor
@router.post("/registro", response_model=Gestor, status_code=status.HTTP_201_CREATED)
async def create_gestor(gestor: GestorDB):
    # Verifica si ya existe un gestor con el mismo email o DNI
    if type(search_gestor("email", gestor.email)) == Gestor or type(search_gestor("dni", gestor.dni)) == Gestor:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Gestor ya existente!")
    
    # Hash de la contraseña del gestor antes de almacenarla
    gestor_dict = dict(gestor)
    gestor_dict["password"] = crypt.hash(gestor.password)

    conn = get_connection()

    if conn:
        try:
            cursor = conn.cursor()
            cursor.callproc("AddGestor", (gestor_dict["nombre"], gestor_dict["apellidos"], gestor_dict["dni"], gestor_dict["email"], gestor_dict["password"]))
            conn.commit()
            cursor.close()
        except Error as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"Error general al insertar gestor: {str(e)}")
        finally:
            close_connection(conn)

    return Gestor(**gestor_dict)

# Endpoint para el login del gestor
@router.post("/login", status_code=status.HTTP_200_OK)
async def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    email = form.username
    password = form.password

    gestor_db = search_gestor_db("email", email)

    # Verifica si el gestor existe y si la contraseña es correcta
    if not gestor_db or not crypt.verify(password, gestor_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos")
    
    # Verifica la validez del login llamando a la función validacion_mayor
    client_ip = request.client.host
    if not validacion_mayor(email, gestor_db.password, client_ip):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email o contraseña incorrectos")
    
    # Genera el token de acceso JWT
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)
    access_token = jwt.encode({"email": email, "id": gestor_db.id_person, "exp": expire}, SECRET, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}

# Función para obtener el gestor actual a partir del token JWT
async def current_me(gestor_token: str = Depends(oauth2_scheme)):

    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"})
        
    try:
        gestor_email = jwt.decode(gestor_token, SECRET, algorithms=[ALGORITHM]).get("email")
        if gestor_email is None:
            raise exception
    except InvalidTokenError:
        raise exception
    
    return search_gestor("email", gestor_email)  # Busca el gestor basado en el email del token

# Endpoint para añadir un gestor existente a una gestión
@router.post("/addGestorExistente/{id_gestion}", status_code=status.HTTP_201_CREATED)
async def add_gestor_existente(id_gestion: int, request: Request, current_gestor: Gestor = Depends(current_me)):
   
   datosGestor = await request.json()

   # Verifica si el gestor a añadir existe
   if type(search_gestor("email", datosGestor.get("manager-email"))) != Gestor:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                            detail="Gestor no existente!")
   
   conn = get_connection()

   if conn:
       try:
           cursor = conn.cursor()
           cursor.callproc("AddGestorGestionExistente", (datosGestor.get("manager-email"), datosGestor.get("manager-name"), id_gestion))
           conn.commit()
           cursor.close()
       except Error as e:
           raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"Error al añadir al gestor: {str(e)}!")
       finally:
           close_connection(conn)  # Asegura que la conexión se cierre

# Endpoint para obtener los detalles del gestor actual
@router.get("/me", response_model=Gestor, status_code=status.HTTP_200_OK)
async def me(current_gestor: Gestor = Depends(current_me)):
    return current_gestor
