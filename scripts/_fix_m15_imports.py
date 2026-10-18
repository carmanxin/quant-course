# -*- coding: utf-8 -*-
# m15 修复：demo fence 若使用 np/pd 但自身没 import，在 fence 顶部补 import
# 用法: python scripts/_fix_m15_imports.py
import io, re, os

def fnv1a(s):
    h = 0x811c9dc5
    for ch in s:
        h ^= ord(ch); h = (h * 0x01000193) & 0xFFFFFFFF
    return format(h, '08x')

fixed = 0
for mod in ['m15-macro']:
    for fn in sorted(os.listdir(f'guide/{mod}')):
        if not fn.endswith('.md') or fn == 'index.md':
            continue
        p = f'guide/{mod}/{fn}'
        lines = io.open(p, encoding='utf-8').read().split('\n')
        changed = False
        in_f = False; lang = ''; start = -1
        for i, line in enumerate(lines):
            if not in_f and line.startswith('```'):
                in_f = True; lang = line[3:].strip(); start = i
            elif in_f and re.match(r'^```\s*$', line):
                in_f = False
                if lang != 'python' and lang != 'py':
                    continue
                block = '\n'.join(lines[start + 1:i])
                if '合成数据最小示例' not in block:
                    continue
                body = lines[start + 1:i]
                has_np_import = any(re.match(r'^import numpy|^from numpy|^import pandas|^from pandas', l) for l in body)
                uses_np = re.search(r'\bnp\.', block) is not None
                uses_pd = re.search(r'\bpd\.', block) is not None
                adds = []
                if uses_np and not has_np_import:
                    adds.append('import numpy as np')
                if uses_pd and not any(re.match(r'^import pandas', l) for l in body):
                    adds.append('import pandas as pd')
                if adds:
                    lines[start + 1:start + 1] = adds + ['']
                    changed = True
                    fixed += 1
                    print('FIX', p, f'L{start + 1}', adds)
        if changed:
            io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print(f'修复 {fixed} 个 fence')
