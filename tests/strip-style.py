import re, pathlib
p = pathlib.Path('index.md')
content = p.read_text(encoding='utf-8')
# 删除 <style scoped>...</style>
new = re.sub(r'<style\s+scoped>[\s\S]*?</style>', '', content)
p.write_text(new, encoding='utf-8')
print(f'old size: {len(content)}, new size: {len(new)}')