import pandas as pd
import requests
import sys
import warnings
from .data import connection
import ast

warnings.filterwarnings("ignore", category=FutureWarning)
ticker = sys.argv[1]
timeframe = sys.argv[2]
initial_period = sys.argv[3]
end_period = sys.argv[4]

# print("Fetching Market Data...")
# url = f'http://localhost:8080/trendsniper/?ticker={ticker}&timeframe={timeframe}&initial_period={initial_period}&end_period={end_period}&options=adr&options=guppy&options=atr&options=macd&options=cbl&options=show-raw-data&options=json'
# response = requests.get(url)
# df = pd.read_json(response.text)
# df['datetime'] = pd.to_datetime(df['time'], unit='s')
# df['asset'] = ticker
# engine = create_engine('sqlite:///robotrader.db')
# df.to_sql(name="market_data", con=conn, if_exists='append', index_label='datetime')


print("Fetching Historical Data...")
conn = connection.get_connection()
data = ''

try:
    url = f'http://localhost:8000/trendsniper/?ticker={ticker}&timeframe={timeframe}&initial_period={initial_period}&end_period={end_period}&options=adr&options=guppy&options=atr&options=macd&options=json'
    response = requests.get(url)
    response.raise_for_status()
    # 1. Safely parse the Python dictionary string
    data = ast.literal_eval(response.text)

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")  # e.g., 404 Client Error: Not Found
except requests.exceptions.RequestException as err:
    print(f"An error occurred: {err}")  # Handle

df = pd.DataFrame(data)
# 3. Convert millisecond timestamp index to datetime
df.index = pd.to_datetime(df.index.astype('int64'), unit='ms')
df.index.name = 'datetime'
# 4. Add asset and save to database
df['asset'] = ticker
df.to_sql(name="historical_data", con=conn, if_exists='replace', index_label='datetime')
print(f"{df.shape[0]} items fetched successfully!")

