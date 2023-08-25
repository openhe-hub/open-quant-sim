import numpy as np
import pandas as pd

from src.backtest.Strategy import Strategy
from open_quant_data.stat.MACDUtils import MACDUtils


class MACDStrategy(Strategy):
    def trade(self):
        macd = MACDUtils.macd_details(self.data['close'].tolist())
        self.data = pd.concat([self.data, macd], axis=1)
        self.data['trade'] = 0
        golden_cross = ((self.data['dif'].shift(1) <= self.data['dea'].shift(1))
                        & (self.data['dif'] > self.data['dea']))
        death_cross = ((self.data['dif'].shift(1) >= self.data['dea'].shift(1))
                       & (self.data['dif'] < self.data['dea']))
        self.data.loc[golden_cross, 'trade'] = 1
        self.data.loc[death_cross, 'trade'] = -1
