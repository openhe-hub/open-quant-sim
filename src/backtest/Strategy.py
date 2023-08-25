import pandas as pd


class Strategy:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def trade(self):
        raise NotImplementedError("Err: you should implement this method to use strategy!")
