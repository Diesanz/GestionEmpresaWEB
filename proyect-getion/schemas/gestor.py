
def gestor_schema(gestor) -> dict:
    return {
        "id_person": int(gestor["id_person"]),
        "nombre": gestor["nombre"],
        "apellidos": gestor["apellidos"],
        "dni": gestor["dni"],
        "email": gestor["email"]
    }

def gestor_schema_db(gestor) -> dict:
    return {
        "id_person": int(gestor["id_person"]),
        "nombre": gestor["nombre"],
        "apellidos": gestor["apellidos"],
        "dni": gestor["dni"],
        "email": gestor["email"],
        "password": gestor["password"]
    }

def users_schema(gestores) -> list:
    return [gestor_schema(gestor) for gestor in gestores]