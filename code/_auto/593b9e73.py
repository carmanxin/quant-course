# @quantlab/output: 593b9e73
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

@dataclass
class StrategyConfig:
    """策略配置参数"""
    # 数据
    start_date: str = '2020-01-01'
    end_date: str = '2024-12-31'
    universe_size: int = 300  # 最大股票池大小

    # 因子
    factors: List[str] = None
    factor_neutralize_industry: bool = True

    # 组合构建
    top_quantile: float = 0.20   # 选前20%
    rebalance_freq: str = 'M'    # 月度再平衡
    max_weight: float = 0.05     # 单只最大权重5%
    min_weight: float = 0.005    # 单只最小权重0.5%

    # 交易成本
    commission_bp: float = 2.0   # 佣金2bp
    slippage_bp: float = 5.0     # 滑点5bp
    spread_cost_bp: float = 3.0  # 价差成本3bp

    # 风险控制
    max_position_pct: float = 0.05  # 单只最大持仓
    stop_loss_pct: float = 0.15     # 单只止损线15%

    def __post_init__(self):
        if self.factors is None:
            self.factors = ['momentum', 'volatility', 'value', 'quality']

class EndToEndStrategy:
    """
    端到端量化策略流水线

    整合了本书中所有关键模块的完整策略示例
    """

    def __init__(self, config: StrategyConfig):
        self.config = config
        self.data = None
        self.factors = None
        self.signals = None
        self.portfolio = None
        self.results = {}

    def generate_sample_data(self, n_stocks=300, n_days=1250) -> pd.DataFrame:
        """生成示例数据用于演示（实际项目中替换为真实数据）"""
        np.random.seed(42)

        stocks = [f'STOCK_{i:04d}' for i in range(n_stocks)]
        dates = pd.date_range(self.config.start_date,
                             periods=n_days, freq='B')

        data_list = []

        for stock_id, stock in enumerate(stocks):
            # 每只股票生成独立的价格序列
            base_price = np.random.uniform(20, 200)
            mu = np.random.uniform(0.0001, 0.001)
            sigma = np.random.uniform(0.01, 0.04)

            log_returns = np.random.randn(n_days) * sigma + mu
            prices = base_price * np.exp(np.cumsum(log_returns))

            for t, (date, price) in enumerate(zip(dates, prices)):
                data_list.append({
                    'date': date,
                    'stock': stock,
                    'close': price,
                    'open': price * np.random.uniform(0.99, 1.01),
                    'high': price * np.random.uniform(1.00, 1.03),
                    'low': price * np.random.uniform(0.97, 1.00),
                    'volume': np.random.randint(100000, 10000000),
                    'market_cap': np.random.uniform(5e8, 5e11),
                    'industry': np.random.choice(
                        ['科技', '金融', '消费', '医药', '能源', '材料',
                         '工业', '地产', '公用', '通信'],
                        replace=False
                    )[0]
                })

        self.data = pd.DataFrame(data_list)
        self.data = self.data.sort_values(['date', 'stock']).reset_index(drop=True)

        print(f"数据生成完成: {len(stocks)} 只股票, {n_days} 个交易日")
        return self.data

    def compute_factors(self) -> pd.DataFrame:
        """计算因子值"""
        df = self.data.copy()

        # 动量因子：过去20日收益率
        df['momentum'] = df.groupby('stock')['close'].transform(
            lambda x: x.pct_change(20)
        )

        # 波动率因子：过去20日收益率标准差
        df['volatility'] = df.groupby('stock')['close'].transform(
            lambda x: x.pct_change().rolling(20).std()
        )

        # 价值因子：市值的倒数（小市值溢价）
        df['value'] = -np.log(df['market_cap'])

        # 质量因子：收益率/波动率（简化版）
        df['quality'] = df['momentum'] / (df['volatility'] + 1e-8)

        # 反转因子：过去5日收益率的负值
        df['reversal'] = df.groupby('stock')['close'].transform(
            lambda x: -x.pct_change(5)
        )

        # 换手率因子：成交量/市值
        df['turnover'] = df['volume'] / df['market_cap']

        # 因子截面标准化（Z-Score）
        factor_cols = self.config.factors + ['reversal', 'turnover']
        for col in factor_cols:
            if col in df.columns:
                df[col + '_z'] = df.groupby('date')[col].transform(
                    lambda x: (x - x.mean()) / (x.std() + 1e-8)
                )

        # 行业中性化（可选）
        if self.config.factor_neutralize_industry:
            for col in factor_cols:
                z_col = col + '_z'
                if z_col in df.columns:
                    neutralized = df.groupby(['date', 'industry'])[z_col].transform(
                        lambda x: x - x.mean()
                    )
                    df[col + '_neutral'] = neutralized
                    # 使用中性化后的因子
                    df[z_col] = neutralized

        # 处理极端值
        for col in factor_cols:
            z_col = col + '_z'
            if z_col in df.columns:
                df[z_col] = df[z_col].clip(-3, 3)
                df[z_col] = df[z_col].fillna(0)

        self.factors = df
        print(f"因子计算完成: {factor_cols}")
        return df

    def compute_ic(self) -> pd.DataFrame:
        """计算因子IC"""
        df = self.factors.copy()

        # 未来1日收益率
        df['fwd_ret_1d'] = df.groupby('stock')['close'].transform(
            lambda x: x.shift(-1) / x - 1
        )

        ic_results = []
        factor_cols = [c for c in df.columns if c.endswith('_z')]

        for date in df['date'].unique():
            day_data = df[df['date'] == date].dropna(subset=['fwd_ret_1d'])
            if len(day_data) < 30:
                continue

            for col in factor_cols:
                valid = day_data[[col, 'fwd_ret_1d']].dropna()
                if len(valid) < 30:
                    continue
                ic = stats.spearmanr(valid[col], valid['fwd_ret_1d'])[0]
                ic_results.append({'date': date, 'factor': col, 'IC': ic})

        ic_df = pd.DataFrame(ic_results)

        # 汇总
        print("\n因子IC分析:")
        print("-" * 55)
        print(f"{'因子':<20} {'IC均值':>8} {'IC std':>8} {'ICIR':>8} {'胜率':>8}")
        print("-" * 55)

        ic_summary = []
        for col in factor_cols:
            factor_ic = ic_df[ic_df['factor'] == col]['IC']
            if len(factor_ic) > 0:
                ic_mean = factor_ic.mean()
                ic_std = factor_ic.std()
                icir = ic_mean / ic_std if ic_std > 0 else 0
                hit_rate = (factor_ic > 0).mean()
                print(f"{col:<20} {ic_mean:>8.4f} {ic_std:>8.4f} {icir:>8.3f} {hit_rate:>7.1%}")
                ic_summary.append({
                    'factor': col, 'IC_mean': ic_mean, 'IC_std': ic_std,
                    'ICIR': icir, 'hit_rate': hit_rate
                })

        return pd.DataFrame(ic_summary)

    def build_signal(self) -> pd.DataFrame:
        """构建综合信号"""
        df = self.factors.copy()

        # 等权综合信号
        signal_cols = [c for c in df.columns if c.endswith('_z')]
        df['composite_signal'] = df[signal_cols].mean(axis=1)

        # 信号排名（截面百分位）
        df['signal_rank'] = df.groupby('date')['composite_signal'].transform(
            lambda x: x.rank(pct=True)
        )

        self.signals = df
        print(f"信号构建完成: 综合 {len(signal_cols)} 个因子")
        return df

    def run_backtest(self) -> Dict:
        """执行回测"""
        df = self.signals.copy()
        config = self.config

        # 再平衡日期
        if config.rebalance_freq == 'M':
            df['year_month'] = df['date'].dt.to_period('M')
            rebalance_dates = df.groupby('year_month')['date'].max().values
        else:
            rebalance_dates = df['date'].unique()

        # 回测主循环
        portfolio_values = []
        holdings = {}
        cash = 1_000_000.0  # 初始资金100万
        equity_curve = []
        trades_log = []

        for i, date in enumerate(rebalance_dates):
            if date not in df['date'].values:
                continue

            day_data = df[df['date'] == date].copy()

            # 选择Top 20%的股票
            threshold = day_data['signal_rank'].quantile(1 - config.top_quantile)
            selected = day_data[day_data['signal_rank'] >= threshold]

            # 等权配仓
            n_selected = len(selected)
            if n_selected == 0:
                equity_curve.append({'date': date, 'equity': cash})
                continue

            weight_per_stock = min(1.0 / n_selected, config.max_weight)

            # 计算总持仓价值
            total_market_value = cash

            # 清仓当前持有
            for stock, shares in list(holdings.items()):
                stock_data = day_data[day_data['stock'] == stock]
                if not stock_data.empty:
                    sell_price = stock_data.iloc[0]['close']
                    sell_value = shares * sell_price * (1 - config.commission_bp/10000)
                    cash += sell_value
                    trades_log.append({
                        'date': date, 'stock': stock, 'action': 'SELL',
                        'shares': shares, 'price': sell_price, 'value': sell_value
                    })
            holdings.clear()

            # 买入新选中的股票
            allocated_per_stock = cash * weight_per_stock
            for _, row in selected.iterrows():
                stock = row['stock']
                buy_price = row['close']

                # 考虑滑点（买入时略高）
                effective_price = buy_price * (1 + config.slippage_bp/10000)

                shares = int(allocated_per_stock / effective_price)
                if shares > 0:
                    cost = shares * effective_price * (1 + config.commission_bp/10000)
                    if cost <= cash:
                        cash -= cost
                        holdings[stock] = shares
                        trades_log.append({
                            'date': date, 'stock': stock, 'action': 'BUY',
                            'shares': shares, 'price': effective_price, 'value': cost
                        })

            # 计算当前净值
            equity = cash
            for stock, shares in holdings.items():
                stock_data = day_data[day_data['stock'] == stock]
                if not stock_data.empty:
                    equity += shares * stock_data.iloc[0]['close']

            equity_curve.append({'date': date, 'equity': equity, 'cash': cash,
                                'n_holdings': len(holdings)})

        # 计算绩效指标
        equity_df = pd.DataFrame(equity_curve)
        equity_df['returns'] = equity_df['equity'].pct_change()

        total_return = equity_df['equity'].iloc[-1] / equity_df['equity'].iloc[0] - 1
        n_years = len(equity_df) / 252
        annual_return = (1 + total_return) ** (1 / n_years) - 1
        annual_vol = equity_df['returns'].std() * np.sqrt(252)
        sharpe = annual_return / annual_vol if annual_vol > 0 else 0

        # 最大回撤
        cummax = equity_df['equity'].cummax()
        drawdown = equity_df['equity'] / cummax - 1
        max_drawdown = drawdown.min()

        self.results = {
            'equity_curve': equity_df,
            'trades': trades_log,
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'calmar_ratio': annual_return / abs(max_drawdown) if max_drawdown != 0 else 0,
            'n_trades': len(trades_log) // 2,  # 买卖配对
            'n_years': n_years,
        }

        print(f"\n回测完成!")
        return self.results

    def print_summary(self):
        """打印策略摘要"""
        r = self.results
        if not r:
            print("请先执行 run_backtest()")
            return

        print("\n" + "=" * 55)
        print("终极项目 - 策略回测摘要")
        print("=" * 55)
        print(f"  回测周期: {self.config.start_date} ~ {self.config.end_date}")
        print(f"  年数: {r['n_years']:.1f}")
        print(f"\n  [收益指标]")
        print(f"  累计收益率:   {r['total_return']:>10.2%}")
        print(f"  年化收益率:   {r['annual_return']:>10.2%}")
        print(f"  年化波动率:   {r['annual_volatility']:>10.2%}")
        print(f"\n  [风险调整指标]")
        print(f"  夏普比:       {r['sharpe_ratio']:>10.3f}")
        print(f"  最大回撤:     {r['max_drawdown']:>10.2%}")
        print(f"  Calmar比:     {r['calmar_ratio']:>10.3f}")
        print(f"\n  [交易统计]")
        print(f"  交易对数:     {r['n_trades']:>10}")
        print("=" * 55)

# ===== 执行终极项目 =====

config = StrategyConfig(
    start_date='2020-01-01',
    end_date='2024-12-31',
    factors=['momentum', 'volatility', 'value', 'quality'],
    factor_neutralize_industry=True,
    top_quantile=0.20,
    rebalance_freq='M',
)

strategy = EndToEndStrategy(config)
strategy.generate_sample_data(n_stocks=300, n_days=1250)
strategy.compute_factors()
strategy.compute_ic()
strategy.build_signal()
strategy.run_backtest()
strategy.print_summary()
