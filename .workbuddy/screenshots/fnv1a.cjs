function fnv1a(str) {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return (h >>> 0).toString(16).padStart(8, '0');
}
function normalizeCode(raw) {
  return raw
    .replace(/^#\s*@quantlab\/output:\s*[\w.\-]+\s*\n?/, '')
    .replace(/\r\n/g, '\n')
    .replace(/[ \t]+$/gm, '')
    .trim();
}
const fs = require('fs');
const files = fs.readdirSync('public/code/_auto').filter(f => f.endsWith('.py'));
const longFiles = files.filter(f => {
  const t = fs.readFileSync('public/code/_auto/' + f, 'utf8');
  return t.includes('CostSimulator');
});
longFiles.forEach(f => console.log(f, '->', fnv1a(normalizeCode(fs.readFileSync('public/code/_auto/' + f, 'utf8')))));