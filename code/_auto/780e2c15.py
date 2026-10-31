# @quantlab/output: 780e2c15
def implied_rate_probability(futures_price: float,
                              current_ffr: float,
                              hike_size_bps: int = 25,
                              days_to_meeting: int = None,
                              days_in_month: int = 30) -> dict:
    """
    从联邦基金期货价格提取隐含的加息概率。

    参数:
        futures_price: 期货合约价格（100 - 隐含利率）
        current_ffr: 当前联邦基金有效利率（%）
        hike_size_bps: 预期的加息幅度（基点）
        days_to_meeting: 距离FOMC会议的天数
        days_in_month: 合约月份的总天数
    返回:
        包含隐含利率、加息概率的字典
    """
    # 期货隐含利率
    implied_rate = 100 - futures_price

    # 如果会议在月内某天
    if days_to_meeting is not None and days_in_month > 0:
        # 会后天数
        days_after = days_in_month - days_to_meeting

        # 隐含利率 = (会前天数/总天数) * 当前利率
        #           + (会后天数/总天数) * (当前利率 + 加息幅度 * 概率)
        # 求解概率
        rate_if_hike = current_ffr + hike_size_bps / 100
        rate_if_no_hike = current_ffr

        prob_hike = (implied_rate - rate_if_no_hike) / \
                    (rate_if_hike - rate_if_no_hike + 1e-10)
        prob_hike = np.clip(prob_hike, 0, 1)
    else:
        prob_hike = (implied_rate - current_ffr) / (hike_size_bps / 100)
        prob_hike = np.clip(prob_hike, 0, 1)

    return {
        'futures_price': futures_price,
        'implied_rate_pct': implied_rate,
        'current_ffr_pct': current_ffr,
        'prob_hike': prob_hike,
        'prob_no_change': 1 - prob_hike
    }
