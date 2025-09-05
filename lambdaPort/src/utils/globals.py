import os
import boto3
# Get the path for the s3 bucket
#BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_DIR = '/'
DATA_PATH = os.path.join(BACKEND_DIR, "cache")