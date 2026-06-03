using Confluent.Kafka;

namespace StreamBus.Gateway.Kafka
{
    public class KafkaConsumer
    {
        public void Consume()
        {
            var config = new ConsumerConfig
            {
                BootstrapServers = "localhost:29092",
                GroupId = "Candles-Consumer",
                AutoOffsetReset = AutoOffsetReset.Earliest,
                EnableAutoCommit = true,

            };

            using var consumer = new ConsumerBuilder<Ignore, string>(config).Build();
            consumer.Subscribe("Candles");
            Console.WriteLine("Esperando mensajes");

            CancellationTokenSource cts = new CancellationTokenSource();

            Console.CancelKeyPress += (_, e) =>
            {
                e.Cancel = true;
                cts.Cancel();
            };

            while(!cts.Token.IsCancellationRequested)
            {
                var result = consumer.Consume(cts.Token);
                Console.WriteLine($"{result.Offset.Value} - {result.Message.Value}");
            }

        }
    }
}
