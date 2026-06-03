namespace MarketDataService.Domain.Interfaces
{
    public interface IDataStreamer : IDisposable
    {
        public Task ConnectAsync(string connectionString, CancellationToken cancellationToken);
        public Task StartAsync(CancellationToken cancellationToken);
        public Task<string> ReadAsync(CancellationToken cancellationToken);
        public Task DisconnetAsync(CancellationToken cancellationToken);

    }
}
