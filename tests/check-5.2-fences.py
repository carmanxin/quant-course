import sys, re, json
content = open('guide/m05-strategies/5.2-dual-ma.md', encoding='utf-8').read()
lines = content.split('\n')
in_fence = False
lang = ''
buf = []
fences = []
for line in lines:
    if not in_fence and line.startswith('```'):
        in_fence = True
        lang = line[3:].strip().split()[0] if len(line) > 3 else ''
        buf = []
    elif in_fence and line.strip() == '```':
        in_fence = False
        if lang in ('python', 'py'):
            fences.append('\n'.join(buf))
    elif in_fence:
        buf.append(line)
print(f'fences: {len(fences)}')

# 计算 hash
def fnv1a(s):
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xFFFFFFFF
    return '%08x' % h

def normalize(raw):
    t = re.sub(r'^#\s*@quantlab/output:\s*[\w.\-]+\s*\n?', '', raw)
    t = t.replace('\r\n', '\n')
    t = re.sub(r'[ \t]+$', '', t, flags=re.M)
    return t.strip()

idx = json.load(open('public/code/_index.json'))
for i, code in enumerate(fences):
    h = fnv1a(normalize(code))
    name = idx.get(h)
    print(f'  #{i} hash={h} → idx: {name or "<MISSING>"}')
    if name:
        out_file = f'public/code/{name}.output.json'
        import os
        if os.path.exists(out_file):
            o = json.load(open(out_file))
            print(f'    output: text="{o.get("text", "")[:60]}" svgs={len(o.get("svgs", []))} note={o.get("note", "")[:40]} error={o.get("error", "")[:60]}')
        else:
            print(f'    MISSING FILE: {out_file}')