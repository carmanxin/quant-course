# -*- coding: utf-8 -*-
"""把清洗后的案例2代码写回 10.1-rl.md（补 ```python 围栏）。"""
import io

P = 'guide/m10-frontier/10.1-rl.md'
CODE_START = 444    # 1-based: import numpy as np
FENCE_END = 838     # 1-based: 收尾 ```

lines = io.open(P, encoding='utf-8').read().split('\n')
assert lines[CODE_START - 1].strip() == 'import numpy as np', lines[CODE_START - 1]
assert lines[FENCE_END - 1].strip() == '```', repr(lines[FENCE_END - 1])

head = io.open('scripts/_case2_head.py', encoding='utf-8').read().rstrip('\n')
tail = io.open('scripts/_case2_tail.py', encoding='utf-8').read().rstrip('\n')
new_code = (head + '\n' + tail).split('\n')

new_lines = lines[:CODE_START - 1] + ['```python'] + new_code + lines[FENCE_END - 1:]
io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(new_lines))
print('done. 新围栏区间: %d .. %d 行, 代码 %d 行' % (CODE_START, CODE_START + len(new_code) + 1, len(new_code)))
