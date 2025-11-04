"""
Create S3 buckets - run once
"""
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

buckets = [
    'crypto-analytics-raw',
    'crypto-analytics-transformed',
    'crypto-analytics-athena'
]

print("Creating S3 buckets...\n")

print("Checking credentials...")
try:
    sts = boto3.client(
        'sts',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    identity = sts.get_caller_identity()
except Exception as e:
    print(f"Credentials error: {e}")
    print("\nCheck your .env file:")
    exit(1)

for bucket in buckets:
    try:
        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={'LocationConstraint': 'eu-north-1'}
        )
        print(f"Created: {bucket}")

    except ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == 'BucketAlreadyOwnedByYou':
            print(f"Already exists (owned by you): {bucket}")

        elif error_code == 'BucketAlreadyExists':
            print(f"Name taken by someone else: {bucket}")
            print(f"Try: {bucket}-v2 or {bucket}-2025")

        else:
            print(f"Error creating {bucket}: {e}")

print("\nListing all your buckets:")
try:
    response = s3.list_buckets()
    for bucket in response['Buckets']:
        print(f"   - {bucket['Name']}")
except Exception as e:
    print(f"Error listing buckets: {e}")

print("\nDone!")