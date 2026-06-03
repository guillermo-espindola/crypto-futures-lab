namespace StreamBus.Gateway.Kafka
{
    using StreamBus.Gateway.Abstractions;
    using Confluent.Kafka;
    public class KafkaPublisher : IMessagePublisher
    {
        private IProducer<Null, string>? _producer;

        public Task ConnectAsync(string connectionString)
        {
            var config = new ProducerConfig
            {
                BootstrapServers = connectionString,
            };
            _producer = new ProducerBuilder<Null, string>(config).Build();

            return Task.CompletedTask;
        }

        public void Dispose()
        {
            _producer?.Dispose();
            GC.SuppressFinalize(this);
        }

        public async Task PublishAsync<TMessage>(string topic, TMessage message, CancellationToken cancellationToken)
        {
            await _producer!.ProduceAsync(topic,
                new Message<Null, string>
                {
                    Value = message?.ToString()!
                }, cancellationToken);
        }
    }
}
