# Usa una imagen base ligera de Python
FROM python:3.9-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias necesarias para gRPC
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de dependencias e instala los paquetes
COPY master/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia la carpeta proto y genera los archivos gRPC
COPY master/proto ./proto
RUN python3 -m grpc_tools.protoc -I=./proto --python_out=. --grpc_python_out=. ./proto/master.proto

# Copia el resto del código del servidor
COPY master/master.py .

# Expone el puerto 50051 para gRPC
EXPOSE 8888

# Comando para ejecutar el servidor Master
CMD ["python", "master.py"]
