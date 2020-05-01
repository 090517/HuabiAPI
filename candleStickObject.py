import requests
import json
import pandas as pd
import mplfinance as mpf
import time


class CandleStickStorage:
    def __init__(self, period: str, ticker: str):
        self.ticker = ticker
        if period not in ["1min", "5min", "15min", "30min", "60min", "4hour", "1day", "1mon", "1year"]:
            raise Exception(
                'period is incorrect entry')  # valid entries are 1min, 5min, 15min, 30min, 60min, 4hour, 1day, 1mon, 1week, 1year
        self.period = period
        self.data = []

    # returns url string to update data
    def returnUrl(self):
        return "https://api.huobi.pro/market/history/kline?period=" + self.period + "&size=2000&symbol=" + self.ticker

    # updates the data for the given ticker/period
    def updateData(self):
        httpreturn=requests.get(self.returnUrl()).text
        #put into while true, catch loop as it kept throwing errors from reading too fast the return before loading.
        counter=0
        while True:
            try:
                json_return = json.loads(httpreturn)
            except:
                time.sleep(.5)
                counter+=1
                if counter>5: #counter to resubmit html if it doesn't load for 2.5s
                    httpreturn = requests.get(self.returnUrl()).text
                    counter=0
                continue
            break

        if json_return['status'] == 'ok':
            self.data = pd.DataFrame(json_return['data']).sort_values(axis="index", by='id',
                                                                      ascending=True).reset_index(drop=True)
            self.data['Date'] = pd.to_datetime(self.data['id'], unit='s')
            self.data['typicalprice'] = (self.data['high'] + self.data['low'] + self.data['close']) / 3
        else:
            raise Exception('API status not ok')

    # returns if last candle was green/red
    def lastCandleTrend(self):
        max = self.data['id'].idxmax()  # gets row index of latest candle
        lastCandle = self.data.iloc[max]
        if lastCandle.close > lastCandle.open:
            return "Upward trend"
        elif lastCandle.close == lastCandle.open:
            return "Flat trend"
        elif lastCandle.close < lastCandle.open:
            return "Downward trend"
        else:
            raise Exception('Last candle trend error')

    # returns series of nperiod moving average
    def movingAverage(self, nPeriods:int):
        return self.data['typicalprice'].rolling(window=nPeriods).mean()

    # returns series of upper and lower BB bands for given nperiods and sd
    def bolingerBand(self, nPeriods:int, SD:int):
        output = pd.DataFrame()
        output['upperBB'] = self.movingAverage(nPeriods) + SD * self.data['typicalprice'].rolling(window=nPeriods).std()
        output['lowerBB'] = self.movingAverage(nPeriods) - SD * self.data['typicalprice'].rolling(window=nPeriods).std()
        return output

    #plots data TODO add bb bands to graph, along with maybe volume?
    def plot(self):
        temp = self.data.set_index('Date')
        mpf.plot(temp.rename(columns={'open': 'Open',
                                      'high': 'High',
                                      'low': 'Low',
                                      'close': 'Close'}))
