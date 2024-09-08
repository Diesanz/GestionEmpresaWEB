# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de la aplicación al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponer el puerto en el que la aplicación escuchará
EXPOSE 80

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
