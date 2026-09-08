# @quantlab/output: 42088b49
import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict

class FactorResearchDemo:
    """
    因子研究的标准工作流演示

    这套流程涵盖了研究员日常工作的核心环节，
    也是量化研究员面试中常见的技术测试内容。
    """

    def __init__(self, data_provider=None):
        self.data = data_provider
        self.factor_cache = {}

    def research_workflow(self, factor_name, factor_func,
                          price_data, universe) -> Dict:
        """
        标准的因子研究流程:
        1. 因子计算
        2. 截面标准化
        3. IC分析
        4. 分层回测
        5. 行业中性化验证
        6. 因子相关性分析
        """
        results = {'factor_name': factor_name}

        # Step 1: 计算因子值
        factor_values = factor_func(price_data)

        # Step 2: 截面标准化
        factor_zscore = factor_values.groupby('date').transform(
            lambda x: (x - x.mean()) / x.std()
        )

        # Step 3: IC分析
        forward_returns = price_data.groupby('stock')['close'].transform(
            lambda x: x.shift(-1) / x - 1  # 未来1日收益率
        )

        ic_series = factor_zscore.groupby('date').apply(
            lambda x: stats.spearmanr(x, forward_returns.loc[x.index])[0]
            if len(x.dropna()) > 20 else np.nan
        )

        results['IC_mean'] = ic_series.mean()
        results['IC_std'] = ic_series.std()
        results['ICIR'] = ic_series.mean() / ic_series.std() if ic_series.std() > 0 else 0
        results['IC_positive_ratio'] = (ic_series > 0).mean()

        # Step 4: 分层回测 (Quick and Dirty)
        factor_zscore.name = 'factor'
        forward_returns.name = 'fwd_ret'
        combined = pd.concat([factor_zscore, forward_returns], axis=1).dropna()

        n_quantiles = 5
        combined['quantile'] = combined.groupby('date')['factor'].transform(
            lambda x: pd.qcut(x, n_quantiles, labels=False, duplicates='drop')
        )

        quantile_returns = combined.groupby(['date', 'quantile'])['fwd_ret'].mean()
        quantile_returns = quantile_returns.unstack()

        # Top减Bottom的多空组合
        if 0 in quantile_returns.columns and (n_quantiles-1) in quantile_returns.columns:
            long_short = quantile_returns[n_quantiles-1] - quantile_returns[0]
            results['long_short_mean'] = long_short.mean()
            results['long_short_sharpe'] = long_short.mean() / long_short.std() * np.sqrt(252)

        results['quantile_returns'] = quantile_returns.mean().to_dict()

        return results

    def generate_research_report(self, results: Dict) -> str:
        """生成因子研究简报"""
        report = f"""
========================================
因子研究报告: {results['factor_name']}
========================================

[IC分析]
  IC均值:    {results.get('IC_mean', np.nan):.4f}
  IC标准差:  {results.get('IC_std', np.nan):.4f}
  ICIR:      {results.get('ICIR', np.nan):.4f}
  IC正比率:  {results.get('IC_positive_ratio', np.nan):.1%}

[分层收益]
"""
        if 'quantile_returns' in results:
            for q, ret in sorted(results['quantile_returns'].items()):
                report += f"  Q{q+1}: 日均收益 = {ret:.6f}\n"

        if 'long_short_sharpe' in results:
            report += f"""
[多空组合]
  多空日均收益: {results.get('long_short_mean', 0):.6f}
  多空夏普比:   {results.get('long_short_sharpe', 0):.3f}

========================================
评估结论: ...
========================================
"""
        return report

demo = FactorResearchDemo()
print("因子研究工作流演示就绪\n")
print("量化研究员的核心技能要求:")
print("  1. Python/R编程 (NumPy/Pandas/scikit-learn)")
print("  2. 统计学基础 (假设检验/回归分析/时间序列)")
print("  3. 机器学习 (XGBoost/神经网络/特征工程)")
print("  4. 金融市场知识 (因子模型/市场微观结构/投资组合理论)")
print("  5. 学术文献阅读 (能将论文中的想法转化为可测试的策略)")
print("  6. 沟通能力 (向非量化人员解释策略逻辑和风险)")
