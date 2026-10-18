# -*- coding: utf-8 -*-
import os, re
for mod in ['m12-fixed-income', 'm13-crypto', 'm14-microstructure-deep',
            'm17-data-engineering', 'm18-strategy-lifecycle', 'm20-interview-prep']:
    print('#' * 22, mod)
    for root, dirs, files in os.walk('guide/' + mod):
        for fn in sorted(files):
            if not fn.endswith('.md') or fn == 'index.md':
                continue
            txt = open(os.path.join(root, fn), encoding='utf-8').read()
            h2 = re.findall(r'^##\s+(.+)$', txt, re.M)
            print(' ', fn)
            for h in h2:
                print('     -', h[:60])
