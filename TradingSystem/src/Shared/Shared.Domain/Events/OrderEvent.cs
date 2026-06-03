namespace Shared.Domain.Events
{
    public class OrderEvent
    {
        // "s":"BTCUSDT", // Symbol
        public string? Symbol { get; set; }

        // "S":"SELL",    // Side
        public string? Side { get; set; }

        // "o":"LIMIT",   // Order Type
        public string? OrderType { get; set; }

        // "f":"IOC",     // Time in Force 
        public string? TimeInForce { get; set; }

        // "q":"0.014",   // Original Quantity
        public string? OriginalQuantity { get; set; }

        // "p":"9910",    // Price        
        public string? Price { get; set; }

        // "ap":"9910",   // Average Price
        public string? AveragePrice { get; set; }

        // "X":"FILLED",  // Order Status
        public string? OrderStatus { get; set; }

        // "l":"0.014",   // Order Last Filled Quantity
        public string? OrderLastFilledQuantity { get; set; }

        // "z":"0.014",   // Order Filled Accumulated Quantity
        public string? OrderFilledAccumulatedQuantity { get; set; }

        // "T":1568014460893,  // Order Trade Time
        public Int64 TradeTime { get; set; }
    }
}
