# Variables
PYTHON = python3
PROTOC = python3 -m grpc_tools.protoc
PROTO_DIR = proto
MASTER_DIR = master
WORKER_DIR = worker
NODE = node

# Generar archivos gRPC
.PHONY: proto
proto:
	$(PROTOC) -I=$(PROTO_DIR) --python_out=$(MASTER_DIR) --grpc_python_out=$(MASTER_DIR) $(PROTO_DIR)/master.proto
	@echo "Archivos gRPC generados correctamente."

# Instalar dependencias
.PHONY: install
install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(MASTER_DIR)/requirements.txt
	cd $(WORKER_DIR) && npm install
	@echo "Dependencias instaladas correctamente."

# Ejecutar el Master
.PHONY: master
master:
	$(PYTHON) $(MASTER_DIR)/master.py

# Ejecutar un Worker (Node.js)
.PHONY: worker
worker:
	cd $(WORKER_DIR) && $(NODE) worker.js

# Limpiar archivos generados
.PHONY: clean
clean:
	rm -f $(MASTER_DIR)/master_pb2.py $(MASTER_DIR)/master_pb2_grpc.py
	@echo "Archivos generados limpiados."

# Ejecutar todo (Master y 2 Workers en paralelo)
.PHONY: run
run: proto install
	@echo "Iniciando Master y Workers..."
	$(PYTHON) $(MASTER_DIR)/master.py &  # Ejecuta el Master en segundo plano
	cd $(WORKER_DIR) && $(NODE) worker.js &
	cd $(WORKER_DIR) && $(NODE) worker.js
