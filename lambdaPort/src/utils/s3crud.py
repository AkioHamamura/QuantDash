import boto3

def test(data):
    #Just try to put the data as a csv to the s3 bucket
    s3_client = boto3.client('s3')
    # Define bucket and key
    bucket_name = 'quant-dash-cache'
    object_key = 'test.csv'

    # Content to upload
    file_content = data.to_csv()

    try:
        # Upload the object
        response = s3_client.put_object(
            Body=file_content,
            Bucket=bucket_name,
            Key=object_key
        )
        print(f"Object '{object_key}' uploaded successfully to bucket '{bucket_name}'.")
        print(f"Response: {response}")

    except Exception as e:
        print(f"Error uploading object: {e}")


def list_s3_objects_client(bucket_name, prefix=''):
    """
    Lists objects in an S3 bucket using the S3 client.

    Args:
        bucket_name (str): The name of the S3 bucket.
        prefix (str): Optional prefix to filter objects (e.g., a folder path).
    """
    s3_client = boto3.client('s3')
    paginator = s3_client.get_paginator('list_objects_v2')

    # Iterate through pages to handle large number of objects
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                print(obj['Key'])
        else:
            print(f"No objects found in '{bucket_name}' with prefix '{prefix}'.")

# Example usage:
# list_s3_objects_client('your-bucket-name')
# list_s3_objects_client('your-bucket-name', 'your-folder-name/')