import pandas as pd

from src.backtest.Strategy import Strategy
from open_quant_data.dataset.thirdparty.akshare.AkshareDataset import AkshareDataset


class BondDiffStrategy(Strategy):
    def load_datasets(self, csv1: str, csv2: str):
        dataset1 = pd.read_csv(csv1)
        dataset2 = pd.read_csv(csv2)
        dataset1 = AkshareDataset.between_date(dataset1, '2023-01-01', '2023-08-28')
        dataset2 = AkshareDataset.between_date(dataset2, '2023-01-01', '2023-08-28')
        dataset1 = dataset1.rename(columns={'close': 'close_1'})
        dataset2 = dataset2.rename(columns={'close': 'close_2'})
        self.data = pd.merge(dataset1[['date', 'close_1']], dataset2[['date', 'close_2']], on='date', how='outer')
        self.data['diff'] = self.data['close_2'] - self.data['close_1']

    def trade(self):
        pass
