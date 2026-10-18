# -*- coding: utf-8 -*-
# 扫描后半场各页缺哪些模板拍
import os, re

BEATS = ['概念详解', '数学原理', 'Python实战', '常见误区', '实战练习', '延伸阅读', '本章要点']
for mod in ['m11-derivatives', 'm12-fixed-income', 'm13-crypto', 'm14-microstructure-deep',
            'm17-data-engineering', 'm18-strategy-lifecycle', 'm20-interview-prep']:
    print('#' * 22, mod)
    for root, dirs, files in os.walk('guide/' + mod):
        for fn in sorted(files):
            if not fn.endswith('.md') or fn == 'index.md':
                continue
            txt = open(os.path.join(root, fn), encoding='utf-8').read()
            have = [b for b in BEATS if b in txt]
            missing = [b for b in BEATS if b not in txt]
            flag = '' if not missing else '  <== 缺: ' + ','.join(missing)
            print(f'  {fn}  有{len(have)}/7{flag}')
