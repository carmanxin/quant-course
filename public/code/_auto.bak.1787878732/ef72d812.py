# @quantlab/output: ef72d812
class OverfittingDefenseChecklist:
    """过拟合防御检查清单"""

    def __init__(self):
        self.checks = []

    def run_all_checks(self, strategy_name,
                       in_sample_sharpe, out_sample_sharpe,
                       n_parameters_tested, n_factors_tested,
                       model_complexity, is_purged_cv_used,
                       has_true_oos_period):
        """
        执行所有过拟合防御检查

        model_complexity: 模型参数数量（或决策树深度等代理指标）
        """
        checks = []

        # 检查1: 样本内 vs 样本外夏普比差异
        degradation = (in_sample_sharpe - out_sample_sharpe) / in_sample_sharpe
        checks.append({
            'check': 'IS/OOS Sharpe差异',
            'value': f"下滑 {degradation:.0%}",
            'passed': degradation < 0.5,
            'warning': '样本内外的巨大差异表明严重过拟合'
        })

        # 检查2: 参数/因子测试量 vs 数据量
        df_factor = n_parameters_tested + n_factors_tested
        checks.append({
            'check': '数据挖掘自由度',
            'value': f"测试了 {df_factor} 个组合",
            'passed': df_factor < 100,
            'warning': '大量测试增加了假阳性风险，考虑计算DSR'
        })

        # 检查3: 模型复杂度
        checks.append({
            'check': '模型复杂度',
            'value': f"{model_complexity} 个参数",
            'passed': model_complexity < 50,
            'warning': '复杂模型在小数据集上极易过拟合'
        })

        # 检查4: 是否使用Purged CV
        checks.append({
            'check': 'Purged交叉验证',
            'value': '使用' if is_purged_cv_used else '未使用',
            'passed': is_purged_cv_used,
            'warning': '不使用Purged CV会导致信息泄露'
        })

        # 检查5: 是否有真正的样本外验证
        checks.append({
            'check': '真正OOS验证',
            'value': '有' if has_true_oos_period else '无',
            'passed': has_true_oos_period,
            'warning': '没有OOS验证的策略不应该进入实盘'
        })

        self.checks = checks

        print(f"\n策略 '{strategy_name}' 过拟合防御检查:")
        print("=" * 60)
        all_passed = True
        for c in checks:
            status = "PASS" if c['passed'] else "FAIL"
            print(f"[{status}] {c['check']:>20}: {c['value']:>20}")
            if not c['passed']:
                print(f"       WARNING: {c['warning']}")
                all_passed = False

        if all_passed:
            print("\n  所有检查通过！策略具有较好的稳健性。")
        else:
            print(f"\n  有 {sum(1 for c in checks if not c['passed'])} 项未通过，建议修复后再上线。")

        return all_passed

# 示例
checker = OverfittingDefenseChecklist()
checker.run_all_checks(
    strategy_name="Multi-Factor Momentum",
    in_sample_sharpe=2.5,
    out_sample_sharpe=1.1,
    n_parameters_tested=300,
    n_factors_tested=50,
    model_complexity=12,
    is_purged_cv_used=True,
    has_true_oos_period=True
)
