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
const codes = Array.from(document.querySelectorAll('.scb-code code')).map(c => c.textContent);
const hashes = codes.map(normalizeCode).map(fnv1a);
JSON.stringify({ first50: codes[0].slice(0, 50), hashes });
