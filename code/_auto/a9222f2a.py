# @quantlab/output: a9222f2a
import pandas as pd
import numpy as np

def build_panel_with_publication_dates(financial_data, report_dates,
                                        price_data, lookback=252):
    """
    构建避免前视偏差的面板数据集

    关键思想：财务数据的实际发布日期（report_dates）通常晚于报告期结束日期。
    回测时必须使用report_dates而非报告期日期来对齐。

    financial_data: DataFrame, index=stock_code, columns=财务指标
    report_dates: DataFrame, index=stock_code, values=发布日期
    price_data: DataFrame, index=date, columns=stock_code
    """
    aligned_data = {}

    for stock in financial_data.index:
        report_date = pd.Timestamp(report_dates.loc[stock, 'report_date'])
        financials = financial_data.loc[stock]

        # 只在发布日期之后才能使用该财务数据
        stock_prices = price_data[stock]
        valid_prices = stock_prices[stock_prices.index >= report_date]

        if len(valid_prices) > 0:
            for col in financials.index:
                aligned_data[(stock, col)] = financials[col]

    return aligned_data


class DataQualityMonitor:
    """
    持续监控数据质量的工具类，适用于实时或批量数据流
    """

    def __init__(self, price_bounds=None, volume_bounds=None):
        self.price_bounds = price_bounds or {}
        self.volume_bounds = volume_bounds or {}
        self.alerts = []

    def check_price_continuity(self, prices, max_gap_pct=0.20):
        """
        检查价格连续性：单日变动超过max_gap_pct可能为错误
        """
        returns = prices.pct_change()
        jumps = returns[returns.abs() > max_gap_pct]

        if len(jumps) > 0:
            for date, ret in jumps.items():
                self.alerts.append({
                    'type': 'price_jump',
                    'date': date,
                    'value': ret,
                    'severity': 'HIGH' if abs(ret) > 0.50 else 'MEDIUM'
                })
        return jumps

    def check_volume_anomaly(self, volumes, zscore_threshold=5):
        """
        成交量异常检测：相对历史均值偏离超过阈值
        """
        vol_mean = volumes.rolling(20).mean()
        vol_std = volumes.rolling(20).std()
        vol_zscore = (volumes - vol_mean) / vol_std

        anomalies = vol_zscore[vol_zscore.abs() > zscore_threshold]

        for date, z in anomalies.items():
            self.alerts.append({
                'type': 'volume_anomaly',
                'date': date,
                'zscore': z,
                'severity': 'MEDIUM'
            })
        return anomalies

    def check_ohlc_logic(self, ohlc_df):
        """
        检查OHLC数据的逻辑一致性
        - Low <= Open, Close, High
        - High >= Open, Close, Low
        - Low <= High
        """
        issues = {}

        # Low 不能高于 Open, Close, High
        issues['low_above_open'] = ohlc_df['low'] > ohlc_df['open']
        issues['low_above_close'] = ohlc_df['low'] > ohlc_df['close']
        issues['low_above_high'] = ohlc_df['low'] > ohlc_df['high']

        # High 不能低于 Open, Close, Low
        issues['high_below_open'] = ohlc_df['high'] < ohlc_df['open']
        issues['high_below_close'] = ohlc_df['high'] < ohlc_df['close']

        total_issues = sum(v.sum() for v in issues.values())

        if total_issues > 0:
            for name, mask in issues.items():
                if mask.any():
                    dates = ohlc_df.index[mask]
                    self.alerts.append({
                        'type': 'ohlc_logic',
                        'rule': name,
                        'count': len(dates),
                        'dates': dates[:5].tolist(),  # 只展示前5个
                        'severity': 'HIGH'
                    })

        return issues, total_issues

    def generate_report(self):
        """生成数据质量报告"""
        df_alerts = pd.DataFrame(self.alerts)

        if len(df_alerts) == 0:
            print("✅ 数据质量检查通过，未发现异常")
            return

        print("=" * 60)
        print(f"数据质量报告 - {len(df_alerts)} 个警报")
        print("=" * 60)

        severity_counts = df_alerts['severity'].value_counts()
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            if severity in severity_counts:
                print(f"  {severity}: {severity_counts[severity]} 个")

        print(f"\n按类型分组:")
        type_counts = df_alerts['type'].value_counts()
        for atype, count in type_counts.items():
            print(f"  {atype}: {count} 个")

        # 高严重性警报详情
        high_alerts = df_alerts[df_alerts['severity'] == 'HIGH']
        if len(high_alerts) > 0:
            print(f"\n=== 高严重性警报 ({len(high_alerts)}个) ===")
            for _, alert in high_alerts.head(10).iterrows():
                print(f"  [{alert['severity']}] {alert['type']}: {alert.to_dict()}")

        return df_alerts
