
FROM python:3.9-slim

# directorio de trabajo
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY master/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia la carpeta proto y genera los archivos gRPC
COPY master/proto ./proto
RUN python3 -m grpc_tools.protoc -I=./proto --python_out=. --grpc_python_out=. ./proto/master.proto

#copia de wait_for_t
COPY wait_for_it/ ./wait_for_it 


COPY master/master.py .

EXPOSE 8888

CMD ["sh", "-c", "wait_for_it/wait-for-it.sh mqtt:1883 --timeout=50 --strict && wait_for_it/wait-for-it.sh redis:6379 --timeout=50 --strict && python -u master.py"]
#CMD ["sh", "-c", "wait_for_it/wait-for-it.sh redis:6379 --timeout=30 --strict && python master.py"]
#CMD ["python", "master.py"]
