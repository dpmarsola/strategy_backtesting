import pandas as pd
import requests
import sys
import warnings
from .data import connection

warnings.filterwarnings("ignore", category=FutureWarning)
ticker = sys.argv[1]
timeframe = sys.argv[2]
initial_period = sys.argv[3]
end_period = sys.argv[4]

print("Fetching Market Data...")

# url = f'http://localhost:8080/trendsniper/?ticker={ticker}&timeframe={timeframe}&initial_period={initial_period}&end_period={end_period}&options=adr&options=guppy&options=atr&options=macd&options=cbl&options=show-raw-data&options=json'
# response = requests.get(url)
# df = pd.read_json(response.text)
# df['datetime'] = pd.to_datetime(df['time'], unit='s')
# df['asset'] = ticker
# engine = create_engine('sqlite:///robotrader.db')
conn = connection.get_connection()
# df.to_sql(name="market_data", con=conn, if_exists='append', index_label='datetime')


print("Fetching Historical Data...")

url = f'http://localhost:8080/trendsniper/?ticker={ticker}&timeframe={timeframe}&initial_period={initial_period}&end_period={end_period}&options=json'
response = requests.get(url)
df = pd.read_json(response.text)
# df['datetime'] = pd.to_datetime(df['time'], unit='s')
df['asset'] = ticker
df.to_sql(name="historical_data", con=conn, if_exists='append', index_label='datetime')

print("Data fetched successfully!")

