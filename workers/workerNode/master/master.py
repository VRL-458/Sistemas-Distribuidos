import grpc
from concurrent import futures
import master_pb2
import master_pb2_grpc

class MasterServicer(master_pb2_grpc.MasterServicer):
    def __init__(self):
        self.worker_list = []

    def RegisterWorker(self, request, context):
        # Generar un worker_id único y devolverlo al Worker
        worker_id = f"worker_{len(self.worker_list) + 1}"
        self.worker_list.append(worker_id)
        print(f"Worker registrado: {worker_id}")
        return master_pb2.RegisterWorkerResponse(worker_id=worker_id)

    def Log(self, request, context):
        # Recibir el log de un Worker
        print(f"Log recibido del Worker {request.worker_id}:")
        print(f"  Sensor ID: {request.sensor_id}")
        print(f"  Frecuencia: {request.freq}")
        print(f"  Iteraciones: {request.iteration}")
        return master_pb2.LogResponse(status="OK")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    master_pb2_grpc.add_MasterServicer_to_server(MasterServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("Servidor Master en ejecución en el puerto 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
