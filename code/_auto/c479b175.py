# @quantlab/output: c479b175
import numpy as np

def pass_through_cashflows(original_balance, wac, wam, servicing_fee, cpr_assumption):
    """
    过手证券现金流模拟
    original_balance: 初始本金余额
    wac: 加权平均票面利率（年化）
    wam: 加权平均剩余期限（月）
    servicing_fee: 服务费率（年化）
    cpr_assumption: CPR 提前还款率假设（年化百分比）

    返回：每月现金流列表
    """
    n_months = wam
    balance = original_balance
    net_rate = (wac - servicing_fee) / 12
    smm = 1 - (1 - cpr_assumption) ** (1/12)  # 单月死亡率

    cashflows = []
    for month in range(1, n_months + 1):
        scheduled_principal = balance / (n_months - month + 1)  # 简化:等额本金
        interest = balance * net_rate
        prepayment = (balance - scheduled_principal) * smm
        total_principal = scheduled_principal + prepayment
        total_cf = total_principal + interest

        cashflows.append({
            'month': month,
            'beginning_balance': balance,
            'interest': interest,
            'scheduled_principal': scheduled_principal,
            'prepayment': prepayment,
            'total_principal': total_principal,
            'total_cashflow': total_cf
        })

        balance -= total_principal
        if balance <= 0:
            break

    return cashflows
