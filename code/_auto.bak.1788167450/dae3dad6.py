# @quantlab/output: dae3dad6
cancel_rate = cancelled_orders / total_orders
if cancel_rate > threshold:
    alert("撤单率过高")
