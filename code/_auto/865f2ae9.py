# @quantlab/output: 865f2ae9
def dark_pool_execution_analysis(orders_history):
    """
    分析暗池执行的绩效

    orders_history: 订单执行记录列表
    """
    results = {
        'total_orders': len(orders_history),
        'filled_in_dark': 0,
        'filled_in_lit': 0,
        'unfilled': 0,
        'avg_price_improvement_bp': 0,
        'avg_wait_time_seconds': 0,
    }

    improvements = []
    wait_times = []

    for order in orders_history:
        if order['status'] == 'FILLED':
            if order['venue'] in ('DARK_A', 'DARK_B', 'INT'):
                results['filled_in_dark'] += 1
                improve = (order['nbbo_mid'] - order['fill_price']) / order['nbbo_mid']
                improvements.append(improve)
            else:
                results['filled_in_lit'] += 1
            wait_times.append(order['fill_time'] - order['send_time'])
        else:
            results['unfilled'] += 1

    if improvements:
        results['avg_price_improvement_bp'] = np.mean(improvements) * 10000
    if wait_times:
        results['avg_wait_time_seconds'] = np.mean(wait_times)

    print("暗池执行绩效分析:")
    print(f"  总订单: {results['total_orders']}")
    print(f"  暗池成交: {results['filled_in_dark']} "
          f"({results['filled_in_dark']/results['total_orders']*100:.1f}%)")
    print(f"  公开成交: {results['filled_in_lit']} "
          f"({results['filled_in_lit']/results['total_orders']*100:.1f}%)")
    print(f"  未成交: {results['unfilled']}")
    print(f"  平均价格改善: {results['avg_price_improvement_bp']:.2f} bp")
    print(f"  平均等待时间: {results['avg_wait_time_seconds']:.2f} 秒")

    return results
