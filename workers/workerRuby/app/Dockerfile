# Usa una imagen base con Ruby
FROM ruby:3.0-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY workers/workerRuby/app/Gemfile ./
RUN bundle install

COPY workers/workerRuby/app/worker.rb .
COPY workers/workerRuby/app/master_pb.rb .
COPY workers/workerRuby/app/master_services_pb.rb .
COPY workers/workerRuby/proto proto/


# Comando para ejecutar el worker
CMD ["ruby", "worker.rb"]
