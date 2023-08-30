import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from src.backtest.Strategy import Strategy


class Backtest:
    def __init__(self, strategy: Strategy, initial_cash: int = 200000):
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.results = None
        self.bench = None
        self.position = 0

    def set_initial_cash(self, cash: int):
        self.initial_cash = cash

    def set_bench(self, bench: pd.DataFrame):
        self.bench = bench

    def compute_returns(self):
        # sim position
        for i in range(1, len(self.strategy.data)):
            if self.strategy.data['trade'].iloc[i] == 1 and self.position == 0:
                self.position = 1
            elif self.strategy.data['trade'].iloc[i] == -1 and self.position == 1:
                self.position = 0
            self.strategy.data.at[i, 'trade'] = self.position
        # calc returns
        self.strategy.data['market_return'] = self.strategy.data['close'].pct_change()
        self.strategy.data['strategy_return'] = (self.strategy.data['trade'].shift(1)
                                                 * self.strategy.data['market_return'])
        self.strategy.data['cumulative_market_return'] = (1 + self.strategy.data['market_return']).cumprod()
        self.strategy.data['cumulative_strategy_return'] = self.initial_cash * (
                1 + self.strategy.data['strategy_return']).cumprod()
        self.results = self.strategy.data

    def compute_returns_multistock(self):
        # market returns
        self.strategy.data['market_return_1'] = self.strategy.data['close_1'].pct_change()
        self.strategy.data['market_return_2'] = self.strategy.data['close_2'].pct_change()
        self.strategy.data['strategy_return'] = 0.0
        # backtest
        for i in range(1, len(self.strategy.data)):
            trade_list_str = self.strategy.data['trade'].iloc[i].split(';')
            trade_id_list_str = self.strategy.data['trade_id'].iloc[i].split(';')
            for j in range(1, len(trade_list_str)):
                trade = int(trade_list_str[j])
                trade_id = int(trade_id_list_str[j])
                if self.position != trade_id and trade == 1:
                    self.position = trade_id
                elif self.position != 0 and trade == -1:
                    self.position = 0
            if not self.position == 0:
                self.strategy.data.loc[i, 'strategy_return'] = self.strategy.data.loc[
                    i, f"market_return_{self.position}"]
        # calc returns
        self.strategy.data['cumulative_market_return_1'] = (1 + self.strategy.data['market_return_1']).cumprod()
        self.strategy.data['cumulative_market_return_2'] = (1 + self.strategy.data['market_return_2']).cumprod()
        self.strategy.data['cumulative_strategy_return'] = self.initial_cash * (
                1 + self.strategy.data['strategy_return']).cumprod()
        self.results = self.strategy.data
        self.results.to_csv('../assets/tmp.csv')
        print(f"ret = {(self.results['cumulative_strategy_return'].iloc[-1] - self.initial_cash) / self.initial_cash}")

    def compute_bench(self):
        if self.bench is not None:
            self.bench['market_return'] = self.bench['close'].pct_change()
            self.bench['cumulative_market_return'] = (1 + self.bench['market_return']).cumprod()

    def plot_results(self):
        if self.results is not None:
            plt.figure(figsize=(10, 6))

            # plot returns
            plt.plot(self.results['date'], (self.results['cumulative_market_return'] - 1), label='Stock',
                     color='blue')
            plt.plot(self.results['date'],
                     (self.results['cumulative_strategy_return'] - self.initial_cash) / self.initial_cash,
                     label='Strategy', color='red')
            if self.bench is not None:
                plt.plot(self.bench['date'], (self.bench['cumulative_market_return'] - 1), label='Bench',
                         color='gray')

            # date
            plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
            plt.gcf().autofmt_xdate()

            plt.title('Strategy vs. Market Performance')
            plt.legend()
            plt.xlabel('Date')
            plt.ylabel('Cumulative Returns')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            print("Please run the backtest before plotting.")

    def run(self, is_multi=False):
        self.strategy.trade()
        if not is_multi:
            self.compute_returns()
        else:
            self.compute_returns_multistock()

    def report(self):
        if self.results is not None:
            print("=====> BackTest Report <=====")
            total_market_return = self.results['cumulative_market_return'].iloc[-1] - 1
            total_strategy_return = (self.results['cumulative_strategy_return'].iloc[
                                         -1] - self.initial_cash) / self.initial_cash
            cum_returns = self.results['cumulative_strategy_return']
            # drawdown
            drawdown = cum_returns - cum_returns.cummax()
            max_drawdown = (drawdown.min() + self.initial_cash) / self.initial_cash - 1
            # annual returns
            annualized_return = (total_strategy_return + 1) ** (252 / len(cum_returns)) - 1
            annualized_volatility = self.results['strategy_return'].std() * (252 ** 0.5)
            # Sharpe ratio
            sharpe_ratio = annualized_return / annualized_volatility

            print(f"Total Market Return: {total_market_return * 100:.2f}%")
            print(f"Total Strategy Return: {total_strategy_return * 100:.2f}%")
            print(f"Max Drawdown: {max_drawdown:.2%}")
            print(f"Annualized Return: {annualized_return:.2%}")
            print(f"Annualized Volatility: {annualized_volatility:.2%}")
            print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
            print("=====>                 <=====")
        else:
            print("Err: please run backtest first!")
