# @quantlab/output: 2ab5dad7
import pandas as pd
import numpy as np

# 假设df包含：Close（收盘价）、signal（0/1信号，1表示持有）
returns = df['Close'].pct_change()
strategy_returns = returns * df['signal'].shift(1)
cumulative = (1 + strategy_returns).cumprod()
