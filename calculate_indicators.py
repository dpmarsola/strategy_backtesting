import trend_sniper.lib.context
from trend_sniper.lib.indicators import atr
from trend_sniper.lib.indicators import cbl
from trend_sniper.lib.indicators import adr
from trend_sniper.lib.indicators import macd
from trend_sniper.lib.indicators import guppy
import requests
import  pandas as pd
import warnings
import sqlite3
import backtesting.constants as constants
import backtesting.data.initialize_db
from backtesting.data import connection



def select_all(asset):

    rows_list = []
    row_dict = {
        "datetime" : '',
        "time" : '',
        "open" : 0.0,
        "high" : 0.0,
        "low" : 0.0,
        "close" : 0.0,
        "tick_volume" : 0,
        "spread" : 0,
        "real_volume" : 0,
        "asset" : ''
    }

    try:
        with sqlite3.connect(f'{constants.DATABASE_NAME}') as conn:
            cursor = conn.cursor()
            result = cursor.execute(
                f'SELECT * FROM {constants.MARKET_DATA_TABLE} WHERE asset = :asset',
                {"asset": asset})
            conn.commit()
            for row in result.fetchall():
                row_dict['datetime'] = row[0]
                row_dict['time'] = row[1]
                row_dict['open'] = row[2]
                row_dict['high'] = row[3]
                row_dict['low'] = row[4]
                row_dict['close'] = row[5]
                row_dict['tick_volume'] = row[6]
                row_dict['spread'] = row[7]
                row_dict['real_volume'] = row[8]
                row_dict['asset'] = row[9]
                rows_list.append(row_dict.copy())
        return rows_list
    except Exception as e:
        if "no such table" in e.__str__():
            print(
                f'Table {constants.MARKET_DATA_TABLE} not found in database {constants.DATABASE_NAME}. Run script to fetch market data.')


warnings.filterwarnings("ignore", category=FutureWarning)
ticker = 'ITSA4'
timeframe = 'D1'
initial_period = '2025-08-01'
end_period = '2025-08-30'

print("Fetching Historical Data...")


df = pd.DataFrame(select_all(ticker))

# url = f'http://localhost:8080/trendsniper/?ticker={ticker}&timeframe={timeframe}&initial_period={initial_period}&end_period={end_period}&options=json'
# response = requests.get(url)
# df = pd.read_json(response.text)
# # df['datetime'] = pd.to_datetime(df['time'], unit='s')
# df['asset'] = ticker
df['datetime'] = pd.to_datetime(df['time'],unit='s')


ctx_load = trend_sniper.lib.context.ContextLoader()
ctx_load.load_context()
ctx_helper = trend_sniper.lib.context.ContextHelper()

atr_periods = ctx_helper.get_context_specific_data(ctx_load.context, 'atr_smp', 'indicator', 'data.atr_period')
atr_multiplier = ctx_helper.get_context_specific_data(ctx_load.context, 'atr_smp', 'indicator', 'data.atr_multiplier')
adr_periods = ctx_helper.get_context_specific_data(ctx_load.context, 'adr', 'indicator', 'data.adr_period')
adr_multiplier = ctx_helper.get_context_specific_data(ctx_load.context, 'adr', 'indicator', 'data.adr_multiplier')
guppy_periods = tuple(ctx_helper.get_context_specific_data(ctx_load.context, 'guppy', 'indicator', 'data.guppy_periods'))

df = atr.ATR().calculate(df, atr_periods, atr_multiplier)
df = adr.ADR().calculate(df,adr_periods, adr_multiplier)
df = cbl.CBL().calculate(df)
df = guppy.Guppy().calculate(df, guppy_periods)
df = macd.MACD().calculate(df)
df = df.set_index('datetime')

conn = connection.get_connection()
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS historical_data;")
df.to_sql(name="historical_data", con=conn, if_exists='replace', index_label='datetime')
