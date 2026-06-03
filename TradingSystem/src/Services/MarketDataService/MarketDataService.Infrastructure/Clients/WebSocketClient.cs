namespace MarketDataService.Infrastructure.Clients
{
    using MarketDataService.Domain.Interfaces;
    using System.Net.WebSockets;
    using System.Text;
    using System.Threading.Channels;
    public class WebSocketClient : IDataStreamer
    {
        private readonly ClientWebSocket _clientWebSocket;
        private readonly Channel<string> _channel;
        private readonly byte[] _buffer;

        public WebSocketClient()
        {
            _clientWebSocket = new ClientWebSocket();
            _channel = Channel.CreateUnbounded<string>(new UnboundedChannelOptions { SingleReader = true, SingleWriter = false });
            _buffer = new byte[64 * 1024];
        }

        public async Task ConnectAsync(string connectionString, CancellationToken cancellationToken)
        {
            await _clientWebSocket.ConnectAsync(new Uri(connectionString), cancellationToken);
        }

        public async Task DisconnetAsync(CancellationToken cancellationToken)
        {
            if (_clientWebSocket.State == WebSocketState.Open)
            {
                await _clientWebSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Disconnect", cancellationToken);
            }
        }

        public void Dispose()
        {
            _clientWebSocket.Dispose();
            _channel.Writer.TryComplete();
            GC.SuppressFinalize(this);
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            WebSocketReceiveResult webSockectReceiveResult;
            
            while (_clientWebSocket.State == WebSocketState.Open && 
                !cancellationToken.IsCancellationRequested)
            {
                do
                {
                    webSockectReceiveResult = await _clientWebSocket.ReceiveAsync(_buffer, cancellationToken);

                } while (!webSockectReceiveResult.EndOfMessage);

                if (webSockectReceiveResult.MessageType == WebSocketMessageType.Close)
                {
                    await DisconnetAsync(cancellationToken);
                    break;
                }
                
                await _channel.Writer.WriteAsync(Encoding.UTF8.GetString(_buffer, 0, webSockectReceiveResult.Count), cancellationToken);
            }
        }

        public async Task<string> ReadAsync(CancellationToken cancellationToken)
        {
            var message = await _channel.Reader.ReadAsync(cancellationToken);
            return message;

        }
    }
}
