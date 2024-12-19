# Usa una imagen base con Ruby
FROM ruby:3.0-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala herramientas de compilación y dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libgmp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos necesarios para instalar las dependencias
COPY workers/workerRuby/app/Gemfile workers/workerRuby/app/Gemfile.lock ./

# Instala las dependencias
RUN bundle install

# Copia los archivos fuente
COPY workers/workerRuby/app/worker.rb .
COPY workers/workerRuby/app/master_pb.rb .
COPY workers/workerRuby/app/master_services_pb.rb .
COPY workers/workerRuby/proto proto/

# Comando para ejecutar el worker
CMD ["ruby", "worker.rb"]
