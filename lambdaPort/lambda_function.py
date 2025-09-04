import sys
def handler(event, context):
    
    print(event)
    print("Test 2")
    return 'Hello from AWS Lambda using Python' + sys.version + '!'