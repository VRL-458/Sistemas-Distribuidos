require 'grpc'
require_relative 'master_pb'
require_relative 'master_services_pb'

def register_with_master
  # Crear un canal gRPC al servidor Master
  stub = Master::Stub.new('localhost:50051', :this_channel_is_insecure)

  # Registrar el Worker con el Master
  request = RegisterWorkerRequest.new
  response = stub.register_worker(request)
  puts "Worker registrado con ID: #{response.worker_id}"

  return response.worker_id, stub
end

def send_log(stub, worker_id, sensor_id, freq, iteration)
  # Enviar un log al Master
  request = LogRequest.new(
    worker_id: worker_id,
    sensor_id: sensor_id,
    freq: freq,
    iteration: iteration
  )
  response = stub.log(request)
  puts "Log enviado: Sensor=#{sensor_id}, Freq=#{freq}, Iteraciones=#{iteration}, Status=#{response.status}"
end

def main
  # Paso 1: Registro con el Master
  worker_id, stub = register_with_master

  # Paso 2: Simulación de tareas
  send_log(stub, worker_id, 'sensor_01', 0.5, 10)
  send_log(stub, worker_id, 'sensor_02', 0.3, 7)
end

main if __FILE__ == $PROGRAM_NAME
