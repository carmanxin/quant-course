# @quantlab/output: c695e2e4
import requests
import pandas as pd

# 使用 Etherscan API 获取链上数据
def fetch_eth_transactions(address, api_key):
    """
    从 Etherscan 获取指定地址的交易记录
    """
    url = "https://api.etherscan.io/api"
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': 0,
        'endblock': 99999999,
        'sort': 'asc',
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == '1':
        df = pd.DataFrame(data['result'])
        df['value_eth'] = df['value'].astype(float) / 1e18
        df['timeStamp'] = pd.to_datetime(df['timeStamp'].astype(int), unit='s')
        return df
    else:
        raise Exception(f"API Error: {data.get('message', 'Unknown error')}")

# 使用 Dune 进行 SQL 分析（示例查询）
dune_query_example = """
-- 每日活跃地址数
SELECT
    date_trunc('day', block_time) AS day,
    COUNT(DISTINCT "from") AS active_senders,
    COUNT(DISTINCT "to") AS active_receivers
FROM ethereum.transactions
WHERE block_time > NOW() - INTERVAL '30' DAY
GROUP BY 1
ORDER BY 1 DESC
"""
