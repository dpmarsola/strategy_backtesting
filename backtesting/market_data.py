import pandas as pd
import requests
from sqlalchemy import create_engine
import sys
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
ticker = sys.argv[1]
timeframe = sys.argv[2]
initial_period = sys.argv[3]
end_period = sys.argv[4]

# Define the URL you want to send the GET request to
url = f'http://localhost:8080/trendsniper/?ticker={ticker}&timeframe={timeframe}&initial_period={initial_period}&end_period={end_period}&options=adr&options=guppy&options=atr&options=macd&options=show-raw-data&options=json'

# Send the GET request
response = requests.get(url)

df = pd.read_json(response.text)

df['datetime'] = pd.to_datetime(df['time'], unit='s')

df['asset'] = ticker

engine = create_engine('sqlite:///robotrader.db')

df.to_sql(name="market_data", con=engine, if_exists='replace', index=False)

read_df = pd.read_sql_table('market_data', con=engine)

print("Data fetched successfully!")
     
