# @quantlab/output: f96ad58d
def run_unit_tests():
    """对引擎各模块做单元测试"""
    import sys

    tests = [
        ('test_portfolio_cash', test_portfolio_cash_flow),
        ('test_risk_drawdown', test_risk_drawdown_halt),
        ('test_execution_commission', test_execution_costs),
        ('test_strategy_no_signal', test_strategy_initial_period),
    ]

    passed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
        except Exception as e:
            print(f"  ⚠ {name}: {type(e).__name__}: {e}")

    print(f"\n{passed}/{len(tests)} 测试通过")
    return passed == len(tests)


def test_portfolio_cash_flow():
    """Portfolio 现金流转正确性"""
    pf = Portfolio(initial_capital=1_000_000)
    pf.current_prices['TEST'] = 100.0

    # 模拟买入 1000 股
    fill_buy = Event(
        timestamp=pd.Timestamp('2024-01-01'),
        event_type=EventType.FILL,
        priority=4,
        data={
            'symbol': 'TEST', 'qty': 1000,
            'fill_price': 100.0, 'direction': 'BUY',
            'commission': 30, 'slippage': 50,
        }
    )
    pf.update_fill(fill_buy)
    assert pf.cash == 1_000_000 - 100 * 1000 - 30, f"现金计算错误: {pf.cash}"
    assert pf.positions['TEST'] == 1000
    assert abs(pf.equity - 1_000_000) < 1  # 市值不变(刚买入)


def test_risk_drawdown_halt():
    """RiskManager 回撤熔断逻辑"""
    pf = Portfolio(initial_capital=1_000_000)
    rm = RiskManager(max_drawdown_pct=0.10)
    pf.current_prices['TEST'] = 100.0

    # 模拟峰值 100 万
    pf.cash = 1_000_000
    rm.peak_equity = 1_000_000

    # 让净值降到 89 万(回撤 11%)
    pf.cash = 890_000

    order = Event(
        timestamp=pd.Timestamp('2024-01-01'),
        event_type=EventType.ORDER,
        priority=3,
        data={'symbol': 'TEST', 'qty': 100, 'order_type': OrderType.MARKET, 'direction': 'BUY', 'limit_price': None}
    )
    allowed = rm.check_order(order, pf)
    assert not allowed, "回撤超过 10% 应该拒绝新订单"


def test_execution_costs():
    """撮合模块手续费计算正确"""
    eh = ExecutionHandler(commission_rate=0.0003, stamp_duty=0.001)

    order = Event(
        timestamp=pd.Timestamp('2024-01-01'),
        event_type=EventType.ORDER,
        priority=3,
        data={'symbol': 'TEST', 'qty': 1000, 'order_type': OrderType.MARKET, 'direction': 'SELL', 'limit_price': None}
    )
    market = Event(
        timestamp=pd.Timestamp('2024-01-01'),
        event_type=EventType.MARKET,
        priority=1,
        data={'symbol': 'TEST', 'close': 100.0, 'high': 100, 'low': 100, 'volume': 1000}
    )
    fill = eh.execute_order(order, market)
    assert fill is not None

    # 卖 1000 股 @ 100 元:印花税 = 100 元,佣金 = 30 元,总成本 130 元
    assert fill.data['commission'] >= 130, f"卖出成本计算错误: {fill.data['commission']}"


def test_strategy_initial_period():
    """策略初始期不产生信号"""
    s = Strategy(['TEST'], fast_window=10, slow_window=30)

    # 前 9 根 K 线不应产生信号
    signals_count = 0
    for i in range(9):
        mkt = Event(
            timestamp=pd.Timestamp('2024-01-01') + pd.Timedelta(days=i),
            event_type=EventType.MARKET,
            priority=1,
            data={'symbol': 'TEST', 'close': 100 + i, 'open': 100, 'high': 100, 'low': 100, 'volume': 1000}
        )
        signals_count += len(s.calculate_signals(mkt))

    assert signals_count == 0, "初始期不应产生信号"

run_unit_tests()
