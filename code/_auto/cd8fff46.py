# @quantlab/output: cd8fff46
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ProcessingArchitecture(ABC):
    """
    量化数据处理的抽象基类，定义批处理和流处理的统一接口。
    """

    @abstractmethod
    def process(self, data, **kwargs):
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        pass


class BatchProcessor(ProcessingArchitecture):
    """
    日终批处理器：在每日收盘后运行，处理全量历史数据。

    适用场景：因子计算、风险模型估计、日频回测数据准备。
    """

    def __init__(self, data_source: str, output_path: str):
        self.data_source = data_source
        self.output_path = output_path
        self.state = {'last_run': None, 'records_processed': 0}

    def process(self,
                date: str,
                symbols: Optional[list] = None) -> pd.DataFrame:
        """
        对指定日期的全量数据进行批处理。

        典型流程：
        1. 读取原始数据
        2. 数据清洗和标准化
        3. 计算日频因子
        4. 写入结果存储
        """
        # 读取原始数据
        raw_data = self._read_raw_data(date, symbols)

        # 数据清洗
        clean_data = self._cleanse(raw_data)

        # 因子计算
        factors = self._compute_factors(clean_data)

        # 写入结果
        self._write_output(factors, date)

        # 更新状态
        self.state['last_run'] = date
        self.state['records_processed'] += len(clean_data)

        return factors

    def _read_raw_data(self, date: str, symbols: list) -> pd.DataFrame:
        """从分区存储中读取指定日期的原始数据"""
        date_path = f"{self.data_source}/{date.replace('-', '')}"
        return pd.read_parquet(date_path)

    def _cleanse(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据清洗管道"""
        # 去重
        data = data.drop_duplicates()
        # 过滤无效价格
        data = data[data['price'] > 0]
        # 过滤非交易时段
        data = data[
            (data['timestamp'].dt.time >= pd.Timestamp('09:30').time()) &
            (data['timestamp'].dt.time <= pd.Timestamp('16:00').time())
        ]
        return data

    def _compute_factors(self, data: pd.DataFrame) -> pd.DataFrame:
        """因子计算引擎"""
        grouped = data.groupby('symbol')

        factors = pd.DataFrame(index=data['symbol'].unique())

        # 日频因子
        factors['daily_return'] = grouped['price'].apply(
            lambda x: x.iloc[-1] / x.iloc[0] - 1
        )
        factors['realized_vol'] = grouped['price'].apply(
            lambda x: np.std(np.diff(np.log(x))) * np.sqrt(252)
        )
        factors['volume'] = grouped['size'].sum()
        factors['vwap'] = grouped.apply(
            lambda g: np.average(g['price'], weights=g['size'])
        )

        return factors

    def _write_output(self, factors: pd.DataFrame, date: str):
        """写入处理结果"""
        output_file = f"{self.output_path}/factors/{date.replace('-', '')}.parquet"
        factors.to_parquet(output_file)

    def get_state(self) -> Dict[str, Any]:
        return self.state


class StreamProcessor(ProcessingArchitecture):
    """
    实时流处理器：持续处理流入的数据，维护增量状态。

    适用场景：实时特征、实时风险监控、实时信号生成。
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.window_buffer: Dict[str, list] = {}  # {symbol: [prices]}
        self.state = {'messages_processed': 0, 'last_update': None}

    def process(self,
                tick: Dict[str, Any],
                symbol: str) -> Optional[Dict[str, float]]:
        """
        处理单个 tick，更新滚动窗口状态并计算实时特征。

        返回:
            当前窗口的实时特征字典，如果窗口数据不足则返回 None
        """
        # 初始化窗口
        if symbol not in self.window_buffer:
            self.window_buffer[symbol] = []

        # 更新窗口
        self.window_buffer[symbol].append(tick['price'])

        # 维护窗口大小
        if len(self.window_buffer[symbol]) > self.window_size:
            self.window_buffer[symbol] = \
                self.window_buffer[symbol][-self.window_size:]

        # 窗口数据不足
        if len(self.window_buffer[symbol]) < self.window_size:
            return None

        prices = np.array(self.window_buffer[symbol])
        returns = np.diff(np.log(prices))

        # 实时特征
        features = {
            'real_time_vwap': np.mean(prices),
            'real_time_vol': np.std(returns) * np.sqrt(252),
            'real_time_skew': pd.Series(returns).skew(),
            'real_time_momentum': prices[-1] / prices[-self.window_size] - 1,
            'bid_ask_spread': tick.get('ask', 0) - tick.get('bid', 0)
        }

        self.state['messages_processed'] += 1
        self.state['last_update'] = tick.get('timestamp')

        return features

    def get_state(self) -> Dict[str, Any]:
        return self.state
