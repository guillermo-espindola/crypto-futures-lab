namespace MarketDataService.Application.Test.Services
{
    using FluentAssertions;
    using MarketDataService.Application.Interfaces;
    using MarketDataService.Application.Services;
    using MarketDataService.Domain.Models;
    public class CandleNormalizerTest
    {
        [Fact]
        public void Normalize_ValidCandleString_ResultCandle()
        {
            var candleData = """
                                {  
                  "e": "kline",
                  "E": 1638747660000,
                  "s": "BTCUSDT",
                  "k": {    
                         "t": 1638747660000,
                         "T": 1638747719999,
                         "s": "BTCUSDT",
                         "i": "1m",
                         "f": 100,
                         "L": 200,
                         "o": "0.0010",
                         "c": "0.0020",
                         "h": "0.0025",
                         "l": "0.0015",
                         "v": "1000",
                         "n": 100,
                         "x": false,
                         "q": "1.0000",
                         "V": "500",
                         "Q": "0.500",
                         "B": "123456"
                       }
                }
                
                """;

            INormalizer<Candle> candleNormalizer = new CandleNormalizer();

            var candle = candleNormalizer.Normalize(candleData);

            candle.Should().NotBeNull();
            candle.Symbol.Should().Be("BTCUSDT");
            candle.Open.Should().Be(0.0010M);
            candle.Close.Should().Be(0.0020M);
            candle.High.Should().Be(0.0025M);
            candle.Low.Should().Be(0.0015M);
            candle.Volume.Should().Be(1000);
            candle.Timestamp.Should().Be(1638747660000);
        }
    }
}
