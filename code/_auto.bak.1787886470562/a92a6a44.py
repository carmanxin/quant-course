# @quantlab/output: a92a6a44
import numpy as np

def kelly_binary(p_win, win_loss_ratio):
    """
    二元结果的凯利公式

    Parameters:
        p_win: 胜率
        win_loss_ratio: 盈亏比（赢一次赚多少/输一次亏多少）
    Returns:
        f_star: 最优下注比例
    """
    f_star = (win_loss_ratio * p_win - (1 - p_win)) / win_loss_ratio
    return max(0, min(1, f_star))  # 限制在[0, 1]

def kelly_continuous(mu, sigma, rf=0):
    """
    连续收益的凯利公式

    Parameters:
        mu: 年化预期收益
        sigma: 年化波动率
        rf: 无风险利率
    Returns:
        f_star: 最优杠杆倍数
    """
    excess_return = mu - rf
    variance = sigma ** 2
    f_star = excess_return / variance
    return f_star

def fractional_kelly(f_star, fraction=0.5):
    """分数凯利"""
    return f_star * fraction
