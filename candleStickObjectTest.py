import json
import requests
import matplotlib.pyplot as plt
import sys

sys.path.append('D:\Dropbox\Projects\Python\Huobi')  # replace with path to library if on other computer.
from candleStickObject import CandleStickStorage

min30CandleStick = CandleStickStorage("30min", "btcusdt")
min30CandleStick.updateData()
print("last candlestick trend was:" + min30CandleStick.lastCandleTrend())
print("moving 5 period averages are:\n" + str(min30CandleStick.movingAverage(5)))
print("bb bands for 5 periods:\n" + str(min30CandleStick.bolingerBand(5, 2)))
bb = (min30CandleStick.bolingerBand(5, 2))
df = min30CandleStick.data
min30CandleStick.plot()
