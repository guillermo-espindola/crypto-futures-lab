namespace MarketDataService.Ingestion.Models
{
    public class IngestionSettings
    {
        public TransportSettings? Transport { get; set; }
        public DestinationSettings? Destination { get; set; }
        public List<StreamSettings> Streams { get; set; } = new List<StreamSettings>();
    }
}
