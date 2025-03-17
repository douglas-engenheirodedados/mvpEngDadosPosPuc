import json
import boto3
import os
from botocore.exceptions import ClientError


def save_json_local(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def upload_to_s3(local_path: str, bucket: str, s3_key: str):
    s3 = boto3.client('s3')
    s3.upload_file(local_path, bucket, s3_key)
    print(f"Uploaded {local_path} to s3://{bucket}/{s3_key}")

def check_s3_file_exists(bucket: str, key: str) -> bool:
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise
