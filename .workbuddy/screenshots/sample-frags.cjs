const fs = require('fs');
const list = JSON.parse(fs.readFileSync('.workbuddy/frag-list.json', 'utf8'));
for (const name of list.slice(0, 14)) {
  const code = fs.readFileSync('public/code/_auto/' + name + '.py', 'utf8')
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '');
  const lines = code.split('\n');
  const defs = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^\s*(?:def|class)\s+([A-Za-z_]\w*)/);
    if (m) {
      let desc = '';
      for (let j = i + 1; j < Math.min(i + 5, lines.length); j++) {
        const t = lines[j].trim();
        if (t.startsWith('"""') || t.startsWith("'''")) {
          desc = t.replace(/^(['"]{3})\s*/, '').replace(/\s*(['"]{3})$/, '').slice(0, 50);
          break;
        }
        if (t.startsWith('#')) { desc = t.replace(/^#+\s*/, '').slice(0, 50); break; }
        if (t === '') continue;
        if (!/^[ \t]/.test(lines[j])) break;
        break;
      }
      defs.push(m[1] + ' → ' + (desc || '(无描述)'));
    }
  }
  console.log(name, ':', defs.join(' | '));
}