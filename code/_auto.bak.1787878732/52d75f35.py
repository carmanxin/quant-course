# @quantlab/output: 52d75f35
def test_limit_order_execution():
    """验证限价单:只在价格达到限价时才成交"""
    engine_singleton = ExecutionHandler(
        commission_rate=0.0003, stamp_duty=0.001, slippage_pct=0
    )

    # 构造一笔限价买单:限价 50 元
    limit_order = Event(
        timestamp=datetime(2024, 1, 15, 10, 0),
        event_type=EventType.ORDER,
        priority=3,
        data={
            'symbol': 'STOCK_A',
            'qty': 100,
            'order_type': OrderType.LIMIT,
            'direction': 'BUY',
            'limit_price': 50.0,
        }
    )

    # 场景 1:市价 49 元(低于限价) → 应该成交
    market_1 = Event(
        timestamp=datetime(2024, 1, 15, 10, 1),
        event_type=EventType.MARKET,
        priority=1,
        data={'symbol': 'STOCK_A', 'close': 49.0, 'high': 50, 'low': 48, 'volume': 1000}
    )
    fill_1 = engine_singleton.execute_order(limit_order, market_1)
    assert fill_1 is not None, "市价 49 < 限价 50 应该成交"
    print(f"场景1 ✓:市价 49,限价 50 的买单成交 @ {fill_1.data['fill_price']}")

    # 场景 2:市价 51 元(高于限价) → 应该不成交
    market_2 = Event(
        timestamp=datetime(2024, 1, 15, 10, 2),
        event_type=EventType.MARKET,
        priority=1,
        data={'symbol': 'STOCK_A', 'close': 51.0, 'high': 52, 'low': 50, 'volume': 1000}
    )
    fill_2 = engine_singleton.execute_order(limit_order, market_2)
    assert fill_2 is None, "市价 51 > 限价 50 应该不成交"
    print(f"场景2 ✓:市价 51,限价 50 的买单不成交(挂单继续等待)")

    # 场景 3:市价回到 50 元 → 应该成交
    market_3 = Event(
        timestamp=datetime(2024, 1, 15, 10, 3),
        event_type=EventType.MARKET,
        priority=1,
        data={'symbol': 'STOCK_A', 'close': 50.0, 'high': 50.5, 'low': 49.5, 'volume': 1000}
    )
    fill_3 = engine_singleton.execute_order(limit_order, market_3)
    assert fill_3 is not None, "市价 50 == 限价 50 应该成交"
    print(f"场景3 ✓:市价 50,限价 50 的买单成交 @ {fill_3.data['fill_price']}")

    print("\n所有限价单撮合场景验证通过 ✓")

test_limit_order_execution()
