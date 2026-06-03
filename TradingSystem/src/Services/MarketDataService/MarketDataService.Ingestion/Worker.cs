namespace MarketDataService.Ingestion
{
    using MarketDataService.Domain.Interfaces;
    using MarketDataService.Ingestion.Models;
    using Microsoft.Extensions.Options;
    using StreamBus.Gateway.Abstractions;
    public class Worker : BackgroundService
    {
        private readonly ILogger<Worker> _logger;        
        private readonly IngestionSettings _ingestionSettings;
        private readonly List<IDataStreamer> _dataStreamers;
        private readonly IMessagePublisher _messagePublisher;
        private readonly IServiceProvider _serviceProvider;

        public Worker(ILogger<Worker> logger,
             IOptions<IngestionSettings> ingestionSettings,
             IMessagePublisher messagePublisher,
             IServiceProvider serviceProvider)
        {
            _logger = logger;
            _ingestionSettings = ingestionSettings.Value;
            _dataStreamers = new List<IDataStreamer>();
            _messagePublisher = messagePublisher;
            _serviceProvider = serviceProvider;
        }
        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Worker running at: {time}", DateTimeOffset.Now);
            
            var taskList = new List<Task>();
            await _messagePublisher.ConnectAsync(_ingestionSettings?.Destination?.Connection!);
            foreach (var streamSettings in _ingestionSettings?.Streams!)
            {
                var webSocketClient = _serviceProvider.GetRequiredService<IDataStreamer>();
                _dataStreamers.Add(webSocketClient);
                await webSocketClient.ConnectAsync($"{_ingestionSettings.Transport?.BaseUrl}{streamSettings.Route}{streamSettings.Parameters}", stoppingToken);

                taskList.Add(StartDataStreamerAsync(webSocketClient, streamSettings.Name!, stoppingToken));
                taskList.Add(IngestDataAsync(webSocketClient, streamSettings.Name!, stoppingToken));
            }

            await Task.WhenAny(taskList);
        }

        public async Task StartDataStreamerAsync(IDataStreamer dataStreamer, string name, CancellationToken cancellationToken)
        {
            _logger.LogInformation($"Starting DataStreamer {name} at: {DateTimeOffset.Now}");
            
            await dataStreamer.StartAsync(cancellationToken);
        }

        public async Task IngestDataAsync(IDataStreamer dataStreamer, string name, CancellationToken cancellationToken)
        {
            _logger.LogInformation($"Ingesting {name} at: {DateTimeOffset.Now}");
            
            while (!cancellationToken.IsCancellationRequested)
            {
                var result = await dataStreamer.ReadAsync(cancellationToken);
                
                //_logger.LogDebug($"**{name}** {result}");

                await _messagePublisher.PublishAsync(name, result, cancellationToken);
            }
        }
        public override void Dispose()
        {
            _messagePublisher.Dispose();
            foreach (var dataStreamer in _dataStreamers)
            {
                dataStreamer.Dispose();
            }

            base.Dispose();
            GC.SuppressFinalize(this);
        }
    }
}
