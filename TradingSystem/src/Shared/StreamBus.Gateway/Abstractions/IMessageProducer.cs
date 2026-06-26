namespace StreamBus.Gateway.Abstractions
{
    public interface IMessageProducer : IDisposable
    {
        public Task ProduceAsync<TMessage>(string topic, TMessage message, CancellationToken cancellationToken);
        public Task ConnectAsync(string stringConnection);
    }
}
