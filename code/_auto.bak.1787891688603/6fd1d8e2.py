# @quantlab/output: 6fd1d8e2
import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple


class ABTestAnalyzer:
    """量化策略 A/B 测试分析器"""

    def __init__(self, returns_a: pd.Series, returns_b: pd.Series,
                 benchmark_returns: pd.Series = None):
        """
        Parameters
        ----------
        returns_a : pd.Series
            对照组（A）的日度收益序列
        returns_b : pd.Series
            实验组（B）的日度收益序列
        benchmark_returns : pd.Series, optional
            基准收益序列，用于计算 Alpha
        """
        self.returns_a = returns_a
        self.returns_b = returns_b
        self.benchmark = benchmark_returns

    def basic_stats(self) -> pd.DataFrame:
        """计算两组的基本统计量"""
        stats_dict = {}
        for name, rets in [('A', self.returns_a), ('B', self.returns_b)]:
            rets = rets.dropna()
            stats_dict[name] = {
                'mean_daily': rets.mean(),
                'std_daily': rets.std(),
                'skewness': rets.skew(),
                'kurtosis': rets.kurtosis(),
                'annual_return': rets.mean() * 252,
                'annual_vol': rets.std() * np.sqrt(252),
                'sharpe': (rets.mean() / rets.std()) * np.sqrt(252) if rets.std() > 0 else 0,
                'max_drawdown': (rets.cumsum() - rets.cumsum().cummax()).min(),
                'win_rate': (rets > 0).mean(),
                'n_days': len(rets)
            }
        return pd.DataFrame(stats_dict)

    def two_sample_ttest(self) -> dict:
        """两样本 t 检验（Welch's t-test，不假设方差相等）"""
        rets_a = self.returns_a.dropna()
        rets_b = self.returns_b.dropna()

        t_stat, p_value = stats.ttest_ind(rets_b, rets_a, equal_var=False)

        return {
            'method': "Welch's t-test",
            't_statistic': t_stat,
            'p_value': p_value,
            'significant_5pct': p_value < 0.05,
            'significant_1pct': p_value < 0.01
        }

    def bootstrap_test(self, n_bootstrap: int = 10000,
                       statistic: str = 'sharpe') -> dict:
        """
        Bootstrap 检验：对夏普比率差异进行 Bootstrap

        Parameters
        ----------
        n_bootstrap : int
            Bootstrap 抽样次数
        statistic : str
            比较的统计量，'sharpe' 或 'mean'
        """
        rets_a = self.returns_a.dropna().values
        rets_b = self.returns_b.dropna().values

        def compute_stat(r):
            ann_r = r.mean() * 252
            if statistic == 'sharpe':
                ann_vol = r.std() * np.sqrt(252)
                return ann_r / ann_vol if ann_vol > 0 else 0
            return ann_r

        obs_diff = compute_stat(rets_b) - compute_stat(rets_a)

        # Bootstrap
        np.random.seed(42)
        boot_diffs = []
        for _ in range(n_bootstrap):
            a_sample = np.random.choice(rets_a, size=len(rets_a), replace=True)
            b_sample = np.random.choice(rets_b, size=len(rets_b), replace=True)
            boot_diffs.append(compute_stat(b_sample) - compute_stat(a_sample))

        boot_diffs = np.array(boot_diffs)

        # 双尾 p 值
        p_value = np.mean(np.abs(boot_diffs) >= np.abs(obs_diff))

        return {
            'method': f'Bootstrap ({statistic})',
            'observed_difference': obs_diff,
            'bootstrap_mean': boot_diffs.mean(),
            'bootstrap_std': boot_diffs.std(),
            'ci_95_lower': np.percentile(boot_diffs, 2.5),
            'ci_95_upper': np.percentile(boot_diffs, 97.5),
            'p_value': p_value,
            'significant_5pct': p_value < 0.05
        }

    def permutation_test(self, n_permutations: int = 10000) -> dict:
        """排列检验：无假设的 A/B 差异检验"""
        rets_a = self.returns_a.dropna().values
        rets_b = self.returns_b.dropna().values

        combined = np.concatenate([rets_a, rets_b])
        n_a = len(rets_a)

        obs_diff = rets_b.mean() - rets_a.mean()

        np.random.seed(42)
        perm_diffs = []
        for _ in range(n_permutations):
            np.random.shuffle(combined)
            perm_diffs.append(combined[:n_a].mean() - combined[n_a:].mean())

        perm_diffs = np.array(perm_diffs)
        p_value = np.mean(np.abs(perm_diffs) >= np.abs(obs_diff))

        return {
            'method': 'Permutation Test',
            'observed_difference': obs_diff,
            'p_value': p_value,
            'significant_5pct': p_value < 0.05
        }

    def calculate_required_sample_size(self, effect_size: float = 0.2,
                                        power: float = 0.8) -> int:
        """
        计算所需样本量

        Parameters
        ----------
        effect_size : float
            期望检测到的最小效应量（以年化夏普差异表示）
        power : float
            统计功效（1 - Type II Error）
        """
        daily_effect = effect_size / np.sqrt(252)
        daily_std = self.returns_a.std()

        # Cohen's d
        d = daily_effect / daily_std

        # 近似公式计算所需样本量（每组）
        from scipy.stats import norm
        z_alpha = norm.ppf(0.975)  # 双尾 5% 显著性
        z_beta = norm.ppf(power)

        n = 2 * ((z_alpha + z_beta) / d) ** 2
        return int(np.ceil(n))

    def generate_report(self) -> str:
        """生成 A/B 测试综合报告"""
        basic = self.basic_stats()
        ttest = self.two_sample_ttest()
        boot = self.bootstrap_test()
        perm = self.permutation_test()

        report_lines = [
            "=" * 60,
            "          量化策略 A/B 测试报告",
            "=" * 60,
            "",
            "【基本统计】",
            basic.to_string(),
            "",
            "【统计检验结果】",
            "",
            f"1. {ttest['method']}:",
            f"   t = {ttest['t_statistic']:.4f}, p = {ttest['p_value']:.4f}",
            f"   5%显著性: {'是' if ttest['significant_5pct'] else '否'}",
            "",
            f"2. {boot['method']}:",
            f"   观测差异 = {boot['observed_difference']:.4f}",
            f"   95% CI = [{boot['ci_95_lower']:.4f}, {boot['ci_95_upper']:.4f}]",
            f"   p = {boot['p_value']:.4f}",
            f"   5%显著性: {'是' if boot['significant_5pct'] else '否'}",
            "",
            f"3. {perm['method']}:",
            f"   观测差异 = {perm['observed_difference']:.4f}",
            f"   p = {perm['p_value']:.4f}",
            "",
            "【结论】",
        ]

        # 综合判断
        if ttest['p_value'] < 0.05 and boot['p_value'] < 0.05:
            report_lines.append("B组显著优于A组，建议推进到下一阶段。")
        elif ttest['p_value'] < 0.1:
            report_lines.append("B组有一定优势但不够显著，建议延长测试时间。")
        else:
            report_lines.append("A/B两组无显著差异，B组的改进可能无效。")

        return '\n'.join(report_lines)
