# Variables
PYTHON = python3
PROTOC = $(PYTHON) -m grpc_tools.protoc
PROTO_DIR = proto
MASTER_DIR = master
WORKER_DIR = worker
REDIS_CONTAINER = redis-container

# Generar archivos gRPC
.PHONY: proto
proto:
	$(PROTOC) -I=$(PROTO_DIR) --python_out=$(MASTER_DIR) --grpc_python_out=$(MASTER_DIR) $(PROTO_DIR)/master.proto
	$(PROTOC) -I=$(PROTO_DIR) --python_out=$(WORKER_DIR) --grpc_python_out=$(WORKER_DIR) $(PROTO_DIR)/master.proto
	@echo "Archivos gRPC generados correctamente."

# Instalar dependencias y levantar Redis
.PHONY: install
install: install-redis
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(MASTER_DIR)/requirements.txt
	$(PYTHON) -m pip install -r $(WORKER_DIR)/requirements.txt
	@echo "Dependencias instaladas correctamente."

# Ejecutar Redis en un contenedor Docker
.PHONY: install-redis
install-redis:
	@echo "Verificando si Redis está corriendo..."
	@docker ps -q -f name=$(REDIS_CONTAINER) || docker run -d --name $(REDIS_CONTAINER) -p 6379:6379 redis:latest
	@echo "Redis está en ejecución."

# Parar el contenedor de Redis
.PHONY: stop-redis
stop-redis:
	@echo "Deteniendo Redis..."
	docker stop $(REDIS_CONTAINER)
	docker rm $(REDIS_CONTAINER)
	@echo "Redis detenido y eliminado."

# Ejecutar el Master
.PHONY: master
master:
	$(PYTHON) $(MASTER_DIR)/master.py

# Ejecutar un Worker
.PHONY: worker
worker:
	$(PYTHON) $(WORKER_DIR)/worker.py

# Limpiar archivos generados
.PHONY: clean
clean:
	rm -f $(MASTER_DIR)/master_pb2.py $(MASTER_DIR)/master_pb2_grpc.py
	rm -f $(WORKER_DIR)/master_pb2.py $(WORKER_DIR)/master_pb2_grpc.py
	@echo "Archivos generados limpiados."

# Ejecutar todo (Master y Workers en paralelo)
.PHONY: run
run: proto install
	@echo "Iniciando Master y Workers..."
	$(PYTHON) $(MASTER_DIR)/master.py &  # Ejecuta el Master en segundo plano
	$(PYTHON) $(WORKER_DIR)/worker.py & # Ejecuta un Worker en segundo plano
	$(PYTHON) $(WORKER_DIR)/worker.py   # Ejecuta otro Worker en primer plano
