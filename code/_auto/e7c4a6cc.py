# @quantlab/output: e7c4a6cc
def fast_pow(base: float, exp: int) -> float:
    """
    二分快速幂算法
    时间复杂度: O(log n)
    """
    result = 1.0
    current = base

    while exp > 0:
        if exp & 1:  # 当前位为1
            result *= current
        current *= current  # 底数平方
        exp >>= 1  # 右移一位

    return result


def matrix_pow(matrix: list, exp: int) -> list:
    """矩阵快速幂（用于马尔可夫链状态转移等场景）"""
    n = len(matrix)

    # 单位矩阵
    result = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    base = [row[:] for row in matrix]

    while exp > 0:
        if exp & 1:
            # result = result * base
            new_result = [[0.0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    new_result[i][j] = sum(result[i][k] * base[k][j] for k in range(n))
            result = new_result

        # base = base * base
        new_base = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                new_base[i][j] = sum(base[i][k] * base[k][j] for k in range(n))
        base = new_base

        exp >>= 1

    return result
