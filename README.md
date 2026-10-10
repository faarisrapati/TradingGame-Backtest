# MarketLab

### Read the chart. Understand the signal. Test the idea.

MarketLab is a stock market learning app I built with **Python and Streamlit** for **KnightHacks 2026**. It started with my interest in trading and technical analysis. I wanted to go beyond looking at stock charts and actually build something where people could practice reading them and test whether a simple trading strategy would have worked in the past.

The app has two main parts: a **Trading Game**, where you make predictions using historical stock charts, and a **Strategy Lab**, where you backtest a moving-average strategy with virtual money. Both use real historical market data, but **no real money or trades are involved**.

## Trading Game

The Trading Game is meant to make learning about stock charts a little more hands-on. Instead of being told what happened to a stock, you look at the information that was available at a particular point in the past and decide what you think will happen next.

Each game has **10 rounds**. In a round, MarketLab picks a stock and a historical date, then shows roughly **60 trading sessions** of price history. You can look at the candlestick chart and technical indicators before predicting whether the closing price will be **higher or lower five trading sessions later**.

Once you submit your prediction, the game reveals the next five candles and shows whether you were correct. It also keeps track of your score, streaks, and previous rounds.

There's also a simple algorithm you can compete against. It predicts **UP** when the 20-day EMA is above the 50-day EMA and RSI is below 70; otherwise, it predicts **DOWN**. I included it to show how a consistent set of rules compares with a person's judgment. **It's a rule-based opponent, not an AI or machine-learning prediction model.**

You can also take the selected stock into Strategy Lab to explore its historical performance in more detail.

## Strategy Lab

The Strategy Lab is where you can test a trading idea instead of just guessing a stock's direction.

You choose a stock, a testing period (**1, 2, 3, or 5 years**), and how much virtual money to start with. MarketLab then runs a backtest using a **20-day and 50-day exponential moving average (EMA) crossover strategy**.

The rules are straightforward:

1. **Buy** when the 20-day EMA crosses above the 50-day EMA.
2. **Sell** when the 20-day EMA crosses below the 50-day EMA.
3. Make the simulated trade at the **next trading day's opening price**, after the signal is known.

That third step matters. If a backtest uses a day's closing price to calculate a signal and then pretends it traded at that same closing price, it can produce unrealistic results. Executing at the next open helps avoid that kind of **look-ahead bias**.

The simulation uses available virtual cash to buy whole shares and tracks the portfolio over time. It also compares the strategy against **buy-and-hold**, which means buying the stock at the beginning and holding it through the same period.

The results show:

- Final portfolio value and total return
- Strategy performance compared with buy-and-hold
- Interactive portfolio-value chart and trade entry/exit markers
- Number of completed trades and percentage of winning trades
- Average profit or loss per completed trade
- Maximum drawdown (the largest decline from a previous portfolio peak)

I wanted the results to show more than just whether the strategy made money. A strategy can have a positive return and still perform worse than buying and holding, or experience large losses along the way.

**Current limitations:** The backtester uses a single long-only strategy and whole-share trades. It doesn't model commissions, slippage, taxes, or every real-world trading constraint. The statistics for completed trades also don't include a position that remains open at the end of the test.

## Market Data and Indicators

MarketLab gets historical daily stock data from **yfinance**. The data is cleaned and organized with **pandas**, and Streamlit caches downloads for an hour so the app doesn't need to request the same information every time you click something.

I used these indicators:

| Indicator | What it helps show |
| --- | --- |
| **EMA 20 and EMA 50** | Shorter-term and longer-term price trends |
| **RSI (14)** | Recent price momentum |
| **MACD (12, 26, 9)** | Changes in momentum and trend direction |
| **RVOL (20)** | Whether volume is higher or lower than its recent average |

The current version supports **10 stocks**: AAPL, MSFT, NVDA, AMD, META, AMZN, GOOGL, TSLA, NFLX, and AVGO.

## Tools I Used

- **Python** — the main language for the game, calculations, and backtester
- **Streamlit** — the website interface and game state
- **yfinance** — historical stock prices
- **pandas** — cleaning and working with market data
- **TA-Lib** — calculating technical indicators
- **Plotly** — interactive charts
- **pytest** — automated testing during development
- **Git and GitHub** — tracking and sharing the project

I also used **AI coding assistance** during development to help with implementation and debugging. This project gave me a chance to work through how the different parts fit together, especially the financial calculations, game logic, and backtesting assumptions.

## How the Code Is Organized

I separated the project into a few Python files so everything wouldn't be inside one large script:

```text
TradingGame-Backtest/
├── app.py             # Main Streamlit app and navigation
├── game.py            # Prediction game and scoring
├── strategy_lab.py    # Strategy Lab interface and results
├── backtest.py        # EMA strategy and backtesting calculations
├── indicators.py      # Technical indicator calculations
├── stock_data.py      # Downloading and cleaning stock data
├── requirements.txt   # Required Python libraries
└── README.md
```

For example, `stock_data.py` handles getting the historical prices, while `backtest.py` handles the simulated trades and performance calculations. That makes it easier to change one part without rewriting the whole app.

## Running MarketLab

If you'd like to run the project on your own computer, clone the repository and open the project folder:

```bash
git clone https://github.com/faarisrapati/TradingGame-Backtest.git
cd TradingGame-Backtest
```

Install the Python libraries and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```



## What I Want to Build Next

I see MarketLab as a starting point rather than a finished trading platform. Right now it lets people practice reading charts and test one simple strategy. There are a lot of directions I could take it from here.

**Stock screening** is one of the biggest. Instead of looking at one stock at a time, I want users to be able to search across the S&P 500 and eventually more of the market for stocks that match certain conditions, such as an EMA crossover, strong relative volume, or a particular RSI range.

I'd also like to add a **custom strategy builder**, where users could combine indicators and create their own rules without having to write Python code. The Strategy Lab could then compare different strategies, add more realistic assumptions like trading fees and slippage, and test ideas across different market conditions.

For the game, I could add difficulty levels, more indicators, leaderboards, and explanations after each prediction so users learn *why* a setup might have looked bullish or bearish—even when the prediction turned out wrong.

Eventually, I'd love to explore portfolio backtesting, more detailed risk analysis, and an educational AI assistant that helps explain charts and strategy results rather than simply telling people what to buy.

The bigger idea is to connect everything in one place: **learn about an indicator, practice using it, build a strategy around it, and test that strategy against historical data**. That's the direction I want MarketLab to grow in.

## About the Project

I built MarketLab as a **solo KnightHacks 2026 project** while learning more about Python, financial data, and app development. It began as a trading-analysis script and grew into something interactive that other people can try.

My main goal was to make the process of learning about markets more approachable, while also getting hands-on experience building a complete application.

I wanted to focus on this project because it directly relates to what I am trying to do career wise but also as a side hustle as a college student. I want to enter the FinTech realm and also I want to use my own detailed script and indicator strategies to apply to my own trading.
