# 📘 Manual de Usuario: Sistema de Trading Quant

Bienvenido al sistema de trading institucional para Binance Futures. Este manual está diseñado para ayudarte a entender cómo funciona el sistema, qué hace y cómo interpretarlo, sin necesidad de ser un experto en programación.

---

## 🌟 ¿Qué es este sistema?
Es un motor de trading automático que analiza el "micro-estatal" del mercado (la lucha real entre compradores y vendedores) para tomar decisiones basadas en **probabilidades**, no en indicadores simples. 

En lugar de decir "compra porque el RSI está bajo", el sistema dice: *"Hay una probabilidad del 85% de subir porque el precio barrió liquidez, rompió la estructura y hay absorción de ventas"*.

---

## 🛠️ ¿Cómo funciona el sistema? (El Flujo)

El sistema sigue un camino lineal de 4 pasos:

1. **Ingesta (Los Oídos)**: Escucha en tiempo real los datos de Binance a través de Kafka (Velas, Trades, Libro de Órdenes y Liquidaciones).
2. **Motores de Análisis (El Cerebro)**: Cuatro motores analizan el precio simultáneamente:
   - **Estructura**: Identifica si la tendencia es alcista o bajista mediante la rotura de máximos y mínimos (BOS).
   - **Liquidez**: Busca "trampas" donde el precio cae para activar stops y luego sube rápidamente (Sweeps).
   - **Flujo (Order Flow)**: Analiza el volumen agresivo. Si hay muchas compras pero el precio no sube, detecta que un "pez gordo" está absorbiendo las órdenes.
   - **Régimen**: Determina si el mercado está en tendencia o si está "lateral" (chop), para evitar operar en mercados sin dirección.
3. **Scoring (El Juez)**: Recolecta las señales de los 4 motores y les asigna un peso. El resultado es un número entre **0.0 y 1.0**.
4. **Ejecución y Riesgo (El Gestor)**: Si la probabilidad es alta (ej. > 0.6), el Gestor de Riesgo calcula cuánto invertir según tu balance para que nunca pierdas más del 1% por operación.

---

## 📊 Datos que necesita y Resultados

### Datos de Entrada (Input)
El sistema consume datos en tiempo real:
- **Candles (Velas)**: Precio de apertura, cierre, máximo y mínimo.
- **Trades**: Cada transacción individual que ocurre en el exchange.
- **Orderbook**: La lista de órdenes de compra y venta pendientes.
- **Liquidations**: Avisos cuando otros traders son liquidados (indicador fuerte de reversión).

### Resultados (Output)
Cuando ejecutas el sistema, verás en la consola:
- **Ejecuciones**: `Executed LONG 0.1234 @ 65000.00` (Indica que se abrió una posición).
- **Estado de Cartera**: 
  - `Equity`: Tu capital total actual (Balance + Ganancias/Pérdidas no realizadas).
  - `Balance`: Tu dinero en efectivo.
  - `Exposure`: Cuánto dinero tienes actualmente arriesgado en el mercado.

---

## ⚙️ Configuración Avanzada

Para cambiar el comportamiento del sistema, ya no usamos un solo archivo, sino que tenemos archivos específicos en la carpeta `config/` según la funcionalidad:

- **Símbolo y Timeframe**: `config/trading_settings.py` (Define qué activo y temporalidad operar).
- **Riesgo**: `config/risk_settings.py` (Define el riesgo por operación, drawdown máximo y apalancamiento).
- **Orderbook**: `config/orderbook_settings.py` (Ajusta los umbrales de desbalance para señales alcistas/bajistas).
- **Estructura**: `config/structure_settings.py` (Define la ventana de velas para identificar máximos y mínimos).
- **Scoring**: `config/scoring_settings.py` (Ajusta los pesos de cada motor en la decisión final).
- **Ejecución**: `config/execution_settings.py` (Configura latencia, slippage y comisiones).
- **Infraestructura**: `config/kafka_settings.py` y `config/state_settings.py` (Ajustes de conexión y límites de memoria).

---

## ⚠️ Advertencia Final
Este sistema opera en **modo simulación**. No envía órdenes reales a Binance, sino que calcula la ejecución basándose en la latencia y el deslizamiento (slippage) real del mercado para darte resultados realistas.
