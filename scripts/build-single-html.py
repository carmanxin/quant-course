#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 VitePress 多页站点打包成 **单个可双击打开的 HTML 文件**（完全离线，无需任何服务器）。

原理：
  1. VitePress build 后的每个 HTML 页面已包含 SSR 渲染好的正文（含代码高亮、
     <details class="scb-out"> 运行结果折叠块、<img> 图表引用）。
  2. 这里把每页正文塞进 <template id="pg-N">（不进渲染树、不加载图片），
     切换页面时才把 template.innerHTML 注入 <main>（懒渲染，27MB 也不卡）。
  3. CSS 与 SVG 全部内联，断网、无服务器、双击即用。

用法：
    python scripts/build-single-html.py
输出：
    QuantLab-离线单文件.html
"""
import os
import re
import sys
import json
import base64
import html as htmllib
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / '.vitepress' / 'dist'
OUT = ROOT / 'QuantLab-离线单文件.html'

# ============================================================
# 1. 收集页面
# ============================================================
def nat(name: str):
    """自然排序键：1.2 < 1.10。
    用 (类型标记, 数值, 文本) 三元组包装，避免 int 与 str 直接比较触发 TypeError。"""
    parts = []
    for t in re.split(r'(\d+)', name):
        parts.append((1, int(t), '') if t.isdigit() else (0, 0, t))
    return parts


def collect_pages():
    """返回 [(分组key, 相对路径, 绝对Path)]，按目录 + 文件名排序。"""
    guide = DIST / 'guide'
    pages = []
    for p in sorted(guide.rglob('*.html')):
        rel = p.relative_to(DIST).as_posix()
        key = p.parent.name          # m01-overview / m02-finance-math ...
        if p.parent == guide:
            key = 'zz-index'         # guide/index.html 排最后
        pages.append((key, rel, p))
    # 同组内按文件名自然排序（1.1 < 1.2 < 1.10）
    pages.sort(key=lambda x: (x[0], nat(x[2].stem)))
    return pages

# ============================================================
# 2. 提取正文 + 标题
# ============================================================
def extract_body(raw: str):
    """取 vp-doc 容器到 </main> 之间的正文 HTML。"""
    m = re.search(r'<div[^>]*class="[^"]*\bvp-doc\b[^"]*"[^>]*>', raw)
    if not m:
        return None
    start = m.start()
    end = raw.find('</main>', start)
    if end == -1:
        end = len(raw)
    body = raw[start:end]
    # 去掉尾部多余的闭合 div（VPDoc / content-container 等）
    # 统计 body 内 div 开闭差，补平
    opens = len(re.findall(r'<div\b', body))
    closes = len(re.findall(r'</div>', body))
    if opens < closes:
        # 多出的闭合标签在尾部，逐个削掉直到平衡
        excess = closes - opens
        for _ in range(excess):
            idx = body.rfind('</div>')
            if idx == -1:
                break
            body = body[:idx] + body[idx + 6:]
    return body.strip()


def extract_title(raw: str, fallback: str):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', raw, re.S)
    if m:
        t = re.sub(r'<[^>]+>', '', m.group(1))
        # 去掉 VitePress 锚点注入的零宽空格（U+200B），否则会残留在侧边栏标题里
        t = htmllib.unescape(t).replace('\u200b', '').strip()
        if t:
            return t
    m = re.search(r'<title>(.*?)</title>', raw, re.S)
    if m:
        return htmllib.unescape(m.group(1)).strip()
    return fallback

# ============================================================
# 3. 内联 SVG 图片
# ============================================================
def inline_svgs(body: str, page_path: Path):
    """把 <img src="...svg"> 换成 data URI（相对路径基于该页面所在目录）。"""
    cache = {}
    page_dir = page_path.parent

    def repl(m):
        src = m.group(1)
        if src.startswith('data:'):
            return m.group(0)
        # 解析成真实文件路径
        if src.startswith('/'):
            fp = DIST / src.lstrip('/')
        else:
            fp = (page_dir / src).resolve()
        key = str(fp)
        if key in cache:
            data = cache[key]
        else:
            try:
                raw = fp.read_bytes()
                data = 'data:image/svg+xml;base64,' + base64.b64encode(raw).decode('ascii')
            except Exception:
                data = src  # 读不到就保持原样
            cache[key] = data
        return m.group(0).replace(src, data)

    return re.sub(r'<img[^>]+src="([^"]+\.svg)"[^>]*>', repl, body)

# ============================================================
# 4. CSS
# ============================================================
def collect_css():
    out = []
    # 主样式
    for p in sorted((DIST / 'assets').glob('style*.css')):
        out.append(p.read_text(encoding='utf-8', errors='replace'))
    # 图标
    icons = DIST / 'vp-icons.css'
    if icons.exists():
        out.append(icons.read_text(encoding='utf-8', errors='replace'))
    return '\n'.join(out)

# ============================================================
# 5. 生成
# ============================================================
EXTRA_CSS = """
/* ===== 离线单文件版自定义样式 ===== */
:root { --vp-c-bg: #ffffff; }
* { box-sizing: border-box; }
html, body { margin:0; padding:0; height:100%; font-family: -apple-system, BlinkMacSystemFont,
  "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; }
body { display:flex; overflow:hidden; }

/* 侧边栏 */
#sidebar {
  width: 300px; flex: 0 0 300px; height:100vh; overflow-y:auto;
  border-right:1px solid var(--vp-c-divider, #e2e2e3);
  background: var(--vp-c-bg-soft, #f9f9f9); padding: 12px 0 60px;
}
#sidebar h1.brand { font-size:15px; padding: 8px 20px 14px; margin:0; font-weight:700; }
#sidebar .grp { margin: 2px 0; }
#sidebar .grp > .gtitle {
  font-size:12.5px; font-weight:700; color:#5f6368; padding:7px 20px;
  cursor:pointer; user-select:none; display:flex; align-items:center;
}
#sidebar .grp > .gtitle .dot { width:6px;height:6px;border-radius:50%;
  background:#ff0080; margin-right:8px; flex:0 0 6px; }
#sidebar .grp > .gtitle:hover { color:#ff0080; }
#sidebar .grp ul { list-style:none; margin:0 0 6px; padding:0; }
#sidebar .grp li a {
  display:block; padding:5px 20px 5px 34px; font-size:13px; color:#3c4043;
  text-decoration:none; line-height:1.5;
}
#sidebar .grp li a:hover { color:#ff0080; }
#sidebar .grp li a.active {
  color:#ff0080; font-weight:600; background:rgba(255,0,128,.07);
  box-shadow: inset 2px 0 0 #ff0080;
}
#sidebar.collapsed { display:none; }

/* 主区 */
#wrap { flex:1; display:flex; flex-direction:column; height:100vh; min-width:0; }
#topbar {
  height:44px; flex:0 0 44px; display:flex; align-items:center; gap:10px;
  padding:0 16px; border-bottom:1px solid var(--vp-c-divider,#e2e2e3);
  background:var(--vp-c-bg,#fff); font-size:13px;
}
#toggle { cursor:pointer; border:1px solid #d0d0d1; background:#fff; border-radius:6px;
  padding:3px 10px; font-size:12px; }
#toggle:hover { border-color:#ff0080; color:#ff0080; }
#crumb { color:#5f6368; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
#main { flex:1; overflow-y:auto; padding: 0; }
.content-wrap {
  max-width: 860px; margin: 0 auto;
  padding: 36px 56px 140px;
  font-size: 15px; line-height: 1.7; color: #2c3e50;
}
/* 与线上版一致：h1 用主题绿色、大字 */
.content-wrap h1 {
  font-size: 34px; font-weight: 700; margin: 8px 0 28px;
  color: #00b96b; letter-spacing: -0.5px;
  border: none; padding: 0;
}
.content-wrap h1::before { display: none; }  /* 关掉 vp-doc h1 左侧的绿色色块 */
.content-wrap h2 { font-size: 24px; font-weight: 700; margin: 36px 0 16px; color:#1f2328; }
.content-wrap h3 { font-size: 19px; font-weight: 600; margin: 28px 0 12px; color:#1f2328; }
.content-wrap h4 { font-size: 16px; font-weight: 600; margin: 22px 0 10px; color:#1f2328; }
.content-wrap p { margin: 0 0 14px; }
.content-wrap ul, .content-wrap ol { margin: 0 0 16px; padding-left: 26px; }
.content-wrap li { margin: 4px 0; }
.content-wrap blockquote {
  margin: 14px 0; padding: 10px 16px;
  border-left: 3px solid var(--vp-c-brand-1, #00b96b);
  background: #f6f8fa; color:#57606a; border-radius: 0 4px 4px 0;
}
.content-wrap hr { margin: 32px 0; border: none; border-top: 1px solid #e2e2e3; }
.content-wrap table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }
.content-wrap th, .content-wrap td { padding: 8px 14px; border: 1px solid #e2e2e3; text-align: left; }
.content-wrap th { background: #f6f8fa; font-weight: 600; }
.content-wrap strong { color: #1f2328; }
.content-wrap a { color: var(--vp-c-brand-1, #00b96b); text-decoration: none; }
.content-wrap a:hover { text-decoration: underline; }
.content-wrap img { max-width: 100%; height: auto; }

/* 代码块 / 运行结果：复用 VitePress 的 shiki + scb-out 样式 */
.content-wrap pre { overflow-x:auto; }
details.scb-out { margin: 12px 0; border:1px solid var(--vp-c-divider,#e2e2e3);
  border-radius:8px; padding:0; background:var(--vp-c-bg-soft,#f9f9f9); }
details.scb-out > summary { cursor:pointer; padding:8px 14px; font-size:13px;
  font-weight:600; list-style:none; }
details.scb-out > summary::-webkit-details-marker { display:none; }
details.scb-out[open] > summary { border-bottom:1px solid var(--vp-c-divider,#e2e2e3); }
.scb-out-body { padding: 12px 14px; }
pre.scb-out-text { margin:0 0 10px; font-size:12.5px; white-space:pre-wrap;
  word-break:break-word; }
.scb-out-svgs img { max-width:100%; height:auto; display:block; margin:8px 0; }

/* 自定义容器：tip / warning / info / danger */
.custom-block {
  margin: 14px 0; padding: 12px 16px 12px 40px;
  border-left: 4px solid; border-radius: 4px;
  position: relative; font-size: 14px; line-height: 1.6;
}
.custom-block p { margin: 4px 0; }
.custom-block-title { font-weight: 700; margin: 0 0 6px; }
.custom-block.tip { background: #f3f5fc; border-color: #3451b2; color: #1f2937; }
.custom-block.info { background: #eef5fc; border-color: #3451b2; color: #1f2937; }
.custom-block.warning { background: #fff8e6; border-color: #d97706; color: #1f2937; }
.custom-block.danger { background: #ffebe9; border-color: #d73a49; color: #1f2937; }
.custom-block.tip .custom-block-title::before { content: "💡"; margin-right: 6px; }
.custom-block.info .custom-block-title::before { content: "ℹ️"; margin-right: 6px; }
.custom-block.warning .custom-block-title::before { content: "⚠️"; margin-right: 6px; }
.custom-block.danger .custom-block-title::before { content: "🚫"; margin-right: 6px; }
.custom-block-title { padding-left: 0; }
.custom-block:not(.tip):not(.info):not(.warning):not(.danger) .custom-block-title::before { content: "📌"; margin-right: 6px; }

/* 页内锚点跳转补偿 */
[id] { scroll-margin-top: 60px; }

@media (max-width: 860px) {
  #sidebar { position:fixed; z-index:50; box-shadow:0 0 24px rgba(0,0,0,.18); }
  .content-wrap { padding: 20px 16px 100px; font-size: 14.5px; }
  .content-wrap h1 { font-size: 26px; }
}
"""

JS = """
(function () {
  var PAGES = window.__PAGES__;
  var byId = {};
  PAGES.forEach(function (p, i) { p.idx = i; byId[p.id] = p; });

  var sidebar = document.getElementById('sidebar');
  var crumb   = document.getElementById('crumb');
  var main    = document.getElementById('main');
  var groups  = {};

  // ---- 构建侧边栏 ----
  PAGES.forEach(function (p) {
    if (!groups[p.group]) groups[p.group] = { title: p.groupTitle, items: [] };
    groups[p.group].items.push(p);
  });

  var frag = document.createDocumentFragment();
  Object.keys(groups).forEach(function (g) {
    var grp = groups[g];
    var wrap = document.createElement('div');
    wrap.className = 'grp';
    var t = document.createElement('div');
    t.className = 'gtitle';
    t.innerHTML = '<span class="dot"></span>';
    t.appendChild(document.createTextNode(grp.title));
    var ul = document.createElement('ul');
    grp.items.forEach(function (p) {
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = '#' + p.id;
      a.textContent = p.title;
      a.dataset.id = p.id;
      li.appendChild(a);
      ul.appendChild(li);
    });
    (function (ul) {
      t.addEventListener('click', function () {
        ul.style.display = (ul.style.display === 'none') ? '' : 'none';
      });
    })(ul);
    wrap.appendChild(t);
    wrap.appendChild(ul);
    frag.appendChild(wrap);
  });
  sidebar.appendChild(frag);

  function markActive(id) {
    var as = sidebar.querySelectorAll('a');
    for (var i = 0; i < as.length; i++) {
      as[i].classList.toggle('active', as[i].dataset.id === id);
    }
  }

  // ---- 懒渲染：切页时才把 template 内容注入 DOM ----
  // 用 .content-wrap 包裹，自己控制 max-width / padding，
  // 不依赖 VitePress 的 .VPDoc 链式 CSS（它假设的父容器结构跟我自定义布局冲突）。
  function render(id) {
    var p = byId[id] || PAGES[0];
    var tpl = document.getElementById('pg-' + p.idx);
    var body = tpl ? tpl.innerHTML : '<p>（内容缺失）</p>';
    main.innerHTML = '<div class="content-wrap">' + body + '</div>';
    crumb.textContent = p.groupTitle + '  ›  ' + p.title;
    document.title = p.title + ' — QuantLab';
    markActive(p.id);
    main.scrollTop = 0;
    window.scrollTo(0, 0);
  }

  function onHash() {
    var id = decodeURIComponent(location.hash.replace(/^#/, ''));
    if (!id || !byId[id]) id = PAGES[0].id;
    render(id);
  }
  window.addEventListener('hashchange', onHash);
  onHash();

  document.getElementById('toggle').addEventListener('click', function () {
    sidebar.classList.toggle('collapsed');
  });

  // 侧边栏链接点击后收起（移动端）
  sidebar.addEventListener('click', function (e) {
    if (e.target.tagName === 'A' && window.innerWidth <= 860) {
      sidebar.classList.add('collapsed');
    }
  });
})();
"""


def main():
    if not DIST.exists():
        print('[ERR] 找不到 .vitepress/dist，请先运行 npx vitepress build')
        return 1

    pages = collect_pages()
    print(f'[1/5] 收集页面: {len(pages)} 个')

    # 模块标题：从 sidebar 找 has-active 的 section 的 h2（即"当前页所在的章节"）。
    # 用每个 key 的第一页（保证只设一次），has-active 标记只有当前模块有，能精确定位。
    group_titles = {}
    for key, rel, p in pages:
        if key in group_titles:
            continue
        try:
            raw = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            raw = ''
        # 找 has-active 的 VPSidebarItem section 里的 h2
        m = re.search(r'VPSidebarItem[^>]*\bhas-active\b.*?<h2[^>]*class="[^"]*\btext\b[^"]*"[^>]*>(.*?)</h2>',
                      raw, re.S)
        if m:
            t = htmllib.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
            if t:
                group_titles[key] = t
                continue
        # fallback：用目录名映射（VitePress sidebar 无 has-active 时的兜底）
        fallback = {
            'm01-overview': '模块一：量化交易全景与行业认知',
            'm02-finance-math': '模块二：金融基础与数理工具',
            'm03-python-data': '模块三：Python 量化编程与数据工程',
            'm04-backtest': '模块四：回测框架与绩效评估',
            'm05-strategies': '模块五：策略开发工作流',
            'm06-factor': '模块六：因子模型',
            'm07-portfolio': '模块七：组合优化',
            'm08-alt-data': '模块八：另类数据',
            'm09-risk': '模块九：风控与合规',
            'm10-frontier': '模块十：量化前沿',
            'm11-derivatives': '模块十一：衍生品定价与对冲',
            'm12-crypto': '模块十二：加密货币与链上数据',
            'm13-fx-futures': '模块十三：外汇与期货',
            'm14-microstructure-deep': '模块十四：微观结构深入',
            'm15-macro': '模块十五：宏观因子',
            'agents': '工具与 Agent',
            'zz-index': '指南目录',
        }
        group_titles[key] = fallback.get(key, key)

    metas, templates = [], []
    total = 0
    for i, (key, rel, p) in enumerate(pages):
        raw = p.read_text(encoding='utf-8', errors='replace')
        body = extract_body(raw)
        if not body:
            print(f'  [WARN] 无正文，跳过: {rel}')
            continue
        body = inline_svgs(body, p)
        title = extract_title(raw, p.stem)
        pid = rel[:-5]  # 去掉 .html，作为 hash id
        metas.append({
            'id': pid, 'title': title,
            'group': key, 'groupTitle': group_titles.get(key, key),
        })
        # 保护：正文里若意外含 </template 会截断，做转义还原
        safe = body.replace('</template', '</tem&#112;late')
        templates.append(f'<template id="pg-{i}">{safe}</template>')
        total += len(body)

    print(f'[2/5] 正文提取完成，合计 {total/1048576:.1f} MB')

    css = collect_css()
    print(f'[3/5] CSS 内联 {len(css)/1024:.0f} KB')

    # index 页排到最后
    order = sorted(range(len(metas)),
                   key=lambda i: (metas[i]['group'] == 'zz-index',
                                  metas[i]['group'],
                                  nat(metas[i]['title'])))
    metas = [metas[i] for i in order]
    templates = [templates[i] for i in order]
    # 关键：重排后必须把 <template id="pg-N"> 重新编号，
    # 否则 N 还是提取时的旧下标，与 PAGES 数组下标错位 → 点 A 章渲染出 B 章内容。
    templates = [
        re.sub(r'^<template id="pg-\d+">', f'<template id="pg-{i}">', t, count=1)
        for i, t in enumerate(templates)
    ]
    for i, m in enumerate(metas):
        m['idx'] = i

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QuantLab 离线版</title>
<style>{css}</style>
<style>{EXTRA_CSS}</style>
</head>
<body>
<aside id="sidebar"><h1 class="brand">QuantLab 量化交易课程</h1></aside>
<div id="wrap">
  <div id="topbar">
    <button id="toggle">☰ 目录</button>
    <span id="crumb"></span>
  </div>
  <main id="main"></main>
</div>
{templates_str(templates)}
<script>window.__PAGES__ = {json.dumps(metas, ensure_ascii=False)};</script>
<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding='utf-8')
    size = OUT.stat().st_size / 1048576
    print(f'[4/5] 已写入 {OUT.name}  {size:.1f} MB')
    print(f'[5/5] 完成：{len(metas)} 页，双击即可打开（完全离线）')
    return 0


def templates_str(tpls):
    return '\n'.join(tpls)


if __name__ == '__main__':
    sys.exit(main())
