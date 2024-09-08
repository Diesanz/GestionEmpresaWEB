import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException, status
from common import access_sercret

# Cargar variables de entorno desde el archivo .env
load_dotenv()

import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException, status
from common import access_secret

def get_connection():
    try:
        # Obtén los secretos desde Secret Manager
        host = access_secret("DB_HOST")
        port = int(access_secret("DB_PORT"))
        database = access_secret("DB_NAME")
        user = access_secret("DB_USER")
        password = access_secret("DB_PASSWORD")
        
        # Conéctate a la base de datos
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Error al conectarse a la base de datos")


def close_connection(connection):
    if connection.is_connected():
        connection.close()
