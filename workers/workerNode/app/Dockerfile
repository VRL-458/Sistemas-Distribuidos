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
COPY workers/workerNode/proto proto/

# Comando para ejecutar el worker
CMD ["node", "worker.js"]
