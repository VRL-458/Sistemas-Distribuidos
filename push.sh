#!/bin/bash

# Variables
IMAGE_NAME="10.1.2.151:5000/worker-image"

# Eliminar imagen local
docker rmi -f $IMAGE_NAME

# Crear (build) la imagen
docker build -t $IMAGE_NAME -f worker/Dockerfile .

# Hacer push de la imagen al registry
docker push $IMAGE_NAME
