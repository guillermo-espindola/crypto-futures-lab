namespace Shared.Domain.Events
{
    public class CandleEvent
    {
        // "e": "kline",     // Event type 
        public string? EventType { get; set; }

        // "E": 1638747660000,   // Event time
        public Int64 EventTime { get; set; }

        // "s": "BTCUSDT",    // Symbol
        public string? Symbol { get; set; }

        // "k": {}  // Kline
        public KlineEvent? Kline { get; set; }
    }
}
