# @quantlab/output: 2236723f
from prometheus_client import Gauge
g = Gauge('pnl', 'Real-time PnL')
g.set(current_pnl)
