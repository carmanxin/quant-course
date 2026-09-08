# @quantlab/output: 2b0a8c30
import numpy as np
import pandas as pd
from scipy import stats

class AlternativeDataPipeline:
    """另类数据处理流水线"""

    def __init__(self, ticker_mapping):
        """
        ticker_mapping: dict, 映射私募公司名到上市公司ticker
        例: {'ByteDance': '私人公司', 'Apple Inc.': 'AAPL'}
        """
        self.ticker_mapping = ticker_mapping
        self.processed_data = {}

    def load_raw_data(self, source_name, raw_df):
        """加载原始数据"""
        self.processed_data[source_name] = {'raw': raw_df, 'clean': None, 'signals': None}

    def clean_panel_data(self, source_name, date_col, entity_col, value_col):
        """
        清洗面板数据：
        1. 去除重复
        2. 对齐时间戳到交易日
        3. 处理异常值
        4. 填充缺失值
        """
        df = self.processed_data[source_name]['raw'].copy()

        # 1. 去重
        df = df.drop_duplicates(subset=[date_col, entity_col])

        # 2. 确保日期列格式正确
        df[date_col] = pd.to_datetime(df[date_col])

        # 3. 按日聚合（如果有日内数据）
        df = df.groupby([date_col, entity_col])[value_col].mean().reset_index()

        # 4. 异常值处理 (MAD方法)
        median = df[value_col].median()
        mad = stats.median_abs_deviation(df[value_col].dropna())
        df[value_col] = df[value_col].clip(median - 5*mad, median + 5*mad)

        # 5. 填充缺失值（前向填充，最多7天）
        df = df.set_index([date_col, entity_col])
        df = df.unstack(level=entity_col)
        df = df.ffill(limit=7)
        df = df.stack(level=entity_col).reset_index()

        self.processed_data[source_name]['clean'] = df
        return df

    def compute_signals(self, source_name, entity_col, value_col,
                        signal_type='zscore', lookback=20):
        """
        将原始另类数据转换为量化信号

        signal_type: 'zscore', 'pct_change', 'diff', 'rank'
        """
        df = self.processed_data[source_name]['clean'].copy()

        if signal_type == 'zscore':
            # 滚动Z-Score: (值 - 均值) / 标准差
            grouped = df.groupby(entity_col)[value_col]
            rolling_mean = grouped.transform(lambda x: x.rolling(lookback, min_periods=5).mean())
            rolling_std = grouped.transform(lambda x: x.rolling(lookback, min_periods=5).std())
            df['signal'] = (df[value_col] - rolling_mean) / rolling_std

        elif signal_type == 'pct_change':
            # 变化率
            df['signal'] = df.groupby(entity_col)[value_col].transform(
                lambda x: x.pct_change(periods=lookback)
            )

        elif signal_type == 'diff':
            # 差分
            df['signal'] = df.groupby(entity_col)[value_col].transform(
                lambda x: x.diff(periods=lookback)
            )

        elif signal_type == 'rank':
            # 截面排名（每日）
            df['signal'] = df.groupby('date')[value_col].transform(
                lambda x: x.rank(pct=True)  # 百分位排名 (0到1)
            )

        # 信号清洗
        df['signal'] = df['signal'].clip(-3, 3)  # winsorize信号
        df['signal'] = df['signal'].fillna(0)

        self.processed_data[source_name]['signals'] = df
        return df

    def map_to_tickers(self, source_name, entity_col):
        """将实体映射到上市公司ticker"""
        df = self.processed_data[source_name]['signals']
        df['ticker'] = df[entity_col].map(self.ticker_mapping)
        df = df.dropna(subset=['ticker'])  # 移除无法映射的
        return df

    def aggregate_signals(self, date):
        """将多个另类数据源的信号聚合为综合信号"""
        all_signals = []

        for source_name, data in self.processed_data.items():
            if data['signals'] is not None:
                signals_df = data['signals']
                # 筛选指定日期的数据
                day_signals = signals_df[signals_df['date'] == date]
                if not day_signals.empty:
                    all_signals.append(day_signals[['ticker', 'signal']].set_index('ticker'))

        if not all_signals:
            return pd.Series(dtype=float)

        # 等权聚合（实际应用中可以使用IC加权）
        combined = pd.concat(all_signals, axis=1)
        combined.columns = [f'source_{i}' for i in range(len(all_signals))]
        combined['aggregate'] = combined.mean(axis=1)

        return combined['aggregate']

# ===== 使用示例 =====
pipeline = AlternativeDataPipeline(ticker_mapping={
    'Company_A': 'AAPL',
    'Company_B': 'TSLA',
    'Company_C': 'NVDA',
})

# 模拟电商排名数据
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=60, freq='D')
entities = ['Company_A', 'Company_B', 'Company_C']

raw_data = []
for entity in entities:
    base_rank = np.random.randint(10, 100)
    for i, date in enumerate(dates):
        rank = base_rank + np.random.randint(-5, 6) + int(2 * np.sin(i/10))
        raw_data.append([date, entity, max(1, rank)])

ecommerce_df = pd.DataFrame(raw_data, columns=['date', 'entity', 'sales_rank'])
pipeline.load_raw_data('ecommerce', ecommerce_df)
pipeline.clean_panel_data('ecommerce', 'date', 'entity', 'sales_rank')
pipeline.compute_signals('ecommerce', 'entity', 'sales_rank', signal_type='zscore', lookback=14)
signals = pipeline.map_to_tickers('ecommerce', 'entity')

print("另类数据信号示例 (电商排名 -> 交易信号):")
print(signals.head(15).to_string(index=False))

# 聚合信号
agg = pipeline.aggregate_signals(dates[-1])
print(f"\n{dates[-1].date()} 综合另类数据信号:")
print(agg.to_string())
