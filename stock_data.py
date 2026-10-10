"""Download and clean historical daily stock data."""

import pandas as pd
import streamlit as st
import yfinance as yf


SUPPORTED_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMD", "META", "AMZN", "GOOGL", "TSLA", "NFLX", "AVGO"
]
PRICE_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]


def clean_stock_data(data: pd.DataFrame) -> pd.DataFrame:
    """Return sorted, numeric OHLCV data with timezone-free dates."""
    if data is None or data.empty:
        return pd.DataFrame(columns=PRICE_COLUMNS)

    cleaned = data.copy()
    if isinstance(cleaned.columns, pd.MultiIndex):
        cleaned.columns = cleaned.columns.get_level_values(0)
    new_columns = []

    for column in cleaned.columns:
        new_columns.append(str(column).title())

    cleaned.columns = new_columns

    if isinstance(cleaned.index, pd.DatetimeIndex) and cleaned.index.tz is not None:
        cleaned.index = cleaned.index.tz_localize(None)
    cleaned.index.name = "Date"

    missing_columns = [column for column in PRICE_COLUMNS if column not in cleaned.columns]
    if missing_columns:
        raise ValueError("The downloaded data is missing required price columns.")

    cleaned = cleaned[PRICE_COLUMNS].sort_index()
    for column in PRICE_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    cleaned = cleaned.dropna(subset=PRICE_COLUMNS)
    return cleaned


@st.cache_data(ttl=3600, show_spinner=False)
def _download_stock_data(ticker: str) -> pd.DataFrame:
    """Cache one five-year adjusted-price download for an hour."""
    history = yf.Ticker(ticker).history(period="5y", auto_adjust=True)
    cleaned = clean_stock_data(history)
    if cleaned.empty:
        raise ValueError("Yahoo Finance returned no historical prices for this stock.")
    return cleaned


def get_stock_data(ticker: str) -> pd.DataFrame:
    """Fetch cached historical data and provide a friendly error on failure."""
    if ticker not in SUPPORTED_TICKERS:
        raise ValueError("Choose a stock from the supported ticker list.")
    try:
        return _download_stock_data(ticker)
    except Exception as error:
        if isinstance(error, ValueError) and str(error).startswith("Yahoo Finance returned"):
            raise
        raise ValueError(
            "Historical prices are temporarily unavailable. Please try again in a moment."
        ) from error