# -*- coding: utf-8 -*-
"""修复 10.1-rl.md 案例2 缺失的 ```python 围栏、多余空行与破损 print。"""
import io, re, sys

P = 'guide/m10-frontier/10.1-rl.md'
src = io.open(P, encoding='utf-8').read()
lines = src.split('\n')

# 1-based 行号 -> 0-based 索引
HEAD = 441          # ### 📌 案例2：...
CODE_START = 444    # import numpy as np
FENCE_END = 838     # 收尾的 ```

assert lines[HEAD - 1].startswith('### 📌 案例2'), lines[HEAD - 1]
assert lines[CODE_START - 1].strip() == 'import numpy as np', lines[CODE_START - 1]
assert lines[FENCE_END - 1].strip() == '```', repr(lines[FENCE_END - 1])

code_raw = lines[CODE_START - 1:FENCE_END - 1]

# 去掉空行（原文每行之间都插了一个空行）
dedup = [l for l in code_raw if l.strip() != '']

# 修复破损的多行 print：把 print(f" 与其后的续行合并成一行普通字符串
merged = []
i = 0
while i < len(dedup):
    cur = dedup[i]
    if cur.rstrip().endswith('print(f"') or cur.rstrip() == 'print(f"':
        # 吞掉后续行直到遇到以 ") 结尾的行
        buf = [cur.rstrip()]
        i += 1
        while i < len(dedup) and not dedup[i].rstrip().endswith('")'):
            buf.append(dedup[i].strip())
            i += 1
        if i < len(dedup):
            buf.append(dedup[i].strip())
            i += 1
        body = ' '.join(buf)
        body = body.replace('print(f"', 'print("', 1)
        if body.endswith('")'):
            body = body[:-2] + '")'
        merged.append(body)
        continue
    merged.append(cur)
    i += 1
dedup = merged

out = []
for i, l in enumerate(dedup):
    if i > 0 and re.match(r'^(class |def |# =====|# ---)', l):
        out.append('')
    out.append(l)

text = '\n'.join(out)
# 兜底：任何残留的跨行 print 合并
text = re.sub(r'print\((f?")\n+\s*', r'print(\1', text)

io.open('scripts/_case2.py', 'w', encoding='utf-8').write(text + '\n')
print('extracted lines:', len(dedup))
print('---- head ----')
print('\n'.join(out[:6]))
print('---- tail ----')
print('\n'.join(out[-8:]))
