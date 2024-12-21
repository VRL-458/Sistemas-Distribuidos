#!/bin/bash

# Variables
REGISTRY="10.1.2.151:5000"                       # Dirección del registro
IMAGE_NAME="master"                              # Nombre de la imagen del master
STACK_NAME="sistemas_distribuidos"               # Nombre del stack
DOCKERFILE_PATH="master/Dockerfile"              # Ruta del Dockerfile del master
NETWORK_NAME="red-gRPC"                          # Nombre de la red Swarm

# Crear la red overlay
if ! docker network inspect $NETWORK_NAME >/dev/null 2>&1; then
  echo "Creando red $NETWORK_NAME..."
  docker network create \
    --driver overlay \
    $NETWORK_NAME
else
  echo "La red $NETWORK_NAME ya existe."
fi

# Crear el servicio MQTT
echo "Creando servicio MQTT..."
docker service create \
  --name sistemas_distribuidos_mqtt \
  --network $NETWORK_NAME \
  --constraint 'node.role == manager' \
  --publish 1883:1883 \
  eclipse-mosquitto:latest

# Crear el servicio Redis
echo "Creando servicio Redis..."
docker service create \
  --name sistemas_distribuidos_redis \
  --network $NETWORK_NAME \
  --constraint 'node.role == manager' \
  --publish 6379:6379 \
  redis:latest

# Verificar que los servicios MQTT y Redis estén corriendo
echo "Esperando que MQTT y Redis estén activos..."
while true; do
  MQTT_RUNNING=$(docker service ls --filter "name=sistemas_distribuidos_mqtt" --format "{{.Replicas}}")
  REDIS_RUNNING=$(docker service ls --filter "name=sistemas_distribuidos_redis" --format "{{.Replicas}}")

  if [[ "$MQTT_RUNNING" == "1/1" && "$REDIS_RUNNING" == "1/1" ]]; then
    echo "MQTT y Redis están activos."
    break
  fi

  echo "Esperando que MQTT y Redis estén listos..."
  sleep 5
done

# Construir la imagen del Master
echo "Construyendo la imagen Docker del Master..."
docker build -t $REGISTRY/$IMAGE_NAME:latest -f $DOCKERFILE_PATH .

# Subir la imagen del Master al registro
echo "Subiendo la imagen del Master al registro $REGISTRY..."
docker push $REGISTRY/$IMAGE_NAME:latest

# Crear el servicio Master
echo "Creando servicio Master..."
docker service create \
  --name sistemas_distribuidos_master \
  --network $NETWORK_NAME \
  --constraint 'node.role == manager' \
  --publish 8888:8888 \
  $REGISTRY/$IMAGE_NAME:latest \
  python3 /app/master.py

# Verificar que el servicio Master esté corriendo
echo "Esperando que el Master esté activo..."
while true; do
  MASTER_RUNNING=$(docker service ls --filter "name=sistemas_distribuidos_master" --format "{{.Replicas}}")

  if [[ "$MASTER_RUNNING" == "1/1" ]]; then
    echo "Master está activo."
    break
  fi

  echo "Esperando al Master..."
  sleep 5
done

# Crear los servicios de Workers
echo "Creando servicios de Workers..."
docker service create \
  --name sistemas_distribuidos_worker_python \
  --replicas 3 \
  --network $NETWORK_NAME \
  --constraint 'node.role == worker' \
  $REGISTRY/worker_python:latest

# Fin
echo "Servicios desplegados exitosamente. Verifica el estado con 'docker service ls'."
