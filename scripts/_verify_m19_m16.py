# -*- coding: utf-8 -*-
# 验收 m19/m16 demo 注入效果
import os, json, re, collections

def fnv1a(s):
    h = 0x811c9dc5
    for ch in s:
        h ^= ord(ch); h = (h * 0x01000193) & 0xFFFFFFFF
    return format(h, '08x')

def norm(raw):
    raw = re.sub(r'^#\s*@quantlab/output:\s*[\w.\-]+\s*\n?', '', raw)
    raw = raw.replace('\r\n', '\n')
    raw = re.sub(r'[ \t]+$', '', raw, flags=re.M)
    return raw.strip()

for mod in ['m19-a-share', 'm16-risk-management']:
    print('#' * 25, mod)
    cats = collections.Counter()
    per_file = collections.defaultdict(lambda: [0, 0])
    for fn in sorted(os.listdir('guide/' + mod)):
        if not fn.endswith('.md') or fn == 'index.md':
            continue
        lines = open('guide/' + mod + '/' + fn, encoding='utf-8').read().split('\n')
        inF = False; lang = ''; buf = []
        for line in lines:
            if not inF and line.startswith('```'):
                inF = True; lang = line[3:].strip(); buf = []
            elif inF and re.match(r'^```\s*$', line):
                inF = False
                if lang not in ('python', 'py'):
                    continue
                n = norm('\n'.join(buf))
                if not n:
                    continue
                h = fnv1a(n)
                op = 'public/code/' + h + '.output.json'
                d = json.load(open(op, encoding='utf-8')) if os.path.exists(op) else {}
                real = bool((d.get('text') or d.get('svgs')) and not d.get('note'))
                cats['real' if real else 'note'] += 1
                per_file[fn][0 if real else 1] += 1
                if not real:
                    sig = next((l.strip()[:45] for l in buf if l.strip().startswith(('def ', 'class '))), '?')
                    print('  note:', fn, '|', sig, '|', (d.get('note') or '')[:20])
            elif inF:
                buf.append(line)
    print('  汇总:', dict(cats))
    for fn, (r, n_) in sorted(per_file.items()):
        print(f'   {fn}: real={r} note={n_}')
