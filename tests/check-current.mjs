import fs from 'node:fs'
const html = fs.readFileSync('portable/dist/guide/m01-overview/1.3-quant-mindset.html', 'utf8')
const re = /<div class="scb-out-body"[^>]*>([\s\S]*?)<\/div><\/details>/g
let m, i = 0
while ((m = re.exec(html)) !== null) {
  const body = m[1]
  const hasText = body.includes('scb-out-text')
  const hasEmpty = body.includes('scb-out-empty')
  const hasNote = body.includes('scb-out-note')
  console.log(`#${i}: text=${hasText} empty=${hasEmpty} note=${hasNote}`)
  if (hasText) {
    const tm = body.match(/<pre class="scb-out-text"[^>]*>([\s\S]*?)<\/pre>/)
    if (tm) console.log(`  text: ${tm[1].slice(0, 100)}`)
  }
  if (hasNote) {
    const nm = body.match(/<div class="scb-out-note"[^>]*>([\s\S]*?)<\/div>/)
    if (nm) console.log(`  note: ${nm[1].slice(0, 100)}`)
  }
  i++
}