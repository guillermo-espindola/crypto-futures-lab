namespace StreamBus.Gateway.Abstractions
{
    public interface IMessagePublisher : IDisposable
    {
        public Task PublishAsync<TMessage>(string topic, TMessage message, CancellationToken cancellationToken);
        public Task ConnectAsync(string stringConnection);
    }
}
