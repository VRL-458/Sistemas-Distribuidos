import grpc
from concurrent import futures
import master_pb2
import master_pb2_grpc
import paho.mqtt.client as mqtt
import json
import redis  # Biblioteca para interactuar con Redis
import threading

# Configuración MQTT
BROKER = "research.upb.edu"
TOPIC_REQUEST = "upb/master/request"
TOPIC_RESPONSE = "upb/master/response"

# Configuración Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def connect_redis(self):
    """Intentar conectar con Redis con reintentos."""
    global redis_client
    for _ in range(5):  # Reintentar hasta 5 veces
        try:
            redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            # Verificar la conexión con un comando PING
            redis_client.ping()
            print("Conectado exitosamente a Redis.")
            break
        except redis.ConnectionError as e:
            print(f"Error al conectar con Redis: {e}. Reintentando en 3 segundos...")
            time.sleep(3)
    else:
        print("No se pudo conectar a Redis después de varios intentos.")
        # Aquí puedes definir una estrategia para seguir, como asignar un Worker predeterminado o salir


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
    if worker_id == "":
        if redis_client.llen(master.worker_list_key) > 0:
            assigned_worker = redis_client.lpop(master.worker_list_key)
            print(f"Asignando Worker ID: {assigned_worker} al Sensor ID: {sensor_id}")

            # Responder al ESP32 con el Worker ID asignado
            response = {
                "sensor_id": sensor_id,
                "worker_id": assigned_worker
            }
            client.publish(TOPIC_RESPONSE, json.dumps(response))
        else:
            print("No hay Workers disponibles en este momento.")
    else:
        # Reinserta el Worker ID en la lista de Redis si está en uso
        redis_client.rpush(master.worker_list_key, worker_id)
        print(f"Worker ID {worker_id} reintegrado a la lista de disponibles.")

# Servidor gRPC
def serve_grpc(master):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    master_pb2_grpc.add_MasterServicer_to_server(master, server)
    server.add_insecure_port("[::]:50051")
    print("Servidor Master en ejecución en el puerto 50051")
    server.start()
    server.wait_for_termination()

# Cliente MQTT
def start_mqtt(master):
    client = mqtt.Client(userdata={"master": master})
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.loop_forever()

if __name__ == "__main__":
    master_servicer = MasterServicer()

    # Iniciar gRPC en un hilo separado
    grpc_thread = threading.Thread(target=serve_grpc, args=(master_servicer,))
    grpc_thread.start()

    # Iniciar MQTT
    start_mqtt(master_servicer)
