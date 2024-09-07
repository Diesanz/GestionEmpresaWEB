
def gestion_schema(gestion) -> dict:
    return {
        "id_gestion": int(gestion["id_gestion"]),
        "descripcion": gestion["descripcion"],
        "fecha_creacion": gestion["fecha_creacion"],
        "nombre_gestion": gestion["nombre_gestion"]
    }

def gestion_empresas_schema(gestion) -> dict:
    return {
        "id_gestion": int(gestion["id_gestion"]),
        "descripcion": gestion["descripcion"],
        "fecha_creacion": gestion["fecha_creacion"],
        "nombre_gestion": gestion["nombre_gestion"],
        "empresas": gestion["empresas"]
    }