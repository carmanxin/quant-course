# @quantlab/output: 3f6d46f2
def psa_prepayment_model(loan_age_months, psa_speed=100):
    """
    PSA 标准提前还款模型
    loan_age_months: 贷款已存续的月数
    psa_speed: PSA速度倍数（100=标准, 150=快, 50=慢）
    """
    if loan_age_months <= 30:
        cpr = 0.06 * (loan_age_months / 30)
    else:
        cpr = 0.06

    # 根据 PSA 速度倍数调整
    cpr *= (psa_speed / 100)

    # 转换为单月死亡率（SMM）
    smm = 1 - (1 - cpr) ** (1/12)
    return cpr, smm

# 模拟不同 PSA 速度下的提前还款曲线
for psa in [50, 100, 150, 200]:
    cprs = [psa_prepayment_model(m, psa)[0] for m in range(1, 361)]
    print(f"PSA {psa}: 第360个月 CPR = {cprs[-1]:.2%}")
