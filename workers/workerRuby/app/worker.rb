require 'grpc'
require_relative 'master_pb'
require_relative 'master_services_pb'
require 'mqtt'
require 'json'

BROKER = 'research.upb.edu'
PORT = 1883
USE_SSL = false  # Cambiar a true si se requiere SSL

# Registrar el Worker con el Master
def register_with_master(worker_id)
  stub = Master::Master::Stub.new('localhost:50051', :this_channel_is_insecure)
  request = Master::RegisterWorkerRequest.new(worker_id: worker_id)
  response = stub.register_worker(request)
  puts "Worker registrado con ID: #{worker_id}"
  return stub
end

# Enviar log al Master
def send_log(stub, worker_id, sensor_id, freq, iteration)
  request = Master::LogRequest.new(
    worker_id: worker_id,
    sensor_id: sensor_id,
    freq: freq,
    iteration: iteration
  )
  response = stub.log(request)
  puts "Log enviado: Sensor=#{sensor_id}, Freq=#{freq}, Iteraciones=#{iteration}, Status=#{response.status}"
end

# Función principal que ejecuta todo el flujo
def main
  # Paso 1: Registro con el Master
  worker_id = "bbb"
  stub = register_with_master(worker_id)
  
  # Paso 2: Configurar el cliente MQTT usando la gema 'mqtt'
  client = MQTT::Client.new(BROKER, PORT)
  client.ack_timeout = 10  # Establecer tiempo de espera para confirmaciones
  client.keep_alive = 60   # Mantener la conexión viva por 60 segundos
  client.connect

  puts "Conectado al broker MQTT"

  # Suscripción al tópico
  request_topic = "upb/#{worker_id}/request"
  client.subscribe(request_topic)
  puts "Worker #{worker_id} suscrito al tópico: #{request_topic}"

  # Configurar callback de mensaje
  client.get do |topic, message|
    begin
      puts "Mensaje recibido - Tópico: #{topic}, Payload: #{message}"
      
      msg_payload = JSON.parse(message)
      sensor_id = msg_payload['sensor_id']
      
      # Generar valores aleatorios
      freq = rand(0.1..1.0).round(2)
      iteration = rand(5..10)
      
      puts "Worker #{worker_id}: Tarea recibida de #{sensor_id}. Freq=#{freq}, Iteration=#{iteration}"
      
      send_log(stub, worker_id, sensor_id, freq, iteration)
      
      # Publicar respuesta al ESP32
      response_topic = "upb/#{worker_id}/response"
      response_message = { 'freq' => freq, 'iteration' => iteration }
      client.publish(response_topic, response_message.to_json)
      
      puts "Respuesta publicada en #{response_topic}: #{response_message}"
    rescue JSON::ParserError
      puts "Error parseando el mensaje JSON"
    rescue => e
      puts "Error procesando mensaje: #{e.message}"
    end
  end
end

main if __FILE__ == $PROGRAM_NAME
