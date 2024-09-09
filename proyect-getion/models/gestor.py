from pydantic import BaseModel
from typing import Optional

class Gestor(BaseModel):  
    id_person: Optional[int] = None
    nombre: str
    apellidos: str
    dni: str
    email: str

class GestorDB(Gestor):
    password: str