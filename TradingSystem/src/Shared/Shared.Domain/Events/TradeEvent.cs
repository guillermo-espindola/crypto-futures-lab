namespace Shared.Domain.Events
{
    public class TradeEvent
    {
        // "e": "aggTrade", // Event type
        public string? EventType { get; set; }

        // "E": 123456789,  // Event time
        public Int64 EventTime { get; set; }

        // "s": "BTCUSDT",  // Symbol
        public string? Symbol { get; set; }

        // "a": 5933014,    // Aggregate trade ID
        public int AggregateTradeId { get; set; }

        // "p": "0.001",    // Price  
        public string? Price { get; set; }

        // "q": "100",      // Quantity with all the market trades
        public string? MarketTradesQuantity { get; set; }

        // "nq": "100",     // Normal quantity without the trades involving RPI orders
        public string? NormalQuantity { get; set; }

        // "f": 100,        // First trade ID
        public int FirstTradeId { get; set; }

        // "l": 105,        // Last trade ID  
        public int LastTradeId { get; set; }

        // "T": 123456785,  // Trade time
        public Int64 TradeTime { get; set; }

        // "m": true,       // Is the buyer the market maker?
        public bool IsMarketMaker { get; set; }

    }
}
