namespace Shared.Domain.Events
{
    public class OrderBookEvent
    {
        // "e": "depthUpdate", // Event type  
        public string? EventType { get; set; }

        // "E": 1571889248277, // Event time  
        public Int64 EventTime { get; set; }

        // "s": "BTCUSDT",  // Symbol
        public string? Symbol { get; set; }

        // "T": 1571889248276, // Transaction time
        public Int64 TransactionTime { get; set; }

        // "U": 390497796,     // First update ID in event
        public int FirstUpdateId { get; set; }

        // "u": 390497878,     // Final update ID in event  
        public int FinalUpdateId { get; set; }

        // "pu": 390497794,    // Final update Id in last stream(ie `u` in last stream)
        public int FinalUpdateLastId { get; set; }

        /* "b": [              // Bids to be updated 
                  [
                   "7403.89",      // Price Level to be updated      
                    "0.002"        // Quantity    
                  ]
                ],
        */
        public List<List<string>> BidsToBeUpdated { get; set; } = new List<List<string>>();

        /* "a": [              // Asks to be updated    
                  [
                    "7405.96",      // Price level to be updated
                    "3.340"         // Quantity    
                  ]
                ]
        */
        public List<List<string>> AsksToBeUpdated { get; set; } = new List<List<string>>();
    }
}
