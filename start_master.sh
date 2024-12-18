#!/bin/bash

# Variables
REGISTRY="10.1.2.151:5000"                       # Dirección del registro
IMAGE_NAME="master"                              # Nombre de la imagen
STACK_NAME="sistemas_distribuidos"               # Nombre del stack
DOCKERFILE_PATH="master/Dockerfile"              # Ruta del Dockerfile
NETWORK_NAME="red-gRPC"                          # Nombre de la red Swarm

# Paso: Construir la imagen Docker
echo "Construyendo la imagen Docker..."
docker build -t $REGISTRY/$IMAGE_NAME:latest -f $DOCKERFILE_PATH .

# Paso: Subir la imagen al registro
echo "Subiendo la imagen al registro $REGISTRY..."
docker push $REGISTRY/$IMAGE_NAME:latest

# Paso: Crear archivo docker-compose-stack.yml
echo "Generando archivo docker-compose-stack.yml..."
cat <<EOF > docker-compose-stack.yml
version: '3.8'

services:
  master:
    image: $REGISTRY/$IMAGE_NAME:latest
    ports:
      - "8888:8888"
    networks:
      - $NETWORK_NAME
    deploy:
      placement:
        constraints:
          - node.role == manager

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    networks:
      - $NETWORK_NAME
    deploy:
      placement:
        constraints:
          - node.role == manager

  mqtt:
    image: eclipse-mosquitto:latest
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
    networks:
      - $NETWORK_NAME
    deploy:
      placement:
        constraints:
          - node.role == manager

networks:
  $NETWORK_NAME:
    external: true
EOF

# Paso 6: Desplegar la pila en Swarm
echo "Desplegando la pila '$STACK_NAME' en Swarm..."
docker stack deploy -c docker-compose-stack.yml $STACK_NAME

# Fin
echo "Despliegue completado. Verifica el estado con 'docker service ls'."
