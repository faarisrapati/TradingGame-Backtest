"""Technical indicators used by the game and strategy backtest."""

import pandas as pd
import talib


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Add EMA, RSI, MACD, and relative-volume columns using past data only."""
    result = data.copy()
    close = result["Close"].astype(float).to_numpy()
    volume = result["Volume"].astype(float)

    result["EMA_20"] = talib.EMA(close, timeperiod=20)
    result["EMA_50"] = talib.EMA(close, timeperiod=50)
    result["RSI_14"] = talib.RSI(close, timeperiod=14)
    macd, macd_signal, macd_histogram = talib.MACD(
        close, fastperiod=12, slowperiod=26, signalperiod=9
    )
    result["MACD"] = macd
    result["MACD_Signal"] = macd_signal
    result["MACD_Histogram"] = macd_histogram
    average_volume = volume.rolling(window=20, min_periods=20).mean()
    result["RVOL"] = volume.div(average_volume)
    return result
