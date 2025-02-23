import json
import boto3

s3 = boto3.client('s3')

def handler(event, context):
    # Extract bucket and file key from the event
    bucket = event['bucket']
    key = event['key']
    
    response = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(response['Body'].read().decode('utf-8'))

    return {
        'statusCode': 200,
        'data': data
    }
