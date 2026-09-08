# @quantlab/output: 6d48d9aa
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

def enhanced_investment_clock(growth_momentum: float,
                               inflation_momentum: float,
                               credit_momentum: float,
                               thresholds: dict = None) -> dict:
    """
    三维增强版美林时钟。

    参数:
        growth_momentum: 增长动量（标准化后的趋势强度）
        inflation_momentum: 通胀动量
        credit_momentum: 信用条件动量（正=信贷宽松，负=信贷紧缩）
        thresholds: 各维度的阈值
    返回:
        包含阶段分类和资产配置建议的字典
    """
    if thresholds is None:
        thresholds = {
            'growth': 0.0,
            'inflation': 0.0,
            'credit': 0.0
        }

    # 确定状态
    growth_state = 'up' if growth_momentum > thresholds['growth'] else 'down'
    infl_state = 'up' if inflation_momentum > thresholds['inflation'] else 'down'
    credit_state = 'tight' if credit_momentum < thresholds['credit'] else 'loose'

    # 8种可能的状态组合
    state = (growth_state, infl_state, credit_state)

    # 状态与资产配置的映射
    config_map = {
        ('up', 'down', 'loose'): {
            'phase': 'Goldilocks (金发姑娘)',
            'equity': 0.55, 'bonds': 0.25, 'commodities': 0.10, 'cash': 0.10,
            'description': '最佳宏观环境：增长强劲、通胀温和、流动性充裕'
        },
        ('up', 'down', 'tight'): {
            'phase': 'Recovery with Tight Credit',
            'equity': 0.40, 'bonds': 0.30, 'commodities': 0.15, 'cash': 0.15,
            'description': '增长恢复但信贷偏紧'
        },
        ('up', 'up', 'loose'): {
            'phase': 'Overheat (过热)',
            'equity': 0.30, 'bonds': 0.05, 'commodities': 0.45, 'cash': 0.20,
            'description': '通胀压力上升'
        },
        ('up', 'up', 'tight'): {
            'phase': 'Tightening Cycle (紧缩周期)',
            'equity': 0.20, 'bonds': 0.20, 'commodities': 0.30, 'cash': 0.30,
            'description': '央行收紧政策对抗通胀'
        },
        ('down', 'up', 'loose'): {
            'phase': 'Stagflation-lite (轻滞胀)',
            'equity': 0.20, 'bonds': 0.10, 'commodities': 0.30, 'cash': 0.40,
            'description': '增长放缓但通胀仍高'
        },
        ('down', 'up', 'tight'): {
            'phase': 'Stagflation (滞胀)',
            'equity': 0.15, 'bonds': 0.15, 'commodities': 0.25, 'cash': 0.45,
            'description': '最糟糕组合：低增长+高通胀+紧信用'
        },
        ('down', 'down', 'loose'): {
            'phase': 'Early Recession (衰退初期)',
            'equity': 0.25, 'bonds': 0.50, 'commodities': 0.10, 'cash': 0.15,
            'description': '经济下行，债券为王'
        },
        ('down', 'down', 'tight'): {
            'phase': 'Credit Crunch (信用紧缩)',
            'equity': 0.10, 'bonds': 0.40, 'commodities': 0.10, 'cash': 0.40,
            'description': '信用收缩加剧经济下行'
        }
    }

    allocation = config_map.get(state, config_map[('down', 'down', 'tight')])

    return allocation
