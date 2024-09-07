import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from fastapi import HTTPException, status

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        if connection.is_connected():
            return connection
    except Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Error al conectarse a la base de datos")

def close_connection(connection):
    if connection.is_connected():
        connection.close()
