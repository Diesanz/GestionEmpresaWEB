from pydantic import BaseModel
from typing import Optional

class Usuario(BaseModel):
    id_person: Optional[int] = None
    nombre: str
    apellidos: str
    dni: str
    email: str

class UsuarioDB(Usuario):
    fecha_creacion: Optional[str] = None
    nombre_usuario: str
    user_company: str