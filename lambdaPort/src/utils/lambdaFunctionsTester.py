#Testing utils/list bucket objects'

from .s3crud import list_s3_objects_client
from .globals import BUCKET_NAME
def beginTest():
    print("Testing utils/list bucket objects'")
    result = list_s3_objects_client(BUCKET_NAME)
    print(result)
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }