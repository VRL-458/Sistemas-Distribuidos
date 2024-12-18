#!/bin/bash

# Variables
IMAGE_PYTHON="10.1.2.151:5000/worker_python"
IMAGE_RUBY="10.1.2.151:5000/worker_ruby"
#IMAGE_NODEJS="10.1.2.151:5000/worker_nodejs"
#IMAGE_C++="10.1.2.151:5000/worker_c++"

# Eliminar imagen local
docker rmi -f $IMAGE_PYTHON
docker rmi -f $IMAGE_RUBY
#docker rmi -f $IMAGE_NODEJS
#docker rmi -f $IMAGE_C++

# Crear (build) la imagen
docker build -t $IMAGE_PYTHON -f workers/workerPython/Dockerfile .
docker build -t $IMAGE_RUBY -f  workers/WorkerRuby/workerRuby/Dockerfile .
#docker build -t $IMAGE_NODEJS -f worker/Dockerfile .
#docker build -t $IMAGE_C++ -f worker/Dockerfile .


# Hacer push de la imagen al registry
docker push $IMAGE_NAME
