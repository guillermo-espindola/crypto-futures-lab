namespace Shared.Domain.Events
{
    public class LiquidationEvent
    {
        // "e":"forceOrder",    // Event Type    
        public string? EventType { get; set; }

        // "E":1568014460893,   // Event Time
        public Int64 EventTime { get; set; }

        // "o":{}  //OrderEvent
        public OrderEvent? Order { get; set; }

    }
}
