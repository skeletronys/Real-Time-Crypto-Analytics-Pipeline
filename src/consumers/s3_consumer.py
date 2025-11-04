"""
Kafka to S3 Consumer
Reads crypto price data from Kafka and writes to S3 in Parquet format
"""
import json
import os
import tempfile
from datetime import datetime, timezone
from typing import List, Dict
import pandas as pd
import boto3
from botocore.exceptions import ClientError
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv

load_dotenv()

# Configuration
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_PRICES", "crypto-prices")
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "s3-consumer-group")

S3_BUCKET = os.getenv("AWS_S3_BUCKET_RAW", "crypto-analytics-raw")
AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")

BUFFER_SIZE = 10  # Write to S3 every 50 records

print(f"Starting S3 Consumer")
print(f"Kafka topic: {KAFKA_TOPIC}")
print(f"S3 bucket: {S3_BUCKET}")
print(f"Buffer size: {BUFFER_SIZE} records")
print(f"Region: {AWS_REGION}\n")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=AWS_REGION
)

# Initialize Kafka Consumer
consumer_conf = {
    'bootstrap.servers': KAFKA_SERVERS,
    'group.id': KAFKA_GROUP,
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True
}

consumer = Consumer(consumer_conf)
consumer.subscribe([KAFKA_TOPIC])

print("Kafka consumer connected")
print("S3 client initialized\n")

# Buffer for batching records
buffer: List[Dict] = []
total_written = 0


def write_to_s3(records: List[Dict]) -> bool:
    """Write batch of records to S3 as Parquet"""
    if not records:
        return False

    try:
        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Create partition path: # 2025-10-30
        now = datetime.now(timezone.utc)
        date_str = now.strftime('%Y-%m-%d')
        partition_path = f"raw/crypto_prices/{date_str}"
        # Filename with timestamp
        time_str = now.strftime('%H%M%S')
        filename = f"data_{time_str}.parquet"
        s3_key = f"{partition_path}/{filename}"

        # Write to local temp file first
        temp_file = os.path.join(tempfile.gettempdir(), filename)
        df.to_parquet(
            temp_file,
            engine='pyarrow',
            compression='snappy',
            index=False
        )

        # Upload to S3
        s3_client.upload_file(
            temp_file,
            S3_BUCKET,
            s3_key
        )

        # Clean up temp file
        os.remove(temp_file)

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Wrote {len(records)} records to s3://{S3_BUCKET}/{s3_key}")

        return True

    except ClientError as e:
        print(f"S3 error: {e}")
        return False

    except Exception as e:
        print(f"Write error: {e}")
        return False


# Main consumer loop
print("🔄 Starting consumption...\n")
print("💡 Press Ctrl+C to stop gracefully\n")

try:
    while True:
        # Poll for messages (timeout 1 second)
        msg = consumer.poll(timeout=1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition - not an error
                continue
            else:
                print(f"Kafka error: {msg.error()}")
                continue

        # Parse message
        try:
            record = json.loads(msg.value().decode('utf-8'))
            buffer.append(record)

            # Write to S3 when buffer is full
            if len(buffer) >= BUFFER_SIZE:
                if write_to_s3(buffer):
                    total_written += len(buffer)
                    print(f"Total records written: {total_written}\n")
                    buffer = []  # Clear buffer

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            continue

except KeyboardInterrupt:
    print("\nStopping consumer...")

    # Write remaining buffer
    if buffer:
        print(f"Writing remaining {len(buffer)} records...")
        if write_to_s3(buffer):
            total_written += len(buffer)

    print(f"\nFinal stats:")
    print(f"   Total records written: {total_written}")
    print(f"   S3 bucket: s3://{S3_BUCKET}/raw/crypto_prices/")

    consumer.close()
    print("Consumer stopped gracefully")

except Exception as e:
    print(f"\nUnexpected error: {e}")
    consumer.close()