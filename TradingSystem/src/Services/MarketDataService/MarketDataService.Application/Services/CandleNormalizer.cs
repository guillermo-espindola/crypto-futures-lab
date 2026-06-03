using MarketDataService.Application.Interfaces;
using MarketDataService.Domain.Models;
using System.Text.Json;

namespace MarketDataService.Application.Services
{
    public class CandleNormalizer : INormalizer<Candle>
    {
        public Candle Normalize(string data)
        {
            var jsonData = JsonDocument.Parse(data);
            var kline = jsonData.RootElement.GetProperty("k");

            return new Candle()
            {
                Symbol = kline.GetProperty("s").GetString(),
                Open = decimal.Parse(kline.GetProperty("o").GetString()!),
                Close = decimal.Parse(kline.GetProperty("c").GetString()!),
                High = decimal.Parse(kline.GetProperty("h").GetString()!),
                Low = decimal.Parse(kline.GetProperty("l").GetString()!),
                Volume = decimal.Parse(kline.GetProperty("v").GetString()!),
                Timestamp = kline.GetProperty("t").GetInt64(),
            };
        }
    }
}
