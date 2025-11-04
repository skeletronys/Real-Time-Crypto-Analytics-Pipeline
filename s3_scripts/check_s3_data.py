# check_s3_data.py
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bucket = os.getenv('AWS_S3_BUCKET_RAW')
prefix = 'raw/crypto_prices/'

print(f"Files in s3://{bucket}/{prefix}\n")

response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

if 'Contents' in response:
    for obj in response['Contents']:
        size_mb = obj['Size'] / 1024 / 1024
        print(f"   {obj['Key']}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Modified: {obj['LastModified']}\n")
else:
    print("No files found")