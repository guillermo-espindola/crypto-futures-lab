using MarketDataService.Domain.Interfaces;
using MarketDataService.Infrastructure.Clients;
using MarketDataService.Ingestion;
using MarketDataService.Ingestion.Models;
using StreamBus.Gateway.Abstractions;
using StreamBus.Gateway.Kafka;

var builder = Host.CreateApplicationBuilder(args);

builder.Services.Configure<IngestionSettings>(builder.Configuration.GetSection(nameof(IngestionSettings)));

builder.Services.AddTransient<IDataStreamer, WebSocketClient>();
builder.Services.AddSingleton<IMessagePublisher, KafkaPublisher>();

builder.Services.AddHostedService<Worker>();

var host = builder.Build();
host.Run();
