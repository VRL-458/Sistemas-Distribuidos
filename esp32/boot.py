import network
import time
import machine
import ntptime

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a la red Wi-Fi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print("Conectado a Wi-Fi:", wlan.ifconfig())

def generate_sensor_id():
    wlan = network.WLAN(network.STA_IF)
    ip_last_digits = wlan.ifconfig()[0].split(".")[-2:]
    ntptime.settime()
    timestamp = int(time.time()) % 100000 
    sensor_id = ".".join(ip_last_digits) + f".{timestamp}"
    print("Sensor ID generado:", sensor_id)
    return sensor_id

# Configuración Wi-Fi
SSID = "Entel 98"
PASSWORD = "Lacaidadel95COMO76"
connect_to_wifi(SSID, PASSWORD)

# Creacion sensor_id
sensor_id = generate_sensor_id()

# Configuración MQTT
BROKER = "research.upb.edu"
PORT = 21512
TOPIC_REQUEST = "upb/master/request"
TOPIC_RESPONSE = "upb/master/response"
worker_id = ""
TOPIC_WORKER_REQ = ""
TOPIC_WORKER_RES = ""

# LED interno del ESP32
led = machine.Pin(2, machine.Pin.OUT)