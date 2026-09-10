# @quantlab/output: be429258
class MEVBoostSimulator:
    """
    MEV-Boost 拍卖机制模拟
    展示构建者如何竞争区块构建权
    """

    def __init__(self, validators, builders):
        self.validators = validators
        self.builders = builders
        self.mempool = []  # 待处理交易池

    def simulate_block_auction(self, slot):
        """模拟一个 slot 中的区块构建拍卖"""
        # 每个构建者构建各自的区块
        builder_bids = []
        for builder in self.builders:
            block_value = builder.build_block(self.mempool)
            # 构建者出价（向提议者支付的金额）
            bid = block_value * 0.95  # 保留5%利润
            builder_bids.append({
                'builder': builder.name,
                'block_value': block_value,
                'bid': bid,
                'transactions': builder.included_txs
            })

        # 提议者选择最高出价
        builder_bids.sort(key=lambda x: x['bid'], reverse=True)
        winning_block = builder_bids[0]

        # 提议者收益 = 出价 + 共识层奖励
        proposer_reward = winning_block['bid']
        builder_profit = winning_block['block_value'] - winning_block['bid']

        return {
            'slot': slot,
            'proposer_reward': proposer_reward,
            'builder_profit': builder_profit,
            'winning_builder': winning_block['builder'],
            'total_mev_extracted': winning_block['block_value']
        }
