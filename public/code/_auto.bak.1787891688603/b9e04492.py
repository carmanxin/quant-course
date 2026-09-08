# @quantlab/output: b9e04492
def block_bootstrap(returns, block_size=10, n_boot=1000):
    """
    分块Bootstrap：保留收益率的时序相关性
    标准的i.i.d. Bootstrap低估了真实方差，因为金融收益率存在自相关和波动率聚集
    """
    n = len(returns)
    n_blocks = int(np.ceil(n / block_size))
    boot_sharpes = []

    for _ in range(n_boot):
        # 随机选择起始块
        block_starts = np.random.choice(n - block_size + 1, size=n_blocks)
        boot_sample = []
        for start in block_starts:
            boot_sample.extend(returns[start:start + block_size])
        boot_sample = np.array(boot_sample[:n])  # 截取到原始长度

        boot_sharpe = boot_sample.mean() / boot_sample.std() * np.sqrt(252)
        boot_sharpes.append(boot_sharpe)

    return np.array(boot_sharpes)

# 对比标准Bootstrap和Block Bootstrap
standard_boot = np.array([
    np.random.choice(returns, size=len(returns), replace=True).mean() /
    np.random.choice(returns, size=len(returns), replace=True).std() * np.sqrt(252)
    for _ in range(1000)
])

block_boot = block_bootstrap(returns, block_size=10, n_boot=1000)

print(f"标准Bootstrap - 均值: {standard_boot.mean():.2f}, 标准差: {standard_boot.std():.2f}")
print(f"分块Bootstrap - 均值: {block_boot.mean():.2f}, 标准差: {block_boot.std():.2f}")
print(f"注意：如果收益率存在正自相关，分块Bootstrap的标准差通常更大，置信区间更宽")
