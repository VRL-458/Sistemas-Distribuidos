using Google.Protobuf.WellKnownTypes;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;

namespace WorkerCSharp.Managers
{
    internal class MQTTManager
    {
        private readonly string brokerAddress;
        private readonly int port;
        private static string hostname;
        private readonly string[] subTopic;
        private static string pubTopic;
        private static MqttClient mqttClient;
        private static Random rand;
        private static Master.MasterClient grpcClient;

        public MQTTManager(string brokerAddress, int port, string hostname, Master.MasterClient grpcClient)
        {
            this.brokerAddress = brokerAddress;
            this.port = port;
            MQTTManager.hostname = hostname;
            MQTTManager.grpcClient = grpcClient;


            this.subTopic = new string[] { $"upb/{hostname}/request" };
            pubTopic = $"upb/{hostname}/response";


            mqttClient = CreateMqttClient();
            rand = new Random();
            InitializeMqttClient(mqttClient);
        }

        private MqttClient CreateMqttClient()
        {
            IPAddress ipv4Address = Array.Find(Dns.GetHostAddresses(brokerAddress), a => a.AddressFamily == AddressFamily.InterNetwork);
            if (ipv4Address == null)
                throw new Exception("No IPv4 address found for the broker.");

            return new MqttClient(ipv4Address.ToString(), port, false, null, null, MqttSslProtocols.None);
        }

        private void InitializeMqttClient(MqttClient client)
        {
            mqttClient = client;
            mqttClient.MqttMsgPublishReceived += MQTTMessageReceived;
            mqttClient.Subscribe(subTopic, new byte[] { MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE });
            mqttClient.Connect(hostname);
            Console.WriteLine("MQTT Client Initialized");
        }

        public static void MQTTMessageReceived(object sender, MqttMsgPublishEventArgs e)
        {
            try
            {
                string receivedMessage = Encoding.UTF8.GetString(e.Message);
                Console.WriteLine($"Message received on topic '{e.Topic}': {receivedMessage}");
                float freq = (float)(rand.NextDouble());
                int iteration = rand.Next(5, 10);

                var mqttMsg = new
                {
                    freq,
                    iteration
                };

                string jsonMessage = JsonSerializer.Serialize(mqttMsg);
                mqttClient.Publish(pubTopic, Encoding.UTF8.GetBytes(jsonMessage), MqttMsgBase.QOS_LEVEL_EXACTLY_ONCE, false);

                GrpcLog(receivedMessage, hostname, freq, iteration, grpcClient);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing received message: {ex.Message}");
            }
        }

        private static void GrpcLog(string message, string hostname, float freq, int iteration, Master.MasterClient grpcClient)
        {
            var parsed = JsonSerializer.Deserialize<Dictionary<string, string>>(message);
            if (parsed != null && parsed.TryGetValue("sensor_id", out string sensorId))
            {
                Console.WriteLine("GRPC LOG");
                LogRequest logRequest = new LogRequest { WorkerId = hostname, Freq = freq, Iteration = iteration, SensorId = sensorId };
                grpcClient.Log(logRequest);
            }
        }
    }
}
