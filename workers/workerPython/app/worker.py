import grpc
import paho.mqtt.client as mqtt
import random
import time
import master_pb2
import master_pb2_grpc

BROKER = "mqtt"  # Dirección del servidor MQTT

def register_with_master(worker_id):
    """Registra el worker con el Master a través de gRPC y devuelve el ID y stub."""
    channel = grpc.insecure_channel("master:8888")
    stub = master_pb2_grpc.MasterStub(channel)

    # Registro con el Master
    response = stub.RegisterWorker(master_pb2.RegisterWorkerRequest(worker_id=worker_id))
    print(f"Worker registrado con ID: {worker_id}")
    return stub

def send_log(stub, worker_id, sensor_id, freq, iteration):
    """Envía un log al Master usando gRPC."""
    log_request = master_pb2.LogRequest(
        worker_id=worker_id,
        sensor_id=sensor_id,
        freq=freq,
        iteration=iteration,
    )
    response = stub.Log(log_request)
    print(f"Log enviado al Master: Worker {worker_id}, Sensor {sensor_id}, "
          f"Freq={freq}, Iteration={iteration}, Respuesta: {response.status}")

def on_message(client, userdata, msg):
    """Callback ejecutado al recibir un mensaje MQTT."""
    payload = eval(msg.payload.decode())  # Se espera un string que represente un diccionario
    print(f"Mensaje recibido en {msg.topic}: {payload}")

    # Extraer datos del mensaje
    sensor_id = payload.get("sensor_id")
    worker_id = userdata["worker_id"]
    stub = userdata["stub"]

    # Generar valores aleatorios
    freq = round(random.uniform(0.1, 1.0), 2)  # Frecuencia [0.1 - 1] con 2 decimales
    iteration = random.randint(5, 10)  # Iteración [5 - 10] enteros

    print(f"Worker {worker_id}: Tarea recibida de {sensor_id}. Freq={freq}, Iteration={iteration}")

    # Enviar log al Master
    send_log(stub, worker_id, sensor_id, freq, iteration)

    # Publicar respuesta al ESP32 en el tópico correspondiente
    response_topic = f"upb/{worker_id}/response"
    response_message = {"freq": freq, "iteration": iteration}
    client.publish(response_topic, str(response_message))
    print(f"Respuesta publicada en {response_topic}: {response_message}")

def main():
    # Paso 1: Registrar el Worker con el Master
    worker_id = "ID WORKER CONTAINER"
    stub = register_with_master(worker_id)

    # Paso 2: Configurar el cliente MQTT
    client = mqtt.Client(userdata={"worker_id": worker_id, "stub": stub})
    client.on_message = on_message

    # Conectar al Broker MQTT
    client.connect(BROKER, 1883, 60)

    # Suscribirse al tópico para recibir tareas
    request_topic = f"upb/{worker_id}/request"
    client.subscribe(request_topic)
    print(f"Worker {worker_id} suscrito al tópico: {request_topic}")

    # Iniciar el loop de recepción de mensajes
    print("Esperando mensajes...")
    client.loop_forever()

if __name__ == "__main__":
    main()
