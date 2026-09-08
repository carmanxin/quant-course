// 验证 describeFragment 提取逻辑
const fs = require('fs');
const list = JSON.parse(fs.readFileSync('.workbuddy/frag-list.json', 'utf8'));

function extractDoc(lines, i) {
  for (let j = i + 1; j < Math.min(i + 4, lines.length); j++) {
    const t = lines[j].trim();
    if (t === '') continue;
    if (t.startsWith('"""') || t.startsWith("'''")) {
      let content = t.slice(3);
      let k = j;
      // 若未在本行闭合，继续拼接
      while (!/("""|''')$/.test(content) && k < Math.min(i + 6, lines.length - 1)) {
        k++;
        content += ' ' + lines[k].trim();
        if (/("""|''')$/.test(content)) break;
      }
      content = content.replace(/^(["']{3})\s*/, '').replace(/\s*(["']{3})$/, '').trim();
      // 过滤参数/返回文档标记
      const firstLine = content.split('\n')[0].trim().split('。')[0];
      if (/^(Parameters|Args|Returns|Note|Examples|属性|参数|返回|示例|注意|:param|:type|:return)/i.test(firstLine)) return '';
      return firstLine || '';
    }
    if (t.startsWith('#')) return t.replace(/^#+\s*/, '').trim();
    if (!/^[ \t]/.test(lines[j])) break;
    break;
  }
  return '';
}

function describeFragment(code) {
  const lines = code.split('\n');
  const items = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^\s*(?:def|class)\s+([A-Za-z_]\w*)/);
    if (m) {
      const kind = lines[i].trim().startsWith('class') ? '类' : '函数';
      const desc = extractDoc(lines, i);
      items.push({ name: m[1], kind, desc });
    }
  }
  if (!items.length) return '';
  const described = items.filter((x) => x.desc).map((x) => `\`${x.name}\`（${x.desc}）`);
  const undescribed = items.filter((x) => !x.desc).map((x) => `\`${x.name}\``);
  let explain = `本段代码定义了${items.length}个${items.length > 1 ? '函数/类' : '函数/类'}：`;
  if (described.length) explain += described.join('、');
  if (undescribed.length) {
    if (described.length) explain += '，以及 ' + undescribed.join('、');
    else explain += undescribed.join('、');
  }
  explain += '。这些定义属于教学展示（未提供独立运行所需的输入数据），可结合上下文章节或实战练习实际调用。';
  return explain;
}

let withDesc = 0;
for (const name of list.slice(0, 40)) {
  const code = fs.readFileSync('public/code/_auto/' + name + '.py', 'utf8')
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '');
  const explain = describeFragment(code);
  console.log(name + ':', explain);
  if (explain.includes('（') && !explain.includes('函数/类：`xxx`')) withDesc++;
}
console.log('\n--- 有 docstring 描述的 (前40个中):', withDesc);