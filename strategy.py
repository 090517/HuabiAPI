import json
import sys
import requests
import pandas as pd
import threading
import time

sys.path.append('D:\Dropbox\Projects\Python\Huobi')
from candleStickObject import CandleStickStorage

# import all the tickers
tickerUrl = "https://api.huobi.pro/market/tickers"
json_return = json.loads(requests.get(tickerUrl).text)
if json_return['status'] == 'ok':
    tickersList = pd.DataFrame(json_return['data'])['symbol']
else:
    raise Exception('API status not ok')

#tickersList = tickersList[0:9]  # comment out after debuing.  Just limits the tickers to 10 for faster iteration.

# create 30 minute candle database set for all tickers
min30CandleSticks = []
for ticker in tickersList:
    min30CandleSticks.append(CandleStickStorage("30min", ticker))

# create 5 mint candle database set for all tickers
min5CandleSticks = []
for ticker in tickersList:
    min5CandleSticks.append(CandleStickStorage("5min", ticker))

# create output dataframe to handle final result
outputFrame = tickersList.to_frame()
outputFrame["Position"] = "None"
outputFrame.set_index('symbol', drop=True, inplace=True)

# while running loop
# while True: #uncomment this for true while loop

# update all the data, #todo make this even faster.... already multithreaded but optimize better...
listOfThreads = []
for dataObject in min30CandleSticks:
    thread = threading.Thread(target=dataObject.updateData)
    thread.start()
    print("Updating 30 min:" + dataObject.ticker)
    listOfThreads.append(thread)

for dataObject in min5CandleSticks:
    thread = threading.Thread(target=dataObject.updateData)
    thread.start()
    print("Updating 5 min:" + dataObject.ticker)
    listOfThreads.append(thread)

for thread in listOfThreads:
    thread.join()

# if no position, and last 30 minute candle was upward trending,
for dataObject in min30CandleSticks:
    if (outputFrame.loc[dataObject.ticker, "Position"] != "Long") and dataObject.lastCandleTrend() == "Upward trend":
        outputFrame.loc[dataObject.ticker, "Position"] = "Buy"

# if has long position, and 6 period moving average is below the previos period's 1sd lower Bolingerband, sell the long position
for dataObject in min5CandleSticks:
    if (outputFrame.loc[dataObject.ticker, "Position"] == "Long") and dataObject.movingAverage(nPeriods=6).iloc[-1] < \
            dataObject.bolingerBand(nPeriods=6, SD=1).iloc[-2]["lowerBB"]:
        outputFrame.loc[dataObject.ticker, "Position"] = "Sell"

#todo Think if it's possible for both conditions to be true... upward trending last candle, but lower than the BB bound..

# code to execute trades here
print(outputFrame)

# Reset the status so sells are removed, and buys are replaced with "long" signifying it's been bought.  This is assuming long only.
outputFrame.replace(to_replace="sell", value="None", inplace=True)
outputFrame.replace(to_replace="Buy", value="Long", inplace=True)
print(outputFrame)
