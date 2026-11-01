# @quantlab/output: ac32ccce
import importlib
import sys
from pathlib import Path
from typing import Type

class StrategyManager:
    """策略管理器 - 支持热加载/卸载策略"""

    def __init__(self, engine):
        self.engine = engine
        self.active_strategies: Dict[str, BaseStrategy] = {}
        self.strategy_configs: Dict[str, dict] = {}

    def load_strategy_from_file(self, filepath: str, class_name: str):
        """从Python文件动态加载策略"""
        filepath = Path(filepath)
        module_name = filepath.stem

        # 动态导入
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        strategy_class = getattr(module, class_name)
        self.logger.info(f"策略类 {class_name} 加载成功")
        return strategy_class

    def deploy_strategy(self, name: str, strategy_class: Type[BaseStrategy],
                        symbols: List[str], **kwargs):
        """部署策略到实盘"""
        if name in self.active_strategies:
            self.logger.warning(f"策略 {name} 已存在，先停止旧策略")
            self.stop_strategy(name)

        strategy = strategy_class(name=name, symbols=symbols, **kwargs)
        self.engine.register_strategy(strategy)
        self.active_strategies[name] = strategy
        self.logger.info(f"策略 {name} 部署成功")

    def stop_strategy(self, name: str):
        """停止并移除策略"""
        if name in self.active_strategies:
            # 发送平仓信号
            strategy = self.active_strategies[name]
            for symbol, pos in strategy.positions.items():
                if pos.quantity != 0:
                    self._close_position(symbol, pos)

            del self.active_strategies[name]
            self.logger.info(f"策略 {name} 已停止")

    def _close_position(self, symbol, position):
        """平仓某个持仓"""
        if position.quantity > 0:
            order = OrderRequest(symbol=symbol, side='SELL',
                                order_type='MKT', quantity=position.quantity)
        else:
            order = OrderRequest(symbol=symbol, side='BUY',
                                order_type='MKT', quantity=abs(position.quantity))
        # 发送平仓订单
        self.engine.order_producer and self.engine.order_producer.send('orders', order)

    def list_strategies(self):
        """列出所有活跃策略"""
        print("活跃策略列表:")
        print("-" * 50)
        for name, strategy in self.active_strategies.items():
            n_positions = sum(1 for p in strategy.positions.values() if p.quantity != 0)
            print(f"  {name}: 标的数={len(strategy.symbols)}, 持仓数={n_positions}")
