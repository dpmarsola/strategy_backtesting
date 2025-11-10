import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
from datetime import datetime
import warnings
from . import globals
register_matplotlib_converters()
warnings.filterwarnings("ignore")

global_vars = globals.Globals()

class DataPlot():

    plt = plt
    fig = None
    ax = None

    def __save_fig(self):
        plt.figure(figsize=(60, 48), dpi=80, layout='tight')
        # filename = f"./{datetime.now().strftime('%d%m%Y_%H%M%S')}.jpg"
        filename = f"./output/{global_vars.get('simulation_id')}.jpg"
        self.fig.savefig(filename,transparent=None, dpi='figure', format=None,
        metadata=None, bbox_inches=None, pad_inches=0.1,facecolor='auto', edgecolor='auto', backend=None)
        plt.close('all')
        print(f"Figure saved as {filename}")

    def __output_stdout(self):
        plt.show()
    
    def __plot_separate_charts(self, rates_dataframe):
        
        
        self.ax.bar(self.xaxis_open_close_cdl, self.yaxis_open_close_cdl, self.width_open_close_cdl, bottom=self.bottom_open_close_cdl, color=self.bar_color)
        self.ax.bar(self.xaxis_high_low_cdl, self.yaxis_high_low_cdl, self.width_high_low_cdl, bottom=self.bottom_high_low_cdl, color=self.bar_color)
        self.ax.plot(self.xaxis_visual_indicator_trades_dates, self.yaxis_visual_indicator_position_long_trades, marker='^', markersize=25, markerfacecolor="#031531", markeredgecolor="#49944F", markeredgewidth=3)
        self.ax.plot(self.xaxis_visual_indicator_trades_dates, self.yaxis_visual_indicator_position_short_trades, marker='v', markersize=25, markerfacecolor="#EDEEDC", markeredgecolor="#B10808", markeredgewidth=3)
        self.ax.tick_params(axis='x')
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5, color=self.grid_color)
        self.ax.set_facecolor(self.background_color)
        self.ax.set_ylabel('PRICE')
        
    def __set_common_styles(self):
        
        chart_style = {
                    "candles_up_color": "#00ab74",
                    "candles_down_color": "#eb4d4d",
                    "grid_color": "#d5d5d5",
                    "background_color": "#ffffff",
                    "style_sheet": "fivethirtyeight",
                    "font_family": "Arial",
                    "font_weight": "normal",
                    "font_size": 10,
                    "font_color": "#000000"
                }
        
        plt.style.use(chart_style["style_sheet"])
        plt.style.use({ 'font.size' : str(chart_style["font_size"])})
        # plt.style.use({ 'font.family' : chart_style["font_family"]})
        plt.style.use({ 'font.weight' : chart_style["font_weight"]})
        plt.rcParams['text.color'] = chart_style["font_color"]
        plt.rcParams['axes.labelcolor'] = chart_style["font_color"]
        plt.rcParams['xtick.color'] = chart_style["font_color"]     
        plt.rcParams['ytick.color'] = chart_style["font_color"]

        self.candles_up_color = chart_style["candles_up_color"]
        self.candles_down_color = chart_style["candles_down_color"]
        self.background_color = chart_style["background_color"]
        self.grid_color = chart_style["grid_color"]
        
        macd_style = {
                    "up_color": "#98eec4",
                    "down_color": "#ee98a5",
                    "width": 0.75
                }
        
        self.macd_up_color = macd_style["up_color"]
        self.macd_down_color = macd_style["down_color"]
        self.macd_width = macd_style["width"]

    def __set_styles_based_on_dataframe_data(self, rates_dataframe): 
        
        # Convert the date column to a string format
        rates_dataframe['date_str'] = pd.to_datetime(rates_dataframe.index, utc=True)
        rates_dataframe['date_str'] = rates_dataframe['date_str'].dt.strftime('%Y-%m-%d %H:%M:%S').astype(str)

        # setting the High and Low candles
        self.xaxis_high_low_cdl = rates_dataframe['date_str']
        self.yaxis_high_low_cdl = rates_dataframe['high'] - rates_dataframe['low']
        self.width_high_low_cdl = 0.05  # the width of the bars: can also be len(x) sequence
        self.bottom_high_low_cdl = rates_dataframe['low']
        
        # setting the Open and Close candles
        self.xaxis_open_close_cdl = rates_dataframe['date_str']
        self.yaxis_open_close_cdl = rates_dataframe['close'] - rates_dataframe['open']
        self.width_open_close_cdl = 0.3  # the width of the bars: can also be len(x) sequence
        self.bottom_open_close_cdl = rates_dataframe['open']
    
        self.bar_color = np.where(rates_dataframe['close'] > rates_dataframe['open'], self.candles_up_color, self.candles_down_color)
        
        # setting the trades data 
        self.xaxis_visual_indicator_trades_dates = rates_dataframe['date_str']
        rates_dataframe['visual_indicator_position_short_trades'] = None
        rates_dataframe['visual_indicator_position_long_trades'] = None
            
        for idx, row in rates_dataframe.iterrows():
            
            if isinstance(row['trade_open_close_indicator'], str):
                if 'short' in row['trade_short_or_long_indicator']:
                    if 'open' in row['trade_open_close_indicator']:
                        rates_dataframe.loc[idx, 'visual_indicator_position_short_trades'] = row['trade_open_price']
                    if 'close' in row['trade_open_close_indicator']:
                        rates_dataframe.loc[idx, 'visual_indicator_position_short_trades'] = row['trade_close_price']
                        
                if 'long' in row['trade_short_or_long_indicator']:
                    if 'open' in row['trade_open_close_indicator']:
                        rates_dataframe.loc[idx, 'visual_indicator_position_long_trades'] = row['trade_open_price']
                    if 'close' in row['trade_open_close_indicator']:
                        rates_dataframe.loc[idx, 'visual_indicator_position_long_trades'] = row['trade_close_price']
                
                        
        self.yaxis_visual_indicator_position_short_trades = rates_dataframe['visual_indicator_position_short_trades']
        self.yaxis_visual_indicator_position_long_trades = rates_dataframe['visual_indicator_position_long_trades']

    def execute(self, rates_dataframe):
        
        self.__set_common_styles()
        self.__set_styles_based_on_dataframe_data(rates_dataframe)
        
        self.fig, self.ax = plt.subplots(1,1, sharex="row", figsize=(16, 9), dpi=80, layout='tight', gridspec_kw={'height_ratios': [1]})
        
        self.__plot_separate_charts(rates_dataframe)

        print("Plotting chart...")
        plt.legend(loc='upper left')
        fig_manager = plt.get_current_fig_manager()
        fig_manager.resize(1600, 900)

        # self.__output_stdout()
        self.__save_fig()


