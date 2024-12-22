using Grpc.Net.Client;
using WorkerCSharp;
using WorkerCSharp.Managers;

string HOSTNAME = Environment.GetEnvironmentVariable("HOSTNAME");
string MQTT_BROKER = "mqtt";//Environment.GetEnvironmentVariable("MQTT_BROKER");
int MQTT_PORT = 1883; //Environment.GetEnvironmentVariable("MQTT_BROKER");
string MASTER_ADD = "master";//Environment.GetEnvironmentVariable("MASTER_ADD");


using var channel = GrpcChannel.ForAddress(MASTER_ADD);
var client = new Master.MasterClient(channel);
var reply = client.RegisterWorker(new RegisterWorkerRequest { WorkerId = HOSTNAME});



MQTTManager mqtt = new MQTTManager(MQTT_BROKER, MQTT_PORT, HOSTNAME, client);


Console.ReadKey();

