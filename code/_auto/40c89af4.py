# @quantlab/output: 40c89af4
import numpy as np
from scipy.optimize import minimize

class PortfolioOptimizerWithConstraints:
    """
    带完整约束的投资组合优化器
    """
    def __init__(self, mu, Sigma, benchmark_weights=None):
        self.mu = mu
        self.Sigma = Sigma
        self.n = len(mu)
        self.benchmark_weights = benchmark_weights

    def build_constraints(self, config):
        """
        构建约束条件

        config keys:
            - long_only: bool, 是否只做多
            - max_weight: float, 单只股票最大权重
            - industry_mapping: dict, stock_idx -> industry_name
            - industry_neutral: bool, 是否行业中性
            - factor_exposures: np.array (n, k), 因子暴露矩阵
            - factor_neutral: list, 需要中性的因子索引
            - current_weights: np.array, 当前持仓
            - max_turnover: float, 最大单边换手率
        """
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]  # 权重和为1

        # 目标收益（MVO）
        if 'target_return' in config:
            constraints.append({
                'type': 'eq',
                'fun': lambda w, r=config['target_return']: w @ self.mu - r
            })

        # 行业中性
        if config.get('industry_neutral') and config.get('industry_mapping'):
            industries = set(config['industry_mapping'].values())
            for ind in industries:
                ind_mask = np.array([
                    config['industry_mapping'].get(i) == ind
                    for i in range(self.n)
                ], dtype=float)
                # 组合行业权重 = 基准行业权重
                if self.benchmark_weights is not None:
                    bench_ind_weight = np.sum(
                        [self.benchmark_weights[i] for i in range(self.n)
                         if config['industry_mapping'].get(i) == ind]
                    )
                    constraints.append({
                        'type': 'eq',
                        'fun': lambda w, m=ind_mask, b=bench_ind_weight: w @ m - b
                    })

        # 因子中性（如Beta中性、市值中性）
        if config.get('factor_neutral') and config.get('factor_exposures') is not None:
            for j in config['factor_neutral']:
                factor_vec = config['factor_exposures'][:, j]
                constraints.append({
                    'type': 'eq',
                    'fun': lambda w, f=factor_vec: w @ f - 0  # 中性化到0
                })

        # 换手率约束
        if config.get('current_weights') is not None and config.get('max_turnover'):
            current_w = np.array(config['current_weights'])
            max_to = config['max_turnover']

            def turnover_constraint(w):
                return max_to - 0.5 * np.sum(np.abs(w - current_w))
            constraints.append({'type': 'ineq', 'fun': turnover_constraint})

        return constraints

    def build_bounds(self, config):
        """构建权重边界"""
        if config.get('long_only', True):
            lower = 0.0
        else:
            lower = -0.5  # 最多做空50%

        max_w = config.get('max_weight', 1.0)
        return [(lower, max_w) for _ in range(self.n)]

    def optimize(self, objective_type='min_variance', config=None):
        """
        执行带约束的组合优化

        objective_type:
            - 'min_variance': 最小方差组合
            - 'max_sharpe': 最大夏普比率
            - 'risk_parity': 风险平价
        """
        if config is None:
            config = {}

        constraints = self.build_constraints(config)
        bounds = self.build_bounds(config)

        if objective_type == 'min_variance':
            def objective(w):
                return w @ self.Sigma @ w
        elif objective_type == 'max_sharpe':
            def objective(w):
                port_mu = w @ self.mu
                port_sigma = np.sqrt(w @ self.Sigma @ w)
                return -(port_mu / port_sigma)  # 最小化 -夏普
        elif objective_type == 'risk_parity':
            def objective(w):
                port_vol = np.sqrt(w @ self.Sigma @ w)
                rc = w * (self.Sigma @ w) / port_vol
                target = 1.0 / self.n
                return np.sum((rc - target) ** 2)

        w0 = np.ones(self.n) / self.n
        result = minimize(objective, w0, method='SLSQP',
                          bounds=bounds, constraints=constraints,
                          options={'maxiter': 5000, 'ftol': 1e-10})

        if not result.success:
            print(f"警告：优化未收敛 - {result.message}")

        return result.x
