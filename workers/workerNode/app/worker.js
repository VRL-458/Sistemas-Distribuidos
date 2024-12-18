const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const mqtt = require('mqtt');

// Configuraciones de conexión
const GRPC_SERVER = 'localhost:50051';
const MQTT_BROKER = 'mqtt://localhost';

// Path del archivo .proto
const PROTO_PATH = '../proto/master.proto';

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
  });
  const grpcObject = grpc.loadPackageDefinition(packageDefinition);
  const masterProto = grpcObject.master;
  
  const grpcClient = new masterProto.Master(GRPC_SERVER, grpc.credentials.createInsecure());
  

// Conectar al broker MQTT
const mqttClient = mqtt.connect(MQTT_BROKER);

// Función para registrarse con el Master
function registerWithMaster() {
  return new Promise((resolve, reject) => {
    grpcClient.RegisterWorker({}, (error, response) => {
      if (error) {
        console.error('Error al registrar el Worker:', error);
        reject(error);
      } else {
        const workerId = response.worker_id;
        console.log(`Worker registrado con ID: ${workerId}`);
        resolve(workerId);
      }
    });
  });
}

// Función para enviar logs al Master
function sendLog(workerId, sensorId, freq, iteration) {
  return new Promise((resolve, reject) => {
    const logRequest = {
      worker_id: workerId,
      sensor_id: sensorId,
      freq: freq,
      iteration: iteration,
    };

    grpcClient.Log(logRequest, (error, response) => {
      if (error) {
        console.error('Error al enviar log:', error);
        reject(error);
      } else {
        console.log(`Log enviado al Master. Respuesta: ${response.status}`);
        resolve();
      }
    });
  });
}

// Función principal
async function main() {
  try {
    // Conexión y registro
    const workerId = await registerWithMaster();

    // Simulación de tareas
    await sendLog(workerId, 'sensor_01', 0.5, 10);
    await sendLog(workerId, 'sensor_02', 0.3, 7);

    // Conexión al MQTT Broker
    mqttClient.on('connect', () => {
      console.log('Conectado al broker MQTT');
      mqttClient.subscribe('worker/logs');
    });

    mqttClient.on('message', (topic, message) => {
      console.log(`Mensaje recibido [${topic}]: ${message.toString()}`);
    });
  } catch (error) {
    console.error('Error en el Worker:', error);
  }
}

main();
