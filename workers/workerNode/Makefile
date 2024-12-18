# Variables
PYTHON = python3
PROTOC = $(PYTHON) -m grpc_tools.protoc
PROTO_DIR = proto
MASTER_DIR = master
WORKER_DIR = worker
WORKER_RUBY_DIR = workerRuby
WORKER_NODE_DIR = workerNode
REDIS_CONTAINER = redis-container
RUBY_GRPC_PLUGIN = $(shell which grpc_tools_ruby_protoc_plugin)
GRPC_TOOLS_NODE_PROTOC = grpc_tools_node_protoc

# Instalar herramientas necesarias para Ruby
.PHONY: install-ruby-tools
install-ruby-tools:
	@echo "Instalando herramientas necesarias para Ruby..."
	@if ! command -v gem >/dev/null 2>&1; then \
		echo "Ruby no está instalado. Por favor, instale Ruby primero."; \
		exit 1; \
	fi
	@if ! gem list grpc -i >/dev/null 2>&1; then \
		echo "Instalando gema grpc..."; \
		gem install grpc; \
	fi
	@if ! gem list grpc-tools -i >/dev/null 2>&1; then \
		echo "Instalando gema grpc-tools..."; \
		gem install grpc-tools; \
	fi
	@if ! gem list google-protobuf -i >/dev/null 2>&1; then \
		echo "Instalando gema google-protobuf..."; \
		gem install google-protobuf; \
	fi
	@echo "Herramientas de Ruby instaladas correctamente."

# Instalar herramientas necesarias para Node.js
.PHONY: install-node-tools
install-node-tools:
	@echo "Instalando herramientas necesarias para Node.js..."
	@if ! command -v npm >/dev/null 2>&1; then \
		echo "Node.js no está instalado. Por favor, instale Node.js primero."; \
		exit 1; \
	fi
	npm install -g grpc-tools
	npm install -g @grpc/proto-loader
	@echo "Herramientas de Node.js instaladas correctamente."

# Generar archivos gRPC
.PHONY: proto
proto: install-ruby-tools install-node-tools
	@echo "Generando archivos gRPC para Python..."
	$(PROTOC) -I=$(PROTO_DIR) --python_out=$(MASTER_DIR) --grpc_python_out=$(MASTER_DIR) $(PROTO_DIR)/master.proto
	$(PROTOC) -I=$(PROTO_DIR) --python_out=$(WORKER_DIR) --grpc_python_out=$(WORKER_DIR) $(PROTO_DIR)/master.proto
	@echo "Generando archivos gRPC para Ruby..."
	@if [ -z "$(RUBY_GRPC_PLUGIN)" ]; then \
		PLUGIN_PATH=$$(gem which grpc_tools_ruby_protoc_plugin | sed 's/\.rb$$//'); \
		if [ -z "$$PLUGIN_PATH" ]; then \
			echo "Error: No se puede encontrar grpc_tools_ruby_protoc_plugin"; \
			exit 1; \
		fi; \
		protoc -I=$(PROTO_DIR) \
			--ruby_out=$(WORKER_RUBY_DIR) \
			--plugin=protoc-gen-grpc=$$PLUGIN_PATH \
			--grpc_out=$(WORKER_RUBY_DIR) $(PROTO_DIR)/master.proto; \
	else \
		protoc -I=$(PROTO_DIR) \
			--ruby_out=$(WORKER_RUBY_DIR) \
			--plugin=protoc-gen-grpc=$(RUBY_GRPC_PLUGIN) \
			--grpc_out=$(WORKER_RUBY_DIR) $(PROTO_DIR)/master.proto; \
	fi
	@if [ $$? -eq 0 ]; then \
		sed -i 's|require "master_pb"|require_relative "master_pb"|' $(WORKER_RUBY_DIR)/master_services_pb.rb; \
		echo "Archivos gRPC para Ruby generados correctamente."; \
	else \
		echo "Error al generar archivos gRPC para Ruby."; \
		exit 1; \
	fi
	@echo "Generando archivos gRPC para Node.js..."
	$(GRPC_TOOLS_NODE_PROTOC) \
		--js_out=import_style=commonjs:$(WORKER_NODE_DIR) \
		--grpc_out=grpc_js:$(WORKER_NODE_DIR) \
		--proto_path=$(PROTO_DIR) \
		$(PROTO_DIR)/master.proto
	@echo "Archivos gRPC generados correctamente."

# Instalar dependencias globales
.PHONY: install
install: install-python install-node install-ruby install-redis
	@echo "Todas las dependencias han sido instaladas correctamente."

# Instalar dependencias de Python
.PHONY: install-python
install-python:
	@echo "Instalando dependencias de Python..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r $(MASTER_DIR)/requirements.txt
	$(PYTHON) -m pip install -r $(WORKER_DIR)/requirements.txt
	@echo "Dependencias de Python instaladas correctamente."

# Instalar dependencias de Node.js
.PHONY: install-node
install-node:
	@echo "Instalando dependencias de Node.js..."
	rm -rf $(WORKER_NODE_DIR)/node_modules $(WORKER_NODE_DIR)/package-lock.json
	npm install -g npm@latest
	cd $(WORKER_NODE_DIR) && npm install --force
	@echo "Dependencias de Node.js instaladas correctamente."

# Instalar dependencias de Ruby
.PHONY: install-ruby
install-ruby: install-ruby-tools
	@echo "Instalando dependencias de Ruby..."
	if ! gem list bundler -i > /dev/null; then \
	    gem install bundler; \
	fi
	cd $(WORKER_RUBY_DIR) && bundle install
	@echo "Dependencias de Ruby instaladas correctamente."

# Instalar Redis en Docker
.PHONY: install-redis
install-redis:
	@echo "Verificando si Redis está corriendo..."
	@if [ -z "$$(docker ps -q -f name=$(REDIS_CONTAINER))" ]; then \
		if [ -n "$$(docker ps -aq -f name=$(REDIS_CONTAINER))" ]; then \
			echo "Redis container encontrado, reiniciando..."; \
			docker start $(REDIS_CONTAINER); \
		else \
			echo "Redis container no encontrado, creando uno nuevo..."; \
			docker run -d --name $(REDIS_CONTAINER) -p 6379:6379 redis:latest; \
		fi \
	else \
		echo "Redis ya está en ejecución."; \
	fi
	@echo "Redis está en ejecución en el puerto 6379."

# Limpiar entornos y archivos generados
.PHONY: clean
clean:
	rm -f $(MASTER_DIR)/master_pb2.py $(MASTER_DIR)/master_pb2_grpc.py
	rm -f $(WORKER_DIR)/master_pb2.py $(WORKER_DIR)/master_pb2_grpc.py
	rm -f $(WORKER_RUBY_DIR)/master_pb.rb $(WORKER_RUBY_DIR)/master_services_pb.rb
	rm -rf $(WORKER_NODE_DIR)/node_modules $(WORKER_NODE_DIR)/package-lock.json
	@echo "Archivos generados y dependencias limpiadas."

# Ejecutar el Master
.PHONY: master
master:
	$(PYTHON) $(MASTER_DIR)/master.py

# Ejecutar un Worker en Python
.PHONY: worker-python
worker-python:
	$(PYTHON) $(WORKER_DIR)/worker.py

# Ejecutar un Worker en Ruby
.PHONY: worker-ruby
worker-ruby:
	cd $(WORKER_RUBY_DIR) && bundle exec ruby worker.rb

# Ejecutar un Worker en Node.js
.PHONY: worker-node
worker-node:
	cd $(WORKER_NODE_DIR) && node worker.js

# Parar y eliminar el contenedor de Redis
.PHONY: stop-redis
stop-redis:
	docker stop $(REDIS_CONTAINER)
	docker rm $(REDIS_CONTAINER)
	@echo "Redis detenido y eliminado."

# Ejecutar todo (Master y Workers)
.PHONY: run
run: proto install
	@echo "Iniciando Master y Workers..."
	$(PYTHON) $(MASTER_DIR)/master.py &      # Ejecuta el Master en segundo plano
	$(PYTHON) $(WORKER_DIR)/worker.py &      # Ejecuta un Worker Python en segundo plano
	cd $(WORKER_RUBY_DIR) && bundle exec ruby worker.rb & # Ejecuta el Worker Ruby en segundo plano
	cd $(WORKER_NODE_DIR) && node worker.js # Ejecuta el Worker Node.js 
