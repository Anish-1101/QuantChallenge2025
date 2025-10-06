QuantChallenge2025 - Anish Athmakoor & Ted Smith Submission

This repo contains two parts: a modeling workflow to predict targets (Y1, Y2) from time-ordered data, and a live trading bot that reacts to basketball game events to trade a win-probability contract.

Research (prediction)

The training file has time and market features A–N with targets Y1 and Y2, the test file has later times with the same features and an id column. The score is the average R² for Y1 and Y2.

Our implementation treats the data as a timeline, aligns all sources, then builds simple market-style signals from each feature, including recent values, short-term changes, moving averages, and rolling min/max. We keep the time order, use walk-forward validation to avoid leakage, compare several regression models, and average the strongest performers. The result is predictions for Y1 and Y2.

Trading (live strategy)

The trader ingests real-time events (scores, rebounds, steals, fouls, etc.) and keeps track of score differential, possession, and a short-lived “momentum” signal. It turns these into a continuously updated estimate of the home team’s win chance, which is more sensitive late in the game. When that estimate disagrees with market prices by enough margin, the bot buys or sells; otherwise it places passive quotes and manages inventory. Risk is controlled with caps on exposure, sensible sizing, and automatic flattening near the end of the game.