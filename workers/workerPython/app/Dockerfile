
FROM python:3.9-slim


WORKDIR /app

# dependencias necesarias para gRPC
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY workers/workerPython/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


#archivos gRPC
COPY workers/workerPython/proto ./proto
RUN python3 -m grpc_tools.protoc -I=./proto --python_out=. --grpc_python_out=. ./proto/master.proto

COPY workers/workerPython/app/worker.py .

COPY wait_for_it/ ./wait_for_it


#wit for it  and excecute worker
CMD ["sh", "-c", "wait_for_it/wait-for-it.sh master:8888 --timeout=50 --strict && python -u worker.py"]
