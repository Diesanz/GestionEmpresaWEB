import os
import json
from google.cloud import secretmanager

def access_secret(secret_name, key):
    client = secretmanager.SecretManagerServiceClient()
    
    # Accede a la última versión del secreto
    name = f"projects/935307705464/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    
    # Decodifica el valor del secreto como un string (formato tipo .env)
    secret_value = response.payload.data.decode('UTF-8')
    
    # Convierte el secreto a un diccionario (clave:valor)
    secret_dict = {}
    for line in secret_value.splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            secret_dict[k] = v
    
    # Retorna el valor asociado a la clave proporcionada
    return secret_dict.get(key)

