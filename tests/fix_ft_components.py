"""
批量修复 m11 中使用的虚构 Vue 组件 (<ft-*>) 为项目支持的 CSS class HTML 元素。

转换规则:
- <ft-quiz>...</ft-quiz>         -> 删除(容器无意义)
- <ft-quiz-item :correct="...">A. TEXT</ft-quiz-item>  -> <div class="quiz-option">A. TEXT</div>
- <ft-marquee title="...">...</ft-marquee>             -> 删除
- <ft-marquee-item label="L" value="V" />              -> <span class="ft-marquee-item"><span class="sym">▸</span><span class="px">L: V</span></span>
- <ft-metric-group ...>...</ft-metric-group>           -> 删除(容器)
- <ft-metric label="L" :value="V" suffix="S" />        -> <span class="ft-metric"><span class="ft-metric-val">VS</span><br/><span class="ft-metric-label">L</span></span>
"""
import re
import os
from pathlib import Path

FILES = list(Path(r'D:/AI/study/quant/guide/m11-derivatives').glob('*.md'))


def fix_file(path: Path) -> dict:
    """处理单个 m11 markdown 文件,返回修改统计。"""
    src = path.read_text(encoding='utf-8')
    orig = src
    stats = {}

    # 1) 删除 <ft-quiz> ... </ft-quiz> 容器
    src, n = re.subn(r'<ft-quiz>\s*', '', src)
    src, _ = re.subn(r'\s*</ft-quiz>', '\n', src)
    stats['ft-quiz'] = n

    # 2) <ft-quiz-item :correct="bool">TEXT</ft-quiz-item> -> <div class="quiz-option">TEXT</div>
    def quiz_item_repl(m):
        text = m.group(1)
        # 文本内容已带 A. B. C. D. 前缀
        return f'<div class="quiz-option">\n{text}\n</div>'

    src, n = re.subn(
        r'<ft-quiz-item[^>]*>\s*([\s\S]*?)\s*</ft-quiz-item>',
        quiz_item_repl,
        src,
    )
    stats['ft-quiz-item'] = n

    # 3) 删除 <ft-marquee title="..."> 与 </ft-marquee>
    src, n = re.subn(r'<ft-marquee[^>]*>\s*', '', src)
    src, _ = re.subn(r'\s*</ft-marquee>', '\n', src)
    stats['ft-marquee'] = n

    # 4) <ft-marquee-item label="L" value="V" />  -> <span class="ft-marquee-item">
    def marquee_item_repl(m):
        label = m.group(1).strip()
        value = m.group(2).strip()
        return f'<span class="ft-marquee-item"><span class="sym">▸</span><span class="px">{label} · {value}</span></span>'
    src, n = re.subn(
        r'<ft-marquee-item\s+label="([^"]+)"\s+value="([^"]+)"\s*/>',
        marquee_item_repl,
        src,
    )
    stats['ft-marquee-item'] = n

    # 5) 删除 <ft-metric-group ...> 与 </ft-metric-group>
    src, n = re.subn(r'<ft-metric-group[^>]*>\s*', '', src)
    src, _ = re.subn(r'\s*</ft-metric-group>', '\n', src)
    stats['ft-metric-group'] = n

    # 6) <ft-metric label="L" :value="V" suffix="S" /> -> ft-metric span (复用 ft-marquee 风格)
    def metric_repl(m):
        label = m.group(1).strip()
        value = m.group(2).strip()
        suffix = m.group(3).strip() if m.group(3) else ''
        # 转义 value 中的特殊字符
        val_display = f'{value}{suffix}'
        return (
            f'<span class="ft-metric">'
            f'<span class="ft-metric-val">{val_display}</span>'
            f'<br/><span class="ft-metric-label">{label}</span>'
            f'</span>'
        )
    src, n = re.subn(
        r'<ft-metric\s+label="([^"]+)"\s+:value="([^"]+)"(?:\s+suffix="([^"]+)")?\s*/>',
        metric_repl,
        src,
    )
    stats['ft-metric'] = n

    # 7) 清理空行累积(连续 3 个以上空行变 2 个)
    src = re.sub(r'\n{4,}', '\n\n\n', src)

    if src != orig:
        path.write_text(src, encoding='utf-8')

    return stats


total = {}
for f in FILES:
    s = fix_file(f)
    total[f.name] = s

print('\n'.join(f'{k}: {v}' for k, v in total.items()))
print('\nDone.')
