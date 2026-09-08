// Trace used analysis for a specific file using the CURRENT script logic
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
for (const line of codeBody.split(/\r?\n/)) {
  if (/^[ \t]/.test(line)) continue;
  if (/^(import\s|from\s|def\s|class\s|#|@|"""|\'\'\')/.test(line)) continue;
  const eqMatch = line.match(/^([^=]*?)=(?!=)/);
  if (eqMatch) {
    const lhsStripped = eqMatch[1].replace(/\b\w+(?=\s*\()/g, '').replace(/['"][^'"]*['"]/g, '""');
    for (const m of lhsStripped.matchAll(/\b([A-Za-z_]\w*)\b/g)) {
      const id = m[1];
      if (ignore.has(id)) continue;
      locallyDefined.add(id);
    }
  }
  let rhs = eqMatch ? line.slice(eqMatch[0].length) : line;
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