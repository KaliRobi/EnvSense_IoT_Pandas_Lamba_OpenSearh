import pandas as pd

def handler(event, context):
    # load the raw data into a DataFrame
    df = pd.DataFrame(event['data'])

    # remove sensor readings that are clearly unrealistic
    df = df[(df['temperature'] >= -20) & (df['temperature'] <= 50)]
    df = df[(df['humidity'] >= 0) & (df['humidity'] <= 100)]

    # deal with leftover missing values 
    df.fillna(method='ffill', inplace=True)


    return {
        'statusCode': 200,
        'cleaned_data': df.to_dict('records')
    }