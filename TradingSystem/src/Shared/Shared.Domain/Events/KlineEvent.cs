namespace Shared.Domain.Events
{
    public class KlineEvent
    {
        // "t": 1638747660000, // Kline start time
        public Int64 StartTime { get; set; }

        // "T": 1638747719999, // Kline close time
        public Int64 CloseTime { get; set; }

        // "s": "BTCUSDT",  // Symbol
        public string? Symbol { get; set; }

        // "i": "1m",      // Interval
        public string? Interval { get; set; }

        // "f": 100,       // First trade ID 
        public int FirstTradeId { get; set; }

        // "L": 200,       // Last trade ID
        public int LastTradeId { get; set; }

        // "o": "0.0010",  // Open price    
        public string? OpenPrice { get; set; }

        // "c": "0.0020",  // Close price
        public string? ClosePrice { get; set; }

        // "h": "0.0025",  // High price
        public string? HighPrice { get; set; }

        // "l": "0.0015",  // Low price
        public string? LowPrice { get; set; }

        // "v": "1000",    // Base asset volume
        public string? BaseAssetVolume { get; set; }

        // "n": 100,       // Number of trades    
        public int NumberOfTrades { get; set; }

        // "x": false,     // Is this kline closed?
        public bool IsClosed { get; set; }

        // "q": "1.0000",  // Quote asset volume
        public string? QuoteAssetVolume { get; set; }

        // "V": "500",     // Taker buy base asset volume
        public string? TakerBuyBaseAssetVolume { get; set; }

        //"Q": "0.500",   // Taker buy quote asset volume    
        public string? TakerBuyQuoteAssetVolume { get; set; }

        // "B": "123456"   // Ignore
        public string? Ignore { get; set; }
    }
}
