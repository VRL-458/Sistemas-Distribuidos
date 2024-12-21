# Usa una imagen base de Node.js
FROM node:18-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios para instalar dependencias
COPY workers/workerNode/app/package.json workers/workerNode/app/package-lock.json ./

# Instala las dependencias
RUN npm install

# Copia los archivos fuente
COPY workers/workerNode/app/worker.js .
COPY workers/workerNode/app/master_pb.js .
COPY workers/workerNode/app/master_grpc_pb.js .
COPY workers/workerNode/proto/master.proto .



COPY wait_for_it/ ./wait_for_it

# Comando para ejecutar el worker

CMD ["sh", "-c", "wait_for_it/wait-for-it.sh master:8888 --timeout=50 --strict && node worker.js"]
#CMD ["node", "worker.js"]
