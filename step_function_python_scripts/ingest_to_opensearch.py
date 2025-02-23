import json
import boto3

opensearch = boto3.client('es')

def handler(event, context):
    # get transformed data
    transformed_data = event['transformed_data']

    opensearch_endpoint = "opensearch-endpoint"

    # upload each record to OpenSearch index
    for record in transformed_data:
        opensearch.index(
            index='sensor-data',
            body=record
        )

    return {
        'statusCode': 200,
        'body': json.dumps('Data ingested successfully!')
    }
