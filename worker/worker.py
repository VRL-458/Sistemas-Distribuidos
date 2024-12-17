import grpc
import master_pb2
import master_pb2_grpc

def register_with_master():
    channel = grpc.insecure_channel("grpc_master:50051")
    stub = master_pb2_grpc.MasterStub(channel)

    # Registro con el Master
    response = stub.RegisterWorker(master_pb2.RegisterWorkerRequest())
    worker_id = response.worker_id
    print(f"Worker registrado con ID: {worker_id}")
    return worker_id, stub

def send_log(stub, worker_id, sensor_id, freq, iteration):
    # Enviar log al Master
    log_request = master_pb2.LogRequest(
        worker_id=worker_id,
        sensor_id=sensor_id,
        freq=freq,
        iteration=iteration,
    )
    response = stub.Log(log_request)
    print(f"Respuesta del Master: {response.status}")

def main():
    # Registro con el Master
    worker_id, stub = register_with_master()

    # Simulación de tareas
    send_log(stub, worker_id, "sensor_01", 0.5, 10)
    send_log(stub, worker_id, "sensor_02", 0.3, 7)

if __name__ == "__main__":
    main()
