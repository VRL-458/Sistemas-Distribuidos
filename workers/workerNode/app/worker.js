const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const mqtt = require('mqtt');

// Configuraciones de conexión
const GRPC_SERVER = 'localhost:50051';
const MQTT_BROKER = 'mqtt://research.upb.edu';
const PROTO_PATH = '../proto/master.proto';

// Cargar la definición del .proto
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

// Cargar el servicio gRPC
const grpcObject = grpc.loadPackageDefinition(packageDefinition);
const masterProto = grpcObject.master;

// Crear cliente gRPC
const grpcClient = new masterProto.Master(GRPC_SERVER, grpc.credentials.createInsecure());

// Clase WorkerManager para manejar el Worker ID
class WorkerManager {
  constructor(grpcClient) {
    this.grpcClient = grpcClient;
  }

  async register(workerId) {
    return new Promise((resolve, reject) => {
      this.grpcClient.RegisterWorker({ worker_id: workerId }, (error, response) => {
        if (error) {
          console.error('Error al registrar el Worker:', error);
          reject(error);
        } else {
          console.log(`Worker registrado con ID: ${workerId}`);
          resolve(workerId);
        }
      });
    });
  }
}

// Función para enviar logs al Master
function sendLog(grpcClient, workerId, sensorId, freq, iteration) {
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
        console.log(
          `Log enviado al Master: Worker ${workerId}, Sensor ${sensorId}, Freq=${freq}, Iteration=${iteration}, Respuesta: ${response.status}`
        );
        resolve(response);
      }
    });
  });
}

// Función principal
async function main() {
  try {
    // Crear una instancia de WorkerManager y registrar el Worker
    const workerId = 'ccc'; // ID del Worker
    const workerManager = new WorkerManager(grpcClient);
    await workerManager.register(workerId);

    // Paso 2: Configurar el cliente MQTT
    const mqttClient = mqtt.connect(MQTT_BROKER, {
      port: 1883,
      keepalive: 60,
      reconnectPeriod: 1000,
      connectTimeout: 30 * 1000,
    });

    // Configurar las opciones del cliente MQTT
    mqttClient.on('connect', () => {
      console.log('Conectado al broker MQTT');

      // Suscribirse al tópico de solicitudes específico del worker
      const requestTopic = `upb/${workerId}/request`;
      mqttClient.subscribe(requestTopic, (err) => {
        if (err) {
          console.error('Error al suscribirse:', err);
        } else {
          console.log(`Worker ${workerId} suscrito al tópico: ${requestTopic}`);
        }
      });
    });

    // Manejar los mensajes MQTT recibidos
    mqttClient.on('message', async (topic, message) => {
      try {
        // Decodificar el mensaje
        const payload = JSON.parse(message.toString());
        console.log(`Mensaje recibido en ${topic}: ${JSON.stringify(payload)}`);

        // Extraer datos del mensaje
        const sensorId = payload.sensor_id;

        // Generar valores aleatorios
        const freq = Number((Math.random() * 0.9 + 0.1).toFixed(2)); // Frecuencia [0.1 - 1] con 2 decimales
        const iteration = Math.floor(Math.random() * 6 + 5); // Iteración [5 - 10] enteros

        console.log(
          `Worker ${workerId}: Tarea recibida de ${sensorId}. Freq=${freq}, Iteration=${iteration}`
        );

        // Enviar log al Master
        await sendLog(grpcClient, workerId, sensorId, freq, iteration);

        // Publicar respuesta al ESP32 en el tópico correspondiente
        const responseTopic = `upb/${workerId}/response`;
        const responseMessage = { freq, iteration };
        mqttClient.publish(responseTopic, JSON.stringify(responseMessage));
        console.log(`Respuesta publicada en ${responseTopic}: ${JSON.stringify(responseMessage)}`);
      } catch (error) {
        console.error('Error procesando mensaje:', error);
      }
    });

    // Manejar errores de MQTT
    mqttClient.on('error', (error) => {
      console.error('Error en la conexión MQTT:', error);
    });

    // Manejar desconexión
    mqttClient.on('close', () => {
      console.log('Conexión MQTT cerrada');
    });
  } catch (error) {
    console.error('Error en el Worker:', error);
  }
}

// Iniciar el worker
main();
