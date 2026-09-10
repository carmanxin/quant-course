# @quantlab/output: f80cb409
from ibapi.client import EClient
class IBApp(EWrapper, EClient):
    def nextValidId(self, orderId):
        contract = Contract()
        contract.symbol = "AAPL"
        order = Order()
        order.action = "BUY"
        order.orderType = "MKT"
        order.totalQuantity = 100
        self.placeOrder(orderId, contract, order)
