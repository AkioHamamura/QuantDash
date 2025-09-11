import boto3
from .globals import BUCKET_NAME

def put_s3_objects_client(bucket_name=None, data=None, object_key=None):
    #Just try to put the data as a csv to the s3 bucket
    s3_client = boto3.client('s3')

    # Content to upload


    try:
        # Upload the object
        response = s3_client.put_object(
            Body=data,
            Bucket=bucket_name,
            Key=object_key
        )
        return {
            'statusCode': 200,
            'body': f"Object '{object_key}' uploaded successfully to bucket '{bucket_name}'.",
            'response': response
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error uploading object: {e}",
            'error': 'Error uploading object to S3. Check your bucket name and object key.'
        }


def list_s3_objects_client(bucket_name, prefix="cache/"):
    """
    Lists objects in an S3 bucket using the S3 client.

    Args:
        bucket_name (str): The name of the S3 bucket.
        prefix (str): Optional prefix to filter objects (e.g., a folder path).
    """
    try:
        s3_client = boto3.client('s3')
        paginator = s3_client.get_paginator('list_objects_v2')
        keys = []
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'] not in ["cache/available_tickers_1d.txt","cache/event.json"]:
                        keys.append(obj['Key'])
        return keys
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error listing objects: {e}"
        }

def read_s3_object_client(bucket_name=BUCKET_NAME, object_key="NVDA"):
    s3_client = boto3.client('s3')
    try:
        # Get the object instead of downloading it
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        # Read the content from the response
        file_content = response['Body'].read()
        return {
            'statusCode': 200,
            'body': file_content
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error reading object: {e}"
        }

# Example usage:
# list_s3_objects_client('your-bucket-name')
# list_s3_objects_client('your-bucket-name', 'your-folder-name/')