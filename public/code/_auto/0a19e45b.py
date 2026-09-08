# @quantlab/output: 0a19e45b
# 陷阱：默认参数只计算一次
def bad_append(item, lst=[]):
    lst.append(item)
    return lst

# 解决方案
def good_append(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
