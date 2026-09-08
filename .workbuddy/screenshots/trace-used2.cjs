// Trace used analysis matching CURRENT script (class state machine)
const fs = require('fs');
const target = process.argv[2] || '0838d39e';
const codeBody = fs.readFileSync(`public/code/_auto/${target}.py`, 'utf8')
  .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '');

const declared = new Set();
for (const line of codeBody.split(/\r?\n/)) {
  let mm;
  if ((mm = line.match(/^def\s+(\w+)/))) declared.add(mm[1]);
  if ((mm = line.match(/^class\s+(\w+)/))) declared.add(mm[1]);
  if ((mm = line.match(/^import\s+(\w+)/))) declared.add(mm[1]);
  if ((mm = line.match(/^from\s+[\w.]+\s+import\s+([\w,\s]+)/))) {
    for (const tok of mm[1].split(',')) {
      const t = tok.trim().split(/\s+as\s+/).pop();
      if (t && /^[_A-Za-z][_A-Za-z0-9]*$/.test(t)) declared.add(t);
    }
  }
  if ((mm = line.match(/^def\s+\w+\s*\(([^)]*)\)/))) {
    for (const p of mm[1].split(',')) {
      const t = p.trim().replace(/[:\s=].*/, '').replace(/^\*+/, '');
      if (t && t !== 'self' && t !== 'cls' && /^[_A-Za-z][_A-Za-z0-9]*$/.test(t)) declared.add(t);
    }
  }
}
const ignore = new Set([
  'print','len','range','int','float','str','list','dict','set','tuple','bool',
  'True','False','None','self','cls','return','yield','pass','lambda',
  'np','pd','plt','sns','yf','nx','math','os','sys','json','csv','re','time',
  'datetime','timedelta','coint','adfuller','stats','scipy','numpy',
  'pandas','matplotlib','sklearn','torch','warnings',
  'and','or','not','in','is','for','while','if','elif','else','try','except',
  'finally','raise','with','from','import','def','class','return','global',
  'nonlocal','assert','del','break','continue','async','await',
]);
const used = new Set();
const locallyDefined = new Set();
let classIndent = -1;
for (const line of codeBody.split(/\r?\n/)) {
  const trimmed = line.trim();
  const indent = line.length - line.trimStart().length;
  if (trimmed === '') continue;
  if (/^class\s+/.test(trimmed)) { classIndent = indent; continue; }
  if (classIndent >= 0) {
    if (indent > classIndent) continue;
    classIndent = -1;
  }
  if (/^\s*(import\s|from\s|def\s|class\s|#|@|"""|\'\'\')/.test(trimmed)) continue;
  const forMatch = trimmed.match(/^for\s+([^:]+?)\s+in\s+/);
  if (forMatch) {
    for (const v of forMatch[1].split(',')) {
      const id = v.trim().split(/\s+/).pop();
      if (/^[A-Za-z_]\w*$/.test(id)) locallyDefined.add(id);
    }
  }
  const eqMatch = trimmed.match(/^([^=]*?)=(?!=)/);
  if (eqMatch) {
    const lhsStripped = eqMatch[1].replace(/\b\w+(?=\s*\()/g, '').replace(/['"][^'"]*['"]/g, '""');
    for (const m of lhsStripped.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
      const id = m[1];
      if (ignore.has(id)) continue;
      locallyDefined.add(id);
    }
  }
  let rhs = eqMatch ? trimmed.slice(eqMatch[0].length) : trimmed;
  rhs = rhs.replace(/"""[\s\S]*?"""/g, '""').replace(/'''[\s\S]*?'''/g, "''");
  rhs = rhs.replace(/"[^"]*"/g, '""').replace(/'[^']*'/g, "''");
  rhs = rhs.replace(/\b\w+(?=\s*\()/g, '');
  rhs = rhs.replace(/\b[A-Za-z_]\w*(?=\s*=)/g, '');
  for (const m of rhs.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
    const id = m[1];
    if (declared.has(id)) continue;
    if (locallyDefined.has(id)) continue;
    if (ignore.has(id)) continue;
    if (!used.has(id)) used.add(id);
  }
}
console.log('declared:', [...declared].sort().join(', '));
console.log('used:', [...used].sort().join(', ') || '(empty)');
console.log('locallyDefined:', [...locallyDefined].sort().join(', '));