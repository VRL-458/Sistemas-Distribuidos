#!/bin/bash

# Variables
REGISTRY="10.1.2.151:5000"                       # Dirección del registro
IMAGE_NAME="master"                              # Nombre de la imagen
STACK_NAME="sistemas_distribuidos"               # Nombre del stack
DOCKERFILE_PATH="master/Dockerfile"              # Ruta del Dockerfile

# Paso: Construir la imagen Docker

docker rmi -f $REGISTRY/$IMAGE_NAME
echo "Construyendo la imagen Docker..."
docker build -t $REGISTRY/$IMAGE_NAME:latest -f $DOCKERFILE_PATH .

# Paso: Subir la imagen al registro
echo "Subiendo la imagen al registro $REGISTRY..."
docker push $REGISTRY/$IMAGE_NAME:latest


# Paso 6: Desplegar la pila en Swarm
echo "Desplegando la pila '$STACK_NAME' en Swarm..."
docker stack deploy -c docker-compose-stack.yml $STACK_NAME

# Fin
