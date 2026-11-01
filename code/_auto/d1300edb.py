# @quantlab/output: d1300edb
def sequential_pay_cmo(pool_cashflows, tranche_sizes):
    """
    顺序支付 CMO 的现金流分配
    pool_cashflows: 整个贷款池的现金流
    tranche_sizes: 各档的初始本金 [tranche_A, tranche_B, ...]
    """
    n_tranches = len(tranche_sizes)
    remaining = list(tranche_sizes)
    tranche_cfs = [[] for _ in range(n_tranches)]
    active_tranche = 0

    for cf in pool_cashflows:
        total_principal = cf['total_principal']

        # 按顺序分配本金
        for t in range(active_tranche, n_tranches):
            if total_principal <= 0:
                break
            allocated = min(total_principal, remaining[t])
            remaining[t] -= allocated
            total_principal -= allocated

            # 计算利息分配
            interest_allocation = remaining[t] * cf['interest'] / cf['beginning_balance']
            tranche_cfs[t].append({
                'month': cf['month'],
                'principal': allocated,
                'interest': interest_allocation,
                'remaining_balance': remaining[t]
            })

            if remaining[t] <= 0:
                active_tranche = t + 1

    return tranche_cfs
