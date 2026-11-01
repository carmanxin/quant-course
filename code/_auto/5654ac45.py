# @quantlab/output: 5654ac45
class TurtleTradingSystem:
    """
    海龟交易法则的完整实现

    包含两个子系统：
    - System 1: 20日通道突破入场, 10日通道突破出场
    - System 2: 55日通道突破入场, 20日通道突破出场
    """
    def __init__(self, atr_period=20, risk_per_trade=0.01):
        self.atr_period = atr_period
        self.risk_per_trade = risk_per_trade

    def compute_signals(self, df):
        """计算双系统信号"""
        data = df.copy()

        # 通道
        for period in [10, 20, 55]:
            data[f'high_{period}'] = data['High'].rolling(period).max().shift(1)
            data[f'low_{period}'] = data['Low'].rolling(period).min().shift(1)

        # System 1 entry: 20日突破
        data['sys1_entry_long'] = data['Close'] > data['high_20']
        data['sys1_entry_short'] = data['Close'] < data['low_20']
        # System 1 exit: 10日反向突破
        data['sys1_exit_long'] = data['Close'] < data['low_10']
        data['sys1_exit_short'] = data['Close'] > data['high_10']

        # System 2 entry: 55日突破
        data['sys2_entry_long'] = data['Close'] > data['high_55']
        data['sys2_entry_short'] = data['Close'] < data['low_55']
        # System 2 exit: 20日反向突破
        data['sys2_exit_long'] = data['Close'] < data['low_20']
        data['sys2_exit_short'] = data['Close'] > data['high_20']

        return data

    def compute_atr(self, df):
        """计算ATR"""
        data = df.copy()
        data['prev_close'] = data['Close'].shift(1)
        data['tr1'] = data['High'] - data['Low']
        data['tr2'] = abs(data['High'] - data['prev_close'])
        data['tr3'] = abs(data['Low'] - data['prev_close'])
        data['TR'] = data[['tr1', 'tr2', 'tr3']].max(axis=1)
        data['ATR'] = data['TR'].rolling(self.atr_period).mean()
        return data['ATR']

    def position_sizing(self, capital, atr, point_value, max_units=None):
        """
        海龟仓位计算

        Parameters:
            capital: 当前账户总资金
            atr: 当前ATR值
            point_value: 每点价值（如股指期货每点300元）
            max_units: 最大持仓手数（单个品种上限）
        """
        risk_amount = capital * self.risk_per_trade
        units = int(risk_amount / (atr * point_value))

        if max_units:
            units = min(units, max_units)

        return max(units, 1)  # 最少1手
