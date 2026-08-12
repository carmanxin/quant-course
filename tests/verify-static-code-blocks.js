// tests/verify-static-code-blocks.js
// Playwright 验证 5 个典型页面的 <StaticCodeBlock> 折叠块可用
import { chromium } from 'playwright'

const PAGES = [
  '/guide/m01-overview/1.3-quant-mindset.html',
  '/guide/m04-backtest/4.3-metrics.html',
  '/guide/m05-strategies/5.2-dual-ma.html',
  '/guide/m11-derivatives/11.1-greeks.html',
  '/guide/m20-interview-prep/20.1-math-stats.html',
]
const BASE = 'http://127.0.0.1:5189'

async function check(page, path) {
  await page.goto(BASE + path, { waitUntil: 'networkidle' })
  const detailsCount = await page.locator('details.scb-out').count()
  if (detailsCount === 0) throw new Error(`${path}: no details.scb-out`)

  // 展开第一个折叠块
  await page.locator('details.scb-out').first().evaluate((el) => el.open = true)
  await page.waitForTimeout(500)

  const text = await page.locator('details.scb-out .scb-out-text').first().textContent().catch(() => '')
  const svgCount = await page.locator('details.scb-out .scb-out-svgs img').count()
  const errorVisible = await page.locator('details.scb-out .scb-out-error').count()
  const summaryText = await page.locator('details.scb-out summary').first().textContent()

  if (!summaryText.includes('点击展开可浏览运行结果')) {
    throw new Error(`${path}: summary 文案不正确 (got "${summaryText}")`)
  }
  if (!text && svgCount === 0 && errorVisible === 0) {
    throw new Error(`${path}: 折叠块展开后为空（既无 text、也无 svg、也无 error）`)
  }
  console.log(`  ✓ ${path}: details=${detailsCount}, text=${text?.length || 0} chars, svgs=${svgCount}`)
}

async function main() {
  const browser = await chromium.launch()
  try {
    const page = await browser.newPage()
    for (const p of PAGES) await check(page, p)
    console.log(`[verify-static-code-blocks] all ${PAGES.length} pages OK`)
  } finally {
    await browser.close()
  }
}

main().catch((e) => {
  console.error(`[verify-static-code-blocks] FAIL: ${e.message}`)
  process.exit(1)
})
