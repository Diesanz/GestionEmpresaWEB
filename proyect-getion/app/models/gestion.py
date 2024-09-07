from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Gestion(BaseModel):
    id_gestion: Optional[int] = None
    descripcion: str
    fecha_creacion: Optional[datetime] = None
    nombre_gestion: str

class Gestion_Empresas(Gestion):
    empresas: Optional[list] = []