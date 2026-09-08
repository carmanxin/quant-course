import re, pathlib
p = pathlib.Path('index.md')
content = p.read_text(encoding='utf-8')
new = re.sub(r'<!--[\s\S]*?-->', '', content)
p.write_text(new, encoding='utf-8')
print(f'old size: {len(content)}, new size: {len(new)}')