// 最终版 describeFragment
const fs = require('fs');
const list = JSON.parse(fs.readFileSync('.workbuddy/frag-list.json', 'utf8'));

function extractDoc(lines, i) {
  for (let j = i + 1; j < Math.min(i + 6, lines.length); j++) {
    const t = lines[j].trim();
    if (t === '') continue;
    if (t.startsWith('"""') || t.startsWith("'''")) {
      let content = t.slice(3);
      let k = j;
      while (!/(["']{3})$/.test(content) && k < Math.min(i + 10, lines.length - 1)) {
        k++;
        content += '\n' + lines[k].trim();
        if (/(["']{3})$/.test(lines[k].trim())) break;
      }
      content = content.replace(/^(["']{3})\s*/, '').replace(/\s*(["']{3})$/, '').trim();
      const firstLine = content.split('\n')[0].trim().split('。')[0];
      if (/^(Parameters|Args|Arguments|Returns|Return|Note|Examples|Notes|Attributes|属性|参数|返回|示例|注意|说明|:param|:type|:return|:raises)/i.test(firstLine)) return '';
      if (firstLine.length > 60) return firstLine.slice(0, 60) + '…';
      return firstLine;
    }
    if (t.startsWith('#')) {
      const c = t.replace(/^#+\s*/, '').trim();
      if (c.length > 60) return c.slice(0, 60) + '…';
      return c;
    }
    // def 续行/其他缩进行：跳过继续找 docstring/注释
  }
  return '';
}

function describeFragment(code) {
  const lines = code.split('\n');
  const items = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(?:def|class)\s+([A-Za-z_]\w*)/);
    if (m) {
      const kind = lines[i].startsWith('class') ? '类' : '函数';
      const desc = extractDoc(lines, i);
      items.push({ name: m[1], kind, desc });
    }
  }
  if (!items.length) return '';
  const described = items.filter((x) => x.desc).map((x) => `${x.kind} \`${x.name}\`（${x.desc}）`);
  const undescribed = items.filter((x) => !x.desc).map((x) => `${x.kind} \`${x.name}\``);
  let explain = `本段代码定义了 ${items.length} 个函数/类：`;
  if (described.length) explain += described.join('、');
  if (undescribed.length) {
    if (described.length) explain += '，以及 ' + undescribed.join('、');
    else explain += undescribed.join('、');
  }
  explain += '。该片段为教学展示（未包含独立运行的输入数据），可在实战练习中结合真实数据调用。';
  return explain;
}

let withDesc = 0;
for (const name of list) {
  const code = fs.readFileSync('public/code/_auto/' + name + '.py', 'utf8')
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '');
  const explain = describeFragment(code);
  if (explain.includes('（')) withDesc++;
}
console.log(`共 ${list.length} 个，有 docstring/注释描述: ${withDesc}`);
// 验证之前无描述的
for (const name of ['03af9dae', '0571e250', '03f70226', '0c67eac2', '102da2d7']) {
  const code = fs.readFileSync('public/code/_auto/' + name + '.py', 'utf8')
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '');
  console.log('\n' + name + ':', describeFragment(code));
}