// tests/verify-static-code-blocks.js
// Playwright 验证 <StaticCodeBlock> 折叠块可用
// 两种模式:
//   默认:   http://127.0.0.1:5189 (需先起 dev/preview server)
//   FILE=1: 直接用 file:// 打开 .vitepress/dist 的构建产物 (无需服务器, 覆盖真实便携场景)
// 逻辑: 展开所有折叠块，至少一个能加载出运行结果（text / svg / error 任一）
import { chromium } from 'playwright'
import path from 'node:path'

const PAGES = [
  '/guide/m01-overview/1.3-quant-mindset.html',
  '/guide/m04-backtest/4.3-metrics.html',
  '/guide/m05-strategies/5.3-stat-arb.html',
  '/guide/m11-derivatives/11.1-greeks.html',
  '/guide/m20-interview-prep/20.1-math-stats.html',
]
const HTTP_BASE = process.env.BASE || 'http://127.0.0.1:5189'
const FILE_MODE = process.env.FILE === '1'

function toUrl(p) {
  if (FILE_MODE) {
    const fp = path.resolve('.vitepress/dist' + p)
    return `file:///${fp}`
  }
  return HTTP_BASE + p
}

async function check(page, path) {
  await page.goto(toUrl(path), { waitUntil: FILE_MODE ? 'load' : 'networkidle' })
  await page.waitForTimeout(1200)
  const details = page.locator('details.scb-out')
  const detailsCount = await details.count()
  if (detailsCount === 0) throw new Error(`${path}: no details.scb-out`)

  // 校验 summary 文案
  const summaryText = await details.first().locator('summary').textContent()
  if (!summaryText.includes('点击展开可浏览运行结果')) {
    throw new Error(`${path}: summary 文案不正确 (got "${summaryText}")`)
  }

  // 展开所有折叠块，等输出加载（file:// 下内联输出即时可见）
  await details.evaluateAll((els) => els.forEach((el) => (el.open = true)))
  await page.waitForTimeout(1500)

  // 至少一个块有运行结果
  const blocks = await details.evaluateAll((els) =>
    els.map((el) => {
      const text = el.querySelector('.scb-out-text')?.textContent?.trim() || ''
      const svgCount = el.querySelectorAll('.scb-out-svgs img').length
      const error = el.querySelector('.scb-out-error')?.textContent?.trim() || ''
      return { text, svgCount, error }
    }),
  )
  const withContent = blocks.filter((b) => b.text || b.svgCount > 0 || b.error)
  if (withContent.length === 0) {
    throw new Error(`${path}: 所有折叠块展开后都为空（无 text / svg / error）`)
  }

  const blockSummary = blocks
    .map((b) => `text=${b.text.length}B svg=${b.svgCount}${b.error ? ' err' : ''}`)
    .join(' | ')
  console.log(`  ✓ ${path}: details=${detailsCount}, contentBlocks=${withContent.length}/${blocks.length} [${blockSummary}]`)
}

async function main() {
  const browser = await chromium.launch()
  try {
    const page = await browser.newPage()
    for (const p of PAGES) await check(page, p)
    console.log(`[verify-static-code-blocks] ${FILE_MODE ? 'FILE://' : 'HTTP'} mode: all ${PAGES.length} pages OK`)
  } finally {
    await browser.close()
  }
}

main().catch((e) => {
  console.error(`[verify-static-code-blocks] FAIL: ${e.message}`)
  process.exit(1)
})
