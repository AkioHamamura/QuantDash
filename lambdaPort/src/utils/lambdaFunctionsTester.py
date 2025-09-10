#Testing utils/list bucket objects'
import pandas as pd
import os
from .globals import BUCKET_NAME
from .s3crud import *
from ..data.data_fetcher import *

def beginTest():

    if not listTest():
        return {
            'statusCode': 500,
            'body': 'FAILED Error in utils/list bucket objects'
        }

    else:
        print("Testing utils/list bucket objects: 'OK \n'")

    if uploadTest()['statusCode'] not in [200, 201]:
        return {
            'statusCode': 500,
            'body': 'FAILED Error in utils/upload bucket objects'
        }
    else:
        print("Testing utils/upload bucket objects: 'OK \n'")

    if readTest()['statusCode'] not in [200, 201]:
        return {
            'statusCode': 500,
            'body': 'FAILED Error in utils/read bucket objects'
        }
    else:
        print("Testing utils/read bucket objects: 'OK \n'")
    testDataFetcher()
    return {
        'statusCode': 200,
        'body': 'Hello from Serverless QuantDash, passed all tests! \n'
    }

def listTest():
    print("Testing utils/list bucket objects: '")
    result = list_s3_objects_client(BUCKET_NAME)
    if result['statusCode'] in [200, 201]:
        return True
    else:
        return False

def uploadTest():
    print("Testing utils/upload bucket objects: '")
    #Creating some data and key
    data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    object_key = 'test.csv'
    return put_s3_objects_client(bucket_name=BUCKET_NAME, data=data, object_key=object_key)

def readTest():
    print("Testing utils/read bucket objects: '")
    object_key = 'test.csv'
    return read_s3_object_client(bucket_name=BUCKET_NAME, object_key=object_key)

def testDataFetcher():
    write_available_tickers(cache_dir=DATA_PATH)