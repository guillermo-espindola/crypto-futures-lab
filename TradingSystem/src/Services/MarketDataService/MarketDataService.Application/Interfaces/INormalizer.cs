namespace MarketDataService.Application.Interfaces
{
    public interface INormalizer<TType>
    {
        public TType Normalize(string data);
    }
}
