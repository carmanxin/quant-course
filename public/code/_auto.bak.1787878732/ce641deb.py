# @quantlab/output: ce641deb
def param_stability_analysis(chosen_params: List[Tuple[int, int]]) -> Dict[str, float]:
    """分析每轮最优参数的稳定性"""
    fast_values = [p[0] for p in chosen_params]
    slow_values = [p[1] for p in chosen_params]

    def coefficient_of_variation(arr):
        mean = np.mean(arr)
        std = np.std(arr)
        return std / mean if mean > 0 else 0

    def stability_score(cv):
        return max(0, 1 - cv)  # CV 越低,稳定性越高

    stability = {
        'fast_mean': np.mean(fast_values),
        'fast_std': np.std(fast_values),
        'fast_cv': coefficient_of_variation(fast_values),
        'fast_stability': stability_score(coefficient_of_variation(fast_values)),
        'slow_mean': np.mean(slow_values),
        'slow_std': np.std(slow_values),
        'slow_cv': coefficient_of_variation(slow_values),
        'slow_stability': stability_score(coefficient_of_variation(slow_values)),
        'n_windows': len(chosen_params),
    }

    print("\n" + "=" * 60)
    print("参数稳定性分析")
    print("=" * 60)
    print(f"分析窗口数: {stability['n_windows']}")
    print(f"\nFast 参数:")
    print(f"  均值={stability['fast_mean']:.2f}, 标准差={stability['fast_std']:.2f}, CV={stability['fast_cv']:.2%}")
    print(f"  稳定性得分: {stability['fast_stability']:.2%}")
    print(f"\nSlow 参数:")
    print(f"  均值={stability['slow_mean']:.2f}, 标准差={stability['slow_std']:.2f}, CV={stability['slow_cv']:.2%}")
    print(f"  稳定性得分: {stability['slow_stability']:.2%}")

    if stability['fast_stability'] < 0.5 or stability['slow_stability'] < 0.5:
        print("\n⚠️ 警告:参数稳定性不足,策略可能在样本外失效。")
        print("  建议:增大训练窗口、减少可调参数、使用参数高原分析。")
    else:
        print("\n✓ 参数稳定性良好,策略可能有真实 alpha。")

    return stability


# 假设你已有 chosen_params
stability = param_stability_analysis(result['chosen_params'])
