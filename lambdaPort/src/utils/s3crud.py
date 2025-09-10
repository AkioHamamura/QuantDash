import boto3

def put_s3_objects_client(bucket_name=None, data=None, object_key=None):
    #Just try to put the data as a csv to the s3 bucket
    s3_client = boto3.client('s3')

    # Content to upload
    file_content = data.to_csv()

    try:
        # Upload the object
        response = s3_client.put_object(
            Body=file_content,
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
    try:
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if 'Contents' in page:
                for obj in page['Contents']:
                    return{
                        'statusCode': 200,
                        'body': obj['Key']
                    }
            else:
                return {
                    'statusCode': 201,
                    'body': f"Listable, but no objects found in '{bucket_name}' with prefix '{prefix}'."
                }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error listing objects: {e}"
        }

def read_s3_object_client(bucket_name, object_key):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        print(response)
        return {
            'statusCode': 200,
            'body': response
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error reading object: {e}"
        }

# Example usage:
# list_s3_objects_client('your-bucket-name')
# list_s3_objects_client('your-bucket-name', 'your-folder-name/')