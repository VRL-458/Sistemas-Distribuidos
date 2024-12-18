
# Variables
IMAGE_PYTHON="10.1.2.151:5000/worker_python"
IMAGE_RUBY="10.1.2.151:5000/worker_ruby"
#IMAGE_NODEJS="10.1.2.151:5000/worker_nodejs"
#IMAGE_C++="10.1.2.151:5000/worker_c++"



# Crear (build) la imagen
docker build -t $IMAGE_PYTHON -f workers/workerPython/app/Dockerfile .
docker build -t $IMAGE_RUBY -f  workers/workerRuby/app/Dockerfile .
#docker build -t $IMAGE_NODEJS -f worker/Dockerfile .
#docker build -t $IMAGE_C++ -f worker/Dockerfile .

