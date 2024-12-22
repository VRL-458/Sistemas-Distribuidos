import grpc
from concurrent import futures
import master_pb2
import master_pb2_grpc
import paho.mqtt.client as mqtt
import json
import redis  # Biblioteca para interactuar con Redis
import threading
import time

# Configuración MQTT
BROKER = "mqtt"
TOPIC_REQUEST = "upb/master/request"
TOPIC_RESPONSE = "upb/master/response"

# Configuración Redis
#REDIS_HOST = "10.1.0.224"
REDIS_HOST = "redis"
REDIS_PORT = 6379
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Cola de esp32
queue = []

# Clase MasterServicer para gRPC
class MasterServicer(master_pb2_grpc.MasterServicer):
    def __init__(self):
        self.worker_list_key = "workers"  # Clave de Redis para la lista de Workers

    def RegisterWorker(self, request, context):
        # Generar un nuevo Worker ID basado en la longitud de la lista en Redis
        worker_id = request.worker_id

        # Guardar el Worker ID en Redis
        redis_client.rpush(self.worker_list_key, worker_id)
        print(f"Worker registrado: {worker_id}")
        return master_pb2.RegisterWorkerResponse(status="OK")

    def Log(self, request, context):
        # Procesar un log de un Worker
        log_message = (f"Log recibido del Worker {request.worker_id}: "
                       f"Sensor ID: {request.sensor_id}, Freq: {request.freq}, Iteration: {request.iteration}")
        print(log_message)
        return master_pb2.LogResponse(status="OK")

# Callback de conexión para MQTT
def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT con código de resultado: ", rc)
    client.subscribe(TOPIC_REQUEST)

# Callback para manejar mensajes recibidos
def on_message(client, userdata, msg):
    master = userdata['master']
    payload = json.loads(msg.payload.decode())
    sensor_id = payload.get("sensor_id", "")
    worker_id = payload.get("worker_id", "")

    print(f"Mensaje recibido: Sensor ID: {sensor_id}, Worker ID: {worker_id}")

    # Asignar un Worker ID si no existe uno asignado

    if worker_id != "":
        # Reinserta el Worker ID en la lista de Redis si está en uso
        redis_client.rpush(master.worker_list_key, worker_id)
        print(f"Worker ID {worker_id} reintegrado a la lista de disponibles.")
			
    queue.append(sensor_id)

# Servidor gRPC
def serve_grpc(master):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    master_pb2_grpc.add_MasterServicer_to_server(master, server)
    server.add_insecure_port("[::]:8888")
    print("Servidor Master en ejecución en el puerto 8888")
    server.start()
    server.wait_for_termination()

# Cliente MQTT
def start_mqtt(master):
    client = mqtt.Client(userdata={"master": master})
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.loop_start()
    return client



if __name__ == "__main__":
    master_servicer = MasterServicer()

    # Iniciar gRPC en un hilo separado
    grpc_thread = threading.Thread(target=serve_grpc, args=(master_servicer,))
    grpc_thread.start()

    mqtt_client = start_mqtt(master_servicer)
    
    try:
        while True:
            if redis_client.llen(master_servicer.worker_list_key) > 0 and queue:
                assigned_worker = redis_client.lpop(master_servicer.worker_list_key)
                sensor_id = queue.pop(0)
                print(f"Asignando Worker ID: {assigned_worker} al Sensor ID: {sensor_id}")

                # Responder al ESP32 con el Worker ID asignado
                response = {
                    "sensor_id": sensor_id,
                    "worker_id": assigned_worker
                }
                mqtt_client.publish(TOPIC_RESPONSE, json.dumps(response))
            time.sleep(0.5)
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        print("Programa terminado por el usuario.")
