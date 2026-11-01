# @quantlab/output: 50896206
# 陷阱：lambda 中的 i 是引用，循环结束后的值
funcs = [lambda x: x + i for i in range(10)]
# 所有 funcs 都用 i=9

# 解决方案
funcs = [lambda x, i=i: x + i for i in range(10)]
