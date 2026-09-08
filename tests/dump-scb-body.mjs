import fs from 'node:fs'
const html = fs.readFileSync('portable/dist/guide/m01-overview/1.3-quant-mindset.html', 'utf8')
// 找所有的 scb-out-body 内部内容
const re = /<div class="scb-out-body"[^>]*>([\s\S]*?)<\/div><\/details>/g
let m, i = 0
while ((m = re.exec(html)) !== null) {
  const body = m[1]
  console.log(`--- scb-out-body #${i} (${body.length} chars) ---`)
  // 找关键标记
  const hasText = body.includes('scb-out-text')
  const hasEmpty = body.includes('scb-out-empty')
  const hasSvgs = body.includes('scb-out-svgs')
  const hasError = body.includes('scb-out-error')
  console.log(`  has-text=${hasText} has-empty=${hasEmpty} has-svgs=${hasSvgs} has-error=${hasError}`)
  if (hasText) {
    const tm = body.match(/<pre class="scb-out-text"[^>]*>([\s\S]*?)<\/pre>/)
    if (tm) console.log('  text:', tm[1].slice(0, 100))
  }
  i++
}
console.log(`total: ${i}`)