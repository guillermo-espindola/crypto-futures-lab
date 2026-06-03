# Arquitectura Profesional .NET 8 — Sistema Quant Crypto Futures

---

# OBJETIVO

Sistema distribuido para:

- ingestión en tiempo real desde Binance Futures
- procesamiento de microestructura
- generación de features cuantitativos
- predicción probabilística
- análisis multi-timeframe
- inferencia ML/IA
- gestión de riesgo
- ejecución automatizada

---

# ARQUITECTURA GENERAL

```text
                    ┌────────────────────┐
                    │ Binance Futures WS │
                    └─────────┬──────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │ MarketDataService        │
                │ (.NET Worker)            │
                └──────────┬───────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │ Redis Streams / Kafka    │
                │ (Stream Bus)             │
                └──────────┬───────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌────────────────┐  ┌────────────────┐
│ FeatureEngine│  │ MLService      │  │ MonitoringSvc  │
│ Worker       │  │ Worker/API     │  │ Worker         │
└──────┬───────┘  └────────┬───────┘  └────────────────┘
       │                   │
       ▼                   ▼
┌──────────────┐  ┌────────────────┐
│ RiskEngine   │  │ Dashboard API  │
│ Worker       │  │ ASP.NET API    │
└──────┬───────┘  └────────────────┘
       │
       ▼
┌──────────────┐
│ ExecutionSvc │
│ Worker       │
└──────────────┘
```

---

# ESTRUCTURA COMPLETA DE LA SOLUTION

```text
TradingSystem.sln
│
├── src/
│
│   ├── Shared/
│   │
│   │   ├── Shared.Contracts/
│   │   ├── Shared.Domain/
│   │   ├── Shared.Indicators/
│   │   ├── Shared.Serialization/
│   │   ├── Shared.TimeSeries/
│   │   ├── StreamBus.Gateway/
│   │
│   ├── Services/
│   │
│   │   ├── MarketDataService/
│   │   ├── FeatureEngine/
│   │   ├── MLService/
│   │   ├── RiskEngine/
│   │   ├── ExecutionService/
│   │   ├── MonitoringService/
│   │
│   ├── Api/
│   │
│   │   ├── Dashboard.Api/
│   │
│   ├── Infrastructure/
│   │
│   │   ├── Redis.Infrastructure/
│   │   ├── Kafka.Infrastructure/
│   │   ├── Mongo.Infrastructure/
│   │   ├── ClickHouse.Infrastructure/
│
├── tests/
│
│   ├── UnitTests/
│   ├── IntegrationTests/
│   ├── BacktestingTests/
│
├── deploy/
│
│   ├── docker/
│   ├── kubernetes/
│
├── docs/
│
│   ├── architecture.md
│   ├── pipelines.md
│   ├── indicators.md
│```

---

# TIPOS DE PROYECTO

| Proyecto | Tipo |
|---|---|
| Shared.Contracts | Class Library |
| Shared.Indicators | Class Library |
| StreamBus.Gateway | Class Library |
| MarketDataService | Worker Service |
| FeatureEngine | Worker Service |
| RiskEngine | Worker Service |
| ExecutionService | Worker Service |
| MLService | Worker/API |
| Dashboard.Api | ASP.NET Core API |

---

# SHARED.CONTRACTS

## RESPONSABILIDAD

Contener todos los DTOs/eventos compartidos.

---

## ESTRUCTURA

```text
Shared.Contracts/
│
├── Events/
│   ├── CandleEvent.cs
│   ├── TradeEvent.cs
│   ├── OrderbookEvent.cs
│   ├── FeatureVectorEvent.cs
│   ├── PredictionEvent.cs
│
├── Models/
│   ├── Candle.cs
│   ├── OrderbookLevel.cs
│
├── Enums/
│   ├── Timeframe.cs
│   ├── SignalType.cs
```

---

# EJEMPLO EVENTO

```csharp
public class CandleEvent
{
    public string Symbol { get; set; }

    public string Timeframe { get; set; }

    public decimal Open { get; set; }

    public decimal High { get; set; }

    public decimal Low { get; set; }

    public decimal Close { get; set; }

    public decimal Volume { get; set; }

    public decimal TakerBuyVolume { get; set; }

    public long Timestamp { get; set; }
}
```

---

# SHARED.INDICATORS

## RESPONSABILIDAD

Toda lógica cuantitativa reusable.

---

# ESTRUCTURA

```text
Shared.Indicators/
│
├── Momentum/
│   ├── MomentumIndicator.cs
│
├── Volatility/
│   ├── AtrIndicator.cs
│   ├── VolatilityRegime.cs
│
├── Orderflow/
│   ├── BuyPressure.cs
│   ├── DeltaImbalance.cs
│
├── Trend/
│   ├── EmaTrend.cs
│   ├── MarketStructure.cs
```

---

# EJEMPLO ATR

```csharp
public static class AtrIndicator
{
    public static decimal Calculate(
        decimal high,
        decimal low,
        decimal prevClose)
    {
        var tr1 = high - low;
        var tr2 = Math.Abs(high - prevClose);
        var tr3 = Math.Abs(low - prevClose);

        return Math.Max(tr1,
            Math.Max(tr2, tr3));
    }
}
```

---

# STREAMBUS.GATEWAY

## TIPO

```text
Class Library
```

---

# RESPONSABILIDAD

Abstracción sobre Redis/Kafka.

---

# ESTRUCTURA

```text
StreamBus.Gateway/
│
├── Abstractions/
│   ├── IMessagePublisher.cs
│   ├── IMessageConsumer.cs
│
├── Redis/
│   ├── RedisStreamPublisher.cs
│   ├── RedisStreamConsumer.cs
│
├── Kafka/
│   ├── KafkaPublisher.cs
│   ├── KafkaConsumer.cs
│
├── Serialization/
│   ├── JsonEventSerializer.cs
```

---

# INTERFAZ

```csharp
public interface IMessagePublisher
{
    Task PublishAsync<T>(
        string stream,
        T message);
}
```

---

# MARKETDATASERVICE

## TIPO

```text
Worker Service
```

---

# RESPONSABILIDAD

- conexión Binance WS
- normalización
- publicación de eventos

---

# ESTRUCTURA

```text
MarketDataService/
│
├── Workers/
│   ├── BinanceKlineWorker.cs
│   ├── BinanceTradeWorker.cs
│
├── Clients/
│   ├── BinanceWsClient.cs
│
├── Parsers/
│   ├── KlineParser.cs
│
├── Publishers/
│   ├── CandlePublisher.cs
```

---

# FLUJO

```text
Binance WS
    ↓
Parser
    ↓
Normalizer
    ↓
Redis Streams
```

---

# FEATUREENGINE

## TIPO

```text
Worker Service
```

---

# RESPONSABILIDAD

- consumir candles
- generar features cuantitativos
- publicar feature vectors

---

# ESTRUCTURA

```text
FeatureEngine/
│
├── Workers/
│   ├── CandleFeatureWorker.cs
│
├── Calculators/
│   ├── MomentumCalculator.cs
│   ├── VolatilityCalculator.cs
│
├── Pipelines/
│   ├── FeaturePipeline.cs
```

---

# FEATURES IMPORTANTES

| Feature | Fórmula |
|---|---|
| Buy Pressure | takerBuy / volume |
| Momentum | (close-prevClose)/ATR |
| ATR | EMA(TrueRange) |
| VWAP Distance | (price-vwap)/ATR |
| Trade Intensity | trades/volume |
| OBI | (bid-ask)/(bid+ask) |

---

# MLSERVICE

## OPCIÓN RECOMENDADA

```text
Python ML + ONNX Runtime en C#
```

---

# MODELOS

| Modelo | Uso |
|---|---|
| LightGBM | clasificación |
| XGBoost | probabilidades |
| TFT | secuencias |
| CNN | orderbook |
| LSTM | momentum |

---

# PIPELINE

```text
Feature Vectors
    ↓
Model Inference
    ↓
Prediction Event
```

---

# RISKENGINE

## RESPONSABILIDAD

- filtrar señales
- sizing
- riesgo dinámico

---

# FILTROS

```csharp
if(probability < 0.72)
    reject();

if(atr > maxAtr)
    reject();
```

---

# EXECUTIONSERVICE

## RESPONSABILIDAD

- enviar órdenes
- trailing stop
- tp/sl
- monitoreo posiciones

---

# STACK

| Tecnología | Uso |
|---|---|
| .NET 8 | backend |
| Redis Streams | event bus |
| Kafka | escala alta |
| ClickHouse | timeseries |
| MongoDB | snapshots |
| Python | entrenamiento ML |
| ONNX Runtime | inferencia |
| Docker | deployment |
| Kubernetes | orquestación |

---

# FLUJO COMPLETO

```text
Binance WS
    ↓
MarketDataService
    ↓
Redis Streams
    ↓
FeatureEngine
    ↓
Feature Vectors
    ↓
MLService
    ↓
Predictions
    ↓
RiskEngine
    ↓
ExecutionService
    ↓
Binance REST
```

---

# BASES DE DATOS

| DB | Uso |
|---|---|
| Redis | streams |
| ClickHouse | timeseries |
| MongoDB | snapshots |
| PostgreSQL | metadata |

---

# STREAM NAMES

```text
candles.1m
candles.3m
candles.5m

trades

orderbook

features.1m

predictions

signals
```

---

# VALIDACIÓN

## NUNCA USAR

```python
train_test_split()
```

---

# USAR

```text
Walk Forward Validation
```

---

# MONITOREO

## STACK

- Prometheus
- Grafana

---

# MÉTRICAS IMPORTANTES

| Métrica | Objetivo |
|---|---|
| Latency | <10ms |
| WinRate | >55% |
| Sharpe | >1.5 |
| PF | >1.3 |
| Drawdown | <15% |

---

# PRINCIPIOS IMPORTANTES

## Workers
Contienen:
- loops infinitos
- consumidores
- publishers

---

## DLLs
Contienen:
- lógica reusable
- indicadores
- contratos

---

## APIs
Contienen:
- dashboards
- observabilidad
- control manual

---

# REGLA DE ORO

```text
Workers NO deben contener lógica cuantitativa pesada
```

La lógica cuantitativa debe vivir en:

```text
Shared.Indicators
Shared.Domain
```

---

# MVP RECOMENDADO

## FASE 1

```text
Binance WS
→ Redis Streams
→ FeatureEngine
→ Heurísticas
```

---

## FASE 2

```text
LightGBM
+
Orderflow
+
Regime Detection
```

---

## FASE 3

```text
Transformers
+
CNN Orderbook
+
Ensemble Models
```

# INFRASTRUCTURE
## Docker
Identificar nombre de un contenedor
```bash
docker ps
```
Acceder al contenedor
```bash
docker exec -it <nombre_del_contenedor> /bin/bash
```

## Kafka (Docker)
Levantar servicio
```bash
docker compose -f kafka-docker-compose.yml -p kafka up -d
```
Detener y eliminar
```bash
docker compose -f kafka-docker-compose.yml down
```

Ver logs
```bash
docker compose -f kafka-docker-compose.yml logs -f
```

Construir Imagenes
```bash
docker compose -f kafka-docker-compose.yml build
```
Comandos

```bash
docker exec -it <nombre_del_contenedor> /bin/bash
```
```bash
cd /opt/kafka/bin
```

Crear un topico
```bash
./kafka-topics.sh --create --topic <nombre_del_topic> --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

Agregar Configuraciones a un Topic
```bash
./kafka-configs.sh --bootstrap-server localhost:9092 --alter --topic <nombre_del_topic> --add-config retention.ms=1000
```

Listar topicos
```bash
./kafka-topics.sh --list --bootstrap-server localhost:9092
```

Producir Mensajes
```bash
./kafka-console-producer.sh --topic <nombre_del_topico> --bootstrap-server localhost:9092
>Mensaje 1
>Mensaje 2
# Usa Ctrl+C para salir
```

Consumir mensajes (Desde el inicio)
```bash
./kafka-console-consumer.sh --topic mi-topico --from-beginning --bootstrap-server localhost:9092
```

Ejecutar comandos directamente desde el host
```bash
docker exec -it kafka /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

# HORUS

En la antigua tierra de Egipto, cuando los dioses aún caminaban entre los hombres, nació Horus, hijo de Osiris y Isis.

Su padre fue traicionado y asesinado por su propio hermano, Set, quien tomó el trono y sumió al reino en la incertidumbre. Isis ocultó al joven Horus en los pantanos del delta para protegerlo mientras crecía. Allí aprendió a observar en silencio: el vuelo de los halcones, el movimiento de las estrellas y los cambios invisibles del mundo.

Cuando alcanzó la madurez, Horus desafió a Set para reclamar lo que le correspondía. La lucha duró años. En una de las batallas perdió un ojo, pero no su determinación. Los dioses restauraron ese ojo, y desde entonces el **Ojo de Horus** se convirtió en símbolo de percepción, protección y conocimiento.

Finalmente, Horus venció. No porque fuera el más fuerte, sino porque veía lo que otros no podían ver. Mientras Set actuaba impulsivamente, Horus observaba, analizaba y esperaba el momento exacto para actuar.

Por eso, en las leyendas egipcias, Horus representa algo más que el poder: representa la capacidad de mantener la mirada sobre el horizonte, detectar los cambios antes que los demás y tomar decisiones cuando llega la oportunidad.

Es una historia que encaja sorprendentemente bien con una plataforma de trading: no se trata de adivinar el futuro, sino de observar mejor que los demás. El símbolo de Horus no promete riqueza; promete visión. 👁️🦅

Tiene un simbolismo muy potente para una aplicación de señales.

Lo interesante de **Horus** es que la historia puede reinterpretarse para el trading de una forma natural:

> Mientras otros reaccionan al mercado, Horus observa.
>
> Mientras otros persiguen movimientos, Horus detecta patrones.
>
> Mientras otros ven ruido, Horus encuentra señales.

Eso encaja perfectamente con una plataforma que analiza datos y genera señales de futuros.

Incluso podrías construir toda la identidad de la marca alrededor del concepto de visión:

* **Horus AI** — El ojo que vigila el mercado.
* **Ojo de Horus** — Tu indicador principal o sistema de puntuación.
* **Visión Horus** — Panel de análisis.
* **Horus Sentinel** — Sistema de monitoreo 24/7.
* **Horus Insight** — Explicación de cada señal generada por la IA.

Un posible eslogan:

* **"Ve lo que otros no ven."**
* **"La visión detrás de cada señal."**
* **"Observa. Analiza. Anticípate."**
* **"El ojo sobre el mercado."**
* **"Donde los datos se convierten en visión."**

Y una versión breve de la historia para la página principal podría ser:

> En la mitología egipcia, Horus era el dios de la visión y la vigilancia. Su ojo simbolizaba la capacidad de percibir lo que permanecía oculto para los demás. Inspirados por esa idea, creamos Horus AI: una plataforma diseñada para analizar miles de datos del mercado y detectar oportunidades antes de que se vuelvan evidentes.

Para una app de criptomonedas, "Horus AI" tiene además una ventaja: suena serio, tecnológico y memorable, sin caer en nombres genéricos como "Crypto Signals Pro" o "Trade Bot AI". Se siente más como una marca que como una herramienta.
