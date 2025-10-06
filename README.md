Overview
QuantChallenge2025 - Anish Athmakoor & Ted Smith Submission

This repo contains two parts: a modeling workflow to predict targets (Y1, Y2) from time-ordered data, and a live trading bot that reacts to basketball game events to trade a win-probability contract.

Research (prediction)

We treat the data as a time-ordered stream of market indicators, align multiple sources into a single timeline, and transform them into simple signals such as recent levels, short-term changes, and rolling summaries to capture trend and momentum. Models are evaluated with walk-forward time-series validation to prevent leakage, we compare several forecasters and keep those that generalize best, then average them to produce stable predictions for Y1 and Y2.

Trading (live strategy)

The trader ingests real-time events (scores, rebounds, steals, fouls, etc.) and keeps track of score differential, possession, and a short-lived “momentum” signal. It turns these into a continuously updated estimate of the home team’s win chance, which is more sensitive late in the game. When that estimate disagrees with market prices by enough margin, the bot buys or sells; otherwise it places passive quotes and manages inventory. Risk is controlled with caps on exposure, sensible sizing, and automatic flattening near the end of the game.