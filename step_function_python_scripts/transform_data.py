import pandas as pd

def handler(event, context):
    #  data into a pandas DataFrame
    df = pd.DataFrame(event['cleaned_data'])

    # timestamp column to datetime and set it as the index for time-based operations
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    
    # to smooth out gaps in data
    df.interpolate(method='linear', inplace=True)

    # remove extreme outliers 
    df = df[(df['temperature'].between(-50, 60)) & (df['humidity'].between(0, 100))]

    # data by day to calculate mean, min, max, and standard deviation
    daily_stats = df.resample('D').agg(['mean', 'min', 'max', 'std'])

    # Clean up column names 
    daily_stats.columns = [f"{col[0]}_{col[1]}" for col in daily_stats.columns]

    # days based on temperature ranges
    bins = [-float('inf'), 0, 20, 30, float('inf')]
    labels = ["Cold", "Cool", "Warm", "Hot"]
    daily_stats['temperature_category'] = pd.cut(daily_stats['temperature_mean'], bins=bins, labels=labels)

    
    return {
        'statusCode': 200,
        'transformed_data': daily_stats.reset_index().to_dict('records')
    }
