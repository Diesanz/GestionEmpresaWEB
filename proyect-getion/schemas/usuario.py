
def usuario_schema(usuario) -> dict:
    return{
        "id_person": int(usuario["id_person"]),
        "nombre": usuario["nombre"],
        "apellidos": usuario["apellidos"],
        "dni": usuario["dni"],
        "email": usuario["email"]
    }

def usuario_schema_db(usuario) -> dict:
    return{
        "id_person": int(usuario["id_person"]),
        "nombre": usuario["nombre"],
        "apellidos": usuario["apellidos"],
        "dni": usuario["dni"],
        "email": usuario["email"],
        "fecha_creación": usuario["fecha_creación"],
        "nombre_usuario": usuario["nombre_usuario"],
    }