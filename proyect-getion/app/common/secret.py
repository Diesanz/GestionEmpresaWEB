import os
from google.cloud import secretmanager

def access_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/gestion-emp/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)
    secret_value = response.payload.data.decode('UTF-8')
    return secret_value