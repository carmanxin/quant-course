// Playwright 自动化测试：验证所有 PythonPlayground 的实际运行结果
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE = 'http://localhost:5173';
const PLAYGROUNDS = [
  { chapter: '/guide/m01-overview/1.3-quant-mindset.html', name: '1.3 Bootstrap检验' },
  { chapter: '/guide/m02-finance-math/2.1-microstructure.html', name: '2.1 冲击成本' },
  { chapter: '/guide/m02-finance-math/2.2-asset-pricing.html', name: '2.2 Black-Scholes' },
  { chapter: '/guide/m03-python-data/3.1-python-stack.html', name: '3.1 移动平均' },
  { chapter: '/guide/m03-python-data/3.2-data-cleaning.html', name: '3.2 数据清洗' },
  { chapter: '/guide/m04-backtest/4.3-metrics.html', name: '4.3 绩效指标' },
  { chapter: '/guide/m05-strategies/5.1-factors.html', name: '5.1 IC分析' },
  { chapter: '/guide/m05-strategies/5.3-stat-arb.html', name: '5.3 统计套利' },
  { chapter: '/guide/m06-portfolio/6.1-mvo.html', name: '6.1 均值方差优化' },
  { chapter: '/guide/m06-portfolio/6.5-var.html', name: '6.5 Monte Carlo VaR' },
  { chapter: '/guide/m08-ml-alt-data/8.1-supervised.html', name: '8.1 随机森林' },
  { chapter: '/guide/m11-derivatives/11.1-greeks.html', name: '11.1 Greeks' },
  { chapter: '/guide/m12-fixed-income/12.1-yield-curve.html', name: '12.1 收益率曲线' },
  { chapter: '/guide/m14-microstructure-deep/14.3-optimal-execution.html', name: '14.3 最优执行' },
  { chapter: '/guide/m20-interview-prep/20.1-math-stats.html', name: '20.1 Monty Hall' },
];

async function testPlayground(page, pg) {
  console.log(`\n📋 测试: ${pg.name}`);
  console.log(`   URL: ${BASE}${pg.chapter}`);

  await page.goto(`${BASE}${pg.chapter}`, { waitUntil: 'networkidle', timeout: 30000 });

  // Wait for the PythonPlayground to render
  await page.waitForSelector('.py-playground', { timeout: 15000 });
  // Wait a bit for Vue hydration + slot loading
  await page.waitForTimeout(2000);

  // Find the playground's "Run" button
  const btn = page.locator('.py-playground .py-run-btn').first();
  if (!(await btn.isVisible())) {
    return { name: pg.name, status: 'SKIP', error: 'Run button not found' };
  }

  // Click run
  await btn.click();
  console.log('   ▶ 点击运行...');

  // Wait for output (either success .py-output or error .py-error)
  // Pyodide first load takes ~15-30 seconds
  try {
    await page.waitForSelector('.py-output pre', { timeout: 60000 });
  } catch (e) {
    return { name: pg.name, status: 'TIMEOUT', error: '60s timeout waiting for output' };
  }

  // Get the output
  const output = await page.locator('.py-output pre').first().textContent();
  const isError = await page.locator('.py-error').first().isVisible().catch(() => false);

  console.log('   --- 输出 ---');
  console.log(output.split('\n').map(l => '   ' + l).join('\n'));
  console.log('   ------------');

  if (isError || output.toLowerCase().includes('traceback') || output.toLowerCase().includes('syntaxerror')) {
    return { name: pg.name, status: 'ERROR', output };
  }
  return { name: pg.name, status: 'OK', output };
}

async function main() {
  console.log('🔍 PythonPlayground 全量运行检测');
  console.log('================================\n');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Collect console errors from the browser
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', err => consoleErrors.push(err.message));

  const results = [];
  for (const pg of PLAYGROUNDS) {
    try {
      const r = await testPlayground(page, pg);
      results.push(r);
    } catch (e) {
      results.push({ name: pg.name, status: 'EXCEPTION', error: e.message });
    }
  }

  await browser.close();

  // Summary
  console.log('\n\n================================');
  console.log('📊 测试汇总');
  console.log('================================');
  const ok = results.filter(r => r.status === 'OK').length;
  const err = results.filter(r => r.status === 'ERROR').length;
  const skip = results.filter(r => r.status === 'SKIP' || r.status === 'TIMEOUT' || r.status === 'EXCEPTION').length;

  console.log(`✅ 通过: ${ok}`);
  console.log(`❌ 错误: ${err}`);
  console.log(`⚠️ 跳过: ${skip}`);
  console.log(`📁 总计: ${results.length}`);

  if (err > 0) {
    console.log('\n❌ 错误详情:');
    for (const r of results.filter(r => r.status === 'ERROR')) {
      console.log(`  ${r.name}: ${r.output?.substring(0, 200)}`);
    }
  }
  if (skip > 0) {
    console.log('\n⚠️ 跳过/超时:');
    for (const r of results.filter(r => r.status !== 'OK' && r.status !== 'ERROR')) {
      console.log(`  ${r.name}: ${r.error}`);
    }
  }

  // Write results file
  fs.writeFileSync(
    path.join(__dirname, 'playground-results.json'),
    JSON.stringify(results, null, 2)
  );
  console.log('\n📄 详细结果已写入 tests/playground-results.json');

  process.exit(err > 0 ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
