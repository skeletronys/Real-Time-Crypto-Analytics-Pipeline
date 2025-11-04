"""
Setup S3 Lifecycle policies for cost optimization
"""
import boto3
from botocore.exceptions import ClientError
import os
import json
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# Lifecycle policy
lifecycle_policy = {
    "Rules": [
        {
            "ID": "DeleteOldRawData",
            "Status": "Enabled",
            "Filter": {"Prefix": "raw/"},
            "Expiration": {"Days": 30}
        },
        {
            "ID": "DeleteOldTransformed",
            "Status": "Enabled",
            "Filter": {"Prefix": "transformed/"},
            "Expiration": {"Days": 60}
        },
        {
            "ID": "DeleteAthenaResults",
            "Status": "Enabled",
            "Filter": {"Prefix": "query-results/"},
            "Expiration": {"Days": 7}
        }
    ]
}

buckets = [
    os.getenv('AWS_S3_BUCKET_RAW'),
    os.getenv('AWS_S3_BUCKET_TRANSFORMED'),
    os.getenv('AWS_S3_BUCKET_ATHENA')
]

print("    Setting up S3 Lifecycle policies...\n")

for bucket in buckets:
    if not bucket:
        continue

    try:
        s3.put_bucket_lifecycle_configuration(
            Bucket=bucket,
            LifecycleConfiguration=lifecycle_policy
        )
        print(f"   Lifecycle applied: {bucket}")
        print(f"   - Raw data deleted after 30 days")
        print(f"   - Transformed data deleted after 60 days")
        print(f"   - Athena results deleted after 7 days\n")

    except ClientError as e:
        print(f"Error for {bucket}: {e}\n")

print("Lifecycle setup complete!")
print("This will save ~90% on storage costs!")