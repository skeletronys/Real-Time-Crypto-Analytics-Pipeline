"""
CoinGecko Kafka Producer
Optimized for Free Tier: 5 minute intervals
"""
import json
import time
import os
from datetime import datetime
import requests
from kafka import KafkaProducer
from kafka.errors import KafkaError
from dotenv import load_dotenv

load_dotenv()

COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_PRICES", "crypto-prices")
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL_SECONDS", "300"))

SYMBOLS = [
    "bitcoin",
    "ethereum",
    "binancecoin",
]

print(f"Starting CoinGecko Producer")
print(f"Tracking: {', '.join(SYMBOLS)}")
print(f"Fetch interval: {FETCH_INTERVAL} seconds ({FETCH_INTERVAL // 60} minutes)")
print(f"Kafka topic: {KAFKA_TOPIC}")
print(f"Kafka servers: {KAFKA_SERVERS}\n")

# Initialize Kafka Producer
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8'),
        acks='all',
        retries=3,
        max_in_flight_requests_per_connection=1
    )
    print("✅ Kafka producer connected\n")
except KafkaError as e:
    print(f"Kafka connection failed: {e}")
    print("Make sure Kafka is running: docker-compose up -d")
    exit(1)


def fetch_prices():
    """Fetch current crypto prices from CoinGecko"""
    try:
        params = {
            'ids': ','.join(SYMBOLS),
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }

        response = requests.get(COINGECKO_API, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")
        return None


def send_to_kafka(data):
    """Send price data to Kafka"""
    if not data:
        return 0

    count = 0
    timestamp = datetime.utcnow().isoformat()

    for symbol, values in data.items():
        record = {
            'symbol': symbol,
            'price_usd': values.get('usd'),
            'market_cap_usd': values.get('usd_market_cap'),
            'volume_24h_usd': values.get('usd_24h_vol'),
            'price_change_24h_pct': values.get('usd_24h_change'),
            'last_updated_at': values.get('last_updated_at'),
            'fetched_at': timestamp,
            'source': 'coingecko'
        }

        try:
            future = producer.send(
                KAFKA_TOPIC,
                key=symbol,
                value=record
            )
            future.get(timeout=10)
            count += 1

        except KafkaError as e:
            print(f"Kafka send error for {symbol}: {e}")

    return count


# Main loop
print("🔄 Starting data collection...")
print(f"💡 Press Ctrl+C to stop\n")

iteration = 0
total_api_calls = 0

try:
    while True:
        iteration += 1
        total_api_calls += 1
        start_time = time.time()

        # Fetch data
        data = fetch_prices()

        if data:
            # Send to Kafka
            count = send_to_kafka(data)

            # Show status
            elapsed = time.time() - start_time
            next_fetch = datetime.now().timestamp() + FETCH_INTERVAL
            next_time = datetime.fromtimestamp(next_fetch).strftime('%H:%M:%S')

            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Sent {count} records | "
                  f"Total API calls: {total_api_calls} | "
                  f"Next: {next_time}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Failed to fetch | "
                  f"Total API calls: {total_api_calls}")

        # Wait for next interval
        sleep_time = max(0, FETCH_INTERVAL - (time.time() - start_time))
        if sleep_time > 0:
            time.sleep(sleep_time)

except KeyboardInterrupt:
    print(f"\nStopping producer...")
    print(f"Total API calls made: {total_api_calls}")
    print(f"Estimated monthly usage: {total_api_calls * 30 * 24 * 60 // (FETCH_INTERVAL // 60):,}")
    producer.flush()
    producer.close()
    print("Producer stopped gracefully")

except Exception as e:
    print(f"\nUnexpected error: {e}")
    producer.close()