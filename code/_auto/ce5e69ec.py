# @quantlab/output: ce5e69ec
from hmmlearn import hmm
import warnings

def hmm_cycle_detection(economic_data: np.ndarray,
                         n_states: int = 2,
                         n_iter: int = 1000) -> dict:
    """
    使用隐马尔可夫模型识别经济周期状态的切换。

    参数:
        economic_data: (T, D) 经济指标矩阵
        n_states: 隐状态数量（通常2=衰退/扩张，或4对应ML时钟）
        n_iter: EM算法迭代次数
    返回:
        包含 state_probabilities, states, model 的字典
    """
    # 数据标准化
    data_std = (economic_data - np.mean(economic_data, axis=0)) / \
               (np.std(economic_data, axis=0) + 1e-10)

    # 拟合高斯HMM
    model = hmm.GaussianHMM(
        n_components=n_states,
        covariance_type='full',
        n_iter=n_iter,
        random_state=42
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(data_std)

    # 预测最可能的隐状态序列
    hidden_states = model.predict(data_std)

    # 计算状态概率（平滑后验概率）
    state_probs = model.predict_proba(data_std)

    # 状态标签解读
    # 假设：高增长状态的均值更高
    state_means = model.means_
    growth_idx = np.argmax(state_means[:, 0])  # 增长维度均值最高的状态
    recession_idx = 0 if growth_idx == 1 else 1

    return {
        'states': hidden_states,
        'state_probabilities': state_probs,
        'model': model,
        'growth_state': growth_idx,
        'recession_state': recession_idx,
        'transition_matrix': model.transmat_,
        'current_state': hidden_states[-1],
        'recession_probability': state_probs[-1, recession_idx]
    }
