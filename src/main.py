from backtest.Backtest import Backtest
from backtest.strategies.MACDStrategy import MACDStrategy

from open_quant_data.stat.MACDUtils import MACDUtils

import pandas as pd

from src.backtest.strategies.BondDiffStrategy import BondDiffStrategy


def test_macd_strategy():
    strategy = MACDStrategy(pd.read_csv('../assets/data.csv'))
    MACDUtils.plot_macd(pd.read_csv('../assets/data.csv')['close'].tolist())
    backtester = Backtest(strategy)
    backtester.set_initial_cash(200000)
    backtester.run()
    backtester.report()
    # bench
    backtester.set_bench(pd.read_csv('../assets/bench.csv'))
    backtester.compute_bench()
    # visualize
    backtester.plot_results()


def test_bond_diff_strategy():
    strategy = BondDiffStrategy(pd.DataFrame())
    strategy.load_datasets('../assets/bond/sz127022.csv', '../assets/bond/sz127067.csv')
    backtester = Backtest(strategy)
    backtester.set_initial_cash(200000)
    backtester.run(is_multi=True)


if __name__ == '__main__':
    test_bond_diff_strategy()
