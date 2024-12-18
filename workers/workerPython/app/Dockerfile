# Usa una imagen base ligera de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias necesarias para gRPC
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de dependencias e instala los paquetes
COPY workers/workerPython/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copia el archivo .proto y genera los archivos gRPC
COPY workers/workerPython/proto ./proto
RUN python3 -m grpc_tools.protoc -I=./proto --python_out=. --grpc_python_out=. ./proto/master.proto

# Copia el archivo principal del Worker
COPY workers/workerPython/app/worker.py .

# Expone el puerto (opcional, ya que el Worker es cliente)
EXPOSE 50051

# Comando por defecto para ejecutar el Worker
CMD ["python", "worker.py"]
