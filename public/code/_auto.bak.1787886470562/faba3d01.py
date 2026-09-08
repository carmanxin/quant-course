# @quantlab/output: faba3d01
def calculate_cds_bond_basis(cds_spread, bond_ytm, risk_free_rate):
    """
    计算 CDS-Bond Basis
    """
    # 资产的互换利差 (Asset Swap Spread) 近似为债券信用利差
    bond_credit_spread = bond_ytm - risk_free_rate
    basis = cds_spread - bond_credit_spread

    return {
        'cds_spread': cds_spread,
        'bond_credit_spread': bond_credit_spread,
        'basis': basis,
        'basis_bps': basis * 10000
    }
