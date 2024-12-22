from umqtt.simple import MQTTClient
import ujson
import time

# Conexión MQTT
def connect_mqtt():
    client = MQTTClient(sensor_id, BROKER, port=PORT)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_RESPONSE)
    print(f"Conectado a MQTT y suscrito a {TOPIC_RESPONSE}")
    return client

# Manejo de mensajes del Worker
def worker_handler(msg):
    try:
        print("Mensaje recibido del Worker:", msg)
        data = ujson.loads(msg.decode("utf-8"))
        freq = float(data["freq"])
        iteration = int(data["iteration"])

        print(f"Tarea recibida: freq={freq}, iteration={iteration}")
        execute_task(freq, iteration)
    except Exception as e:
        print("Error procesando mensaje del Worker:", e)

# Manejo de mensajes del Master
def master_handler(client, msg):
    global sensor_id, worker_id, TOPIC_WORKER_REQ, TOPIC_WORKER_RES
    try:
        print("Mensaje recibido del Master:", msg)
        data = ujson.loads(msg.decode("utf-8"))
        sensor_id_ = data["sensor_id"]

        if sensor_id_ == sensor_id:
            worker_id = data["worker_id"]
            TOPIC_WORKER_RES = f"upb/{worker_id}/response"
            TOPIC_WORKER_REQ = f"upb/{worker_id}/request"
            
            print(f"Suscribiéndose a {TOPIC_WORKER_RES}")
            client.subscribe(TOPIC_WORKER_RES)
            send_request(client, TOPIC_WORKER_REQ)
    except Exception as e:
        print("Error procesando mensaje del Master:", e)

# Callback de mensajes MQTT
def on_message(topic, msg):
    global client
    topic = topic.decode('utf-8')
    if topic == TOPIC_RESPONSE:
        master_handler(client, msg)
    elif topic == TOPIC_WORKER_RES:
        worker_handler(msg)

# Ejecutar la tarea del Worker
def execute_task(freq, iteration):
    global client, worker_id, TOPIC_WORKER_REQ, TOPIC_WORKER_RES
    for _ in range(iteration):
        led.on()
        time.sleep(freq)
        led.off()
        time.sleep(freq)
    
    # Una vez completada la tarea, enviar solicitud al Master
    print("Tarea completada, solicitando nueva asignación")
    TOPIC_WORKER_REQ = ""
    TOPIC_WORKER_RES = ""
    send_request(client, TOPIC_REQUEST)

# Enviar solicitudes al Master o Worker
def send_request(client, topic):
    global worker_id, sensor_id
    request_data = {
        "sensor_id": sensor_id,
        "worker_id": worker_id
    }
    client.publish(topic, ujson.dumps(request_data))
    print(f"Solicitud enviada a {topic}:", request_data)

# Main
try:
    client = connect_mqtt()
    send_request(client, TOPIC_REQUEST) 
    while True:
        client.check_msg()
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Ejecución interrumpida por el usuario.")
except Exception as e:
    print("Error en el programa:", e)
finally:
    if client:
        client.disconnect()
    print("Cliente MQTT desconectado.")