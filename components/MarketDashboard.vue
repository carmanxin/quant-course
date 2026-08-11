<template>
  <div class="mdb" :class="{ 'mdb--bull': trendBull, 'mdb--bear': !trendBull }">
    <!-- 顶部实时行情条 -->
    <div class="mdb-ticker">
      <div class="mdb-ticker-row">
        <span v-for="(it, i) in displayQuotes" :key="i" class="mdb-tk-item">
          <span class="sym">{{ it.sym }}</span>
          <span class="px">{{ it.px.toFixed(it.sym === 'VIX' ? 2 : (it.px < 100 ? 3 : 2)) }}</span>
          <span :class="['chg', it.chg >= 0 ? 'up' : 'down']">
            <span class="ar">{{ it.chg >= 0 ? '▲' : '▼' }}</span>
            {{ it.chg >= 0 ? '+' : '' }}{{ it.chg.toFixed(2) }}%
          </span>
        </span>
      </div>
    </div>

    <!-- 主体三列 -->
    <div class="mdb-main">
      <!-- K 线图 -->
      <div class="mdb-chart">
        <div class="mdb-chart-head">
          <span class="mdb-chart-title">
            <span class="dot"></span>
            <span class="name">{{ chartSym }}</span>
            <span class="px">${{ chartPx.toFixed(2) }}</span>
            <span :class="['chg-big', chgColor]">{{ chartChg >= 0 ? '+' : '' }}{{ chartChg.toFixed(2) }}%</span>
          </span>
          <span class="mdb-chart-intervals">
            <span :class="{active: ivl==='1m'}" @click="ivl='1m'">1m</span>
            <span :class="{active: ivl==='5m'}" @click="ivl='5m'">5m</span>
            <span :class="{active: ivl==='1h'}" @click="ivl='1h'">1h</span>
            <span :class="{active: ivl==='1d'}" @click="ivl='1d'">1d</span>
          </span>
        </div>
        <svg viewBox="0 0 400 200" class="mdb-svg" preserveAspectRatio="none">
          <g class="grid">
            <line v-for="i in 5" :key="'h'+i" x1="0" :y1="i*40" x2="400" :y2="i*40" />
            <line v-for="i in 8" :key="'v'+i" :x1="i*50" y1="0" :x2="i*50" y2="200" />
          </g>
          <g class="candles">
            <g v-for="(c, idx) in candles" :key="idx" :transform="`translate(${idx * 8 + 4},0)`">
              <line :x1="0" :y1="200 - c.h * 1.6" :x2="0" :y2="200 - c.l * 1.6"
                    :class="c.o <= c.c ? 'wick bull' : 'wick bear'" />
              <rect :x="-3" :y="200 - Math.max(c.o, c.c) * 1.6"
                    width="6" :height="Math.abs(c.o - c.c) * 1.6"
                    :class="c.o <= c.c ? 'body bull' : 'body bear'" />
            </g>
          </g>
          <path :d="maPath" class="ma" />
          <line x1="0" :y1="200 - lastCandle.c * 1.6" x2="400" :y2="200 - lastCandle.c * 1.6" class="lastline" stroke-dasharray="2 2" />
        </svg>
        <div class="mdb-chart-foot">
          <span>成交量 {{ volDisplay }}</span>
          <span>MA20 {{ ma20.toFixed(2) }}</span>
          <span>RSI {{ rsi.toFixed(1) }}</span>
        </div>
      </div>

      <!-- 订单簿 -->
      <div class="mdb-book">
        <div class="mdb-book-head">
          <span>订单簿</span>
          <span class="mdb-book-sub">Level-2 模拟</span>
        </div>
        <div class="mdb-book-asks">
          <div v-for="(lv, i) in asksRev" :key="'a'+i" class="mdb-book-row ask">
            <span class="px">{{ lv.px.toFixed(2) }}</span>
            <span class="sz">{{ lv.sz.toFixed(3) }}</span>
            <div class="bar" :style="{ width: lv.sz/2 + '%', right: 0 }"></div>
          </div>
        </div>
        <div class="mdb-book-mid">
          <span :class="trendBull ? 'up' : 'down'">{{ spreadPx.toFixed(2) }}</span>
          <span class="lbl">spread {{ spreadTick }} ticks</span>
        </div>
        <div class="mdb-book-bids">
          <div v-for="(lv, i) in bids" :key="'b'+i" class="mdb-book-row bid">
            <span class="px">{{ lv.px.toFixed(2) }}</span>
            <span class="sz">{{ lv.sz.toFixed(3) }}</span>
            <div class="bar" :style="{ width: lv.sz/2 + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部策略 PnL 曲线 -->
    <div class="mdb-pnl">
      <div class="mdb-pnl-head">
        <span>策略 PnL · 回测模拟</span>
        <span class="mdb-pnl-val" :class="trendBull ? 'up' : 'down'">
          {{ (equityNow - 100000).toFixed(0) }} USD
          <small>({{ ((equityNow / 100000 - 1) * 100).toFixed(2) }}%)</small>
        </span>
      </div>
      <svg viewBox="0 0 600 80" class="mdb-pnl-svg" preserveAspectRatio="none">
        <defs>
          <linearGradient id="pnlFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" :stop-color="trendBull ? 'rgba(0,229,160,.6)' : 'rgba(255,77,109,.6)'" />
            <stop offset="100%" :stop-color="trendBull ? 'rgba(0,229,160,0)' : 'rgba(255,77,109,0)'" />
          </linearGradient>
        </defs>
        <path :d="pnlFill" fill="url(#pnlFill)" />
        <path :d="pnlLine" :class="trendBull ? 'pnl-line up' : 'pnl-line down'" fill="none" stroke-width="2" />
      </svg>
      <div class="mdb-pnl-foot">
        <span>Sharpe {{ sharpe.toFixed(2) }}</span>
        <span>Max DD {{ maxDD.toFixed(1) }}%</span>
        <span>胜率 {{ winRate.toFixed(0) }}%</span>
        <span>交易 {{ tradeCount }} 笔</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Quote { sym: string; px: number; chg: number }
interface Candle { o: number; c: number; h: number; l: number }
interface BookLevel { px: number; sz: number }

// ============ 实时行情初始值 ============
const quotes = ref<Quote[]>([
  { sym: 'AAPL',    px: 219.45, chg: -0.78 },
  { sym: 'NVDA',    px: 912.80, chg:  4.56 },
  { sym: 'TSLA',    px: 245.30, chg:  3.21 },
  { sym: 'MSFT',    px: 432.10, chg:  1.04 },
  { sym: 'GOOG',    px: 168.50, chg: -0.35 },
  { sym: 'META',    px: 568.20, chg:  2.10 },
  { sym: 'AMZN',    px: 192.40, chg:  0.88 },
  { sym: 'BTC',  px: 67890.12, chg:  2.34 },
  { sym: 'ETH',  px:  3456.78, chg:  1.56 },
  { sym: 'SPX',   px:  5680.10, chg:  0.42 },
  { sym: 'VIX',   px:    16.42, chg: -3.46 },
  { sym: 'CSI300', px: 3789.20, chg: -1.12 },
])
const displayQuotes = computed(() => quotes.value)

const ivl = ref<'1m' | '5m' | '1h' | '1d'>('1m')
const chartSym = ref('SPX')
const chartPx = ref(5680.10)
const chartChg = ref(0.42)
const candles = ref<Candle[]>(generateInitialCandles())
const lastCandle = computed(() => candles.value[candles.value.length - 1])

function generateInitialCandles(): Candle[] {
  const list: Candle[] = []
  let prev = 5600
  for (let i = 0; i < 50; i++) {
    const o = prev
    const drift = (Math.random() - 0.48) * 30
    const c = Math.max(1, o + drift)
    const range = Math.random() * 25 + 5
    const h = Math.max(o, c) + Math.random() * range
    const l = Math.min(o, c) - Math.random() * range
    list.push({ o, c, h, l })
    prev = c
  }
  return list
}

const maPath = computed(() => {
  if (candles.value.length < 20) return ''
  const closes = candles.value.map(c => c.c)
  const points: string[] = []
  for (let i = 19; i < closes.length; i++) {
    const slice = closes.slice(i - 19, i + 1)
    const avg = slice.reduce((a, b) => a + b) / 20
    const x = i * 8 + 4
    const y = 200 - avg * 1.6
    points.push(`${i === 19 ? 'M' : 'L'} ${x},${y}`)
  }
  return points.join(' ')
})

const ma20 = computed(() => {
  const closes = candles.value.slice(-20).map(c => c.c)
  return closes.reduce((a, b) => a + b) / closes.length
})

const rsi = computed(() => {
  const closes = candles.value.map(c => c.c)
  let gains = 0, losses = 0
  for (let i = closes.length - 14; i < closes.length; i++) {
    if (i <= 0) continue
    const diff = closes[i] - closes[i - 1]
    if (diff > 0) gains += diff
    else losses -= diff
  }
  if (losses === 0) return 100
  const rs = gains / losses
  return 100 - 100 / (1 + rs)
})

const volDisplay = computed(() => {
  const total = candles.value.slice(-20).reduce((sum, c) => sum + Math.abs(c.c - c.o), 0)
  if (total > 1e6) return (total / 1e6).toFixed(2) + 'M'
  if (total > 1e3) return (total / 1e3).toFixed(2) + 'K'
  return total.toFixed(0)
})

const chgColor = computed(() => chartChg.value >= 0 ? 'up' : 'down')

function makeBook(mid: number): { bids: BookLevel[]; asks: BookLevel[] } {
  const bids: BookLevel[] = []
  const asks: BookLevel[] = []
  for (let i = 1; i <= 8; i++) {
    bids.push({ px: mid - i * 0.5, sz: Math.random() * 1.5 + 0.3 })
    asks.push({ px: mid + i * 0.5, sz: Math.random() * 1.5 + 0.3 })
  }
  return { bids, asks }
}
const midPx = ref(100.0)
const book = ref(makeBook(midPx.value))
const bids = computed(() => book.value.bids)
const asksRev = computed(() => [...book.value.asks].reverse())
const spreadTick = computed(() => 1)
const spreadPx = computed(() => book.value.asks[0].px - book.value.bids[0].px)

const equity = ref<number[]>(Array.from({ length: 100 }, (_, i) => 100000 + i * 50))
const equityNow = computed(() => equity.value[equity.value.length - 1])
const trendBull = computed(() => equityNow.value >= 100000)

const pnlLine = computed(() => {
  const min = Math.min(...equity.value)
  const max = Math.max(...equity.value)
  const range = max - min || 1
  return equity.value.map((v, i) => {
    const x = (i / (equity.value.length - 1)) * 600
    const y = 80 - ((v - min) / range) * 70 - 5
    return `${i === 0 ? 'M' : 'L'} ${x},${y}`
  }).join(' ')
})

const pnlFill = computed(() => {
  return pnlLine.value + ' L 600,80 L 0,80 Z'
})

const sharpe = computed(() => {
  const rets = []
  for (let i = 1; i < equity.value.length; i++) {
    rets.push((equity.value[i] - equity.value[i - 1]) / equity.value[i - 1])
  }
  const mean = rets.reduce((a, b) => a + b) / rets.length
  const std = Math.sqrt(rets.map(r => (r - mean) ** 2).reduce((a, b) => a + b) / rets.length)
  return std > 0 ? (mean / std) * Math.sqrt(252) : 0
})

const maxDD = computed(() => {
  let peak = equity.value[0], dd = 0
  for (const v of equity.value) {
    if (v > peak) peak = v
    const drawdown = (peak - v) / peak * 100
    if (drawdown > dd) dd = drawdown
  }
  return dd
})

const winRate = computed(() => {
  const rets = []
  for (let i = 1; i < equity.value.length; i++) {
    rets.push(equity.value[i] - equity.value[i - 1] > 0 ? 1 : 0)
  }
  return (rets.reduce((a, b) => a + b, 0) / rets.length) * 100
})

const tradeCount = ref(247)

let tkrT: number | undefined
let chartT: number | undefined
let bookT: number | undefined
let equityT: number | undefined

onMounted(() => {
  tkrT = window.setInterval(() => {
    quotes.value = quotes.value.map(q => {
      const drift = (Math.random() - 0.5) * 0.005
      const newChg = q.chg * 0.97 + drift * 6
      const newPx = q.px * (1 + drift)
      return { ...q, px: newPx, chg: newChg }
    })
  }, 1500)

  chartT = window.setInterval(() => {
    const last = candles.value[candles.value.length - 1]
    const o = last.c
    const drift = (Math.random() - 0.48) * 25
    const c = Math.max(1, o + drift)
    const range = Math.random() * 20 + 4
    const h = Math.max(o, c) + Math.random() * range
    const l = Math.min(o, c) - Math.random() * range
    const next: Candle = { o, c, h, l }
    candles.value = [...candles.value.slice(-49), next]
    chartPx.value = c
    const open0 = candles.value[0].o
    chartChg.value = ((c - open0) / open0) * 100
  }, 2000)

  bookT = window.setInterval(() => {
    midPx.value += (Math.random() - 0.5) * 0.3
    book.value = makeBook(midPx.value)
  }, 800)

  equityT = window.setInterval(() => {
    const ret = (Math.random() - 0.45) * 0.012
    const newEq = Math.max(80000, equity.value[equity.value.length - 1] * (1 + ret))
    equity.value = [...equity.value.slice(-99), newEq]
    if (Math.random() < 0.05) {
      tradeCount.value += 1
    }
  }, 600)
})

onUnmounted(() => {
  if (tkrT) clearInterval(tkrT)
  if (chartT) clearInterval(chartT)
  if (bookT) clearInterval(bookT)
  if (equityT) clearInterval(equityT)
})
</script>

<style scoped>
.mdb {
  --mdb-bull: #00E5A0;
  --mdb-bear: #FF4D6D;
  --mdb-text: #e7eaf6;
  --mdb-text2: #8a92a6;
  --mdb-border: rgba(0, 229, 160, .12);
  background: linear-gradient(135deg, #0a0e1a 0%, #131a2b 100%);
  border: 1px solid var(--mdb-border);
  border-radius: 16px;
  overflow: hidden;
  color: var(--mdb-text);
  font-family: 'SF Mono', 'JetBrains Mono', Consolas, Menlo, monospace;
  font-size: 13px;
  position: relative;
  box-shadow: 0 12px 40px rgba(0, 0, 0, .35);
  margin: 16px 0;
}
.mdb::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 17px;
  background: linear-gradient(135deg, rgba(0,229,160,.4), rgba(0,212,255,.2), rgba(124,58,237,.3));
  z-index: -1;
  filter: blur(8px);
  opacity: .35;
}

.mdb-ticker {
  background: rgba(0, 0, 0, .35);
  padding: 8px 0;
  overflow: hidden;
  border-bottom: 1px solid var(--mdb-border);
}
.mdb-ticker-row {
  display: flex;
  gap: 24px;
  padding: 0 16px;
  animation: tickerScroll 35s linear infinite;
  white-space: nowrap;
  width: max-content;
}
@keyframes tickerScroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
.mdb-tk-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.mdb-tk-item .sym { font-weight: 700; color: #fff; font-size: 13px; }
.mdb-tk-item .px  { color: #c8cee0; }
.mdb-tk-item .chg.up { color: var(--mdb-bull); }
.mdb-tk-item .chg.down { color: var(--mdb-bear); }
.mdb-tk-item .ar { font-size: 9px; }

.mdb-main {
  display: grid;
  grid-template-columns: 1fr 220px;
  gap: 0;
}

.mdb-chart {
  padding: 14px 16px;
  border-right: 1px solid var(--mdb-border);
}
.mdb-chart-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.mdb-chart-title {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--mdb-bull);
  box-shadow: 0 0 8px var(--mdb-bull);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .35; }
}
.mdb-chart-title .name {
  color: #fff; font-weight: 700;
}
.mdb-chart-title .px { color: var(--mdb-text); }
.mdb-chart-title .chg-big.up { color: var(--mdb-bull); font-weight: 700; }
.mdb-chart-title .chg-big.down { color: var(--mdb-bear); font-weight: 700; }

.mdb-chart-intervals span {
  margin-left: 4px;
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--mdb-text2);
  cursor: pointer;
  font-size: 11px;
}
.mdb-chart-intervals span.active {
  background: rgba(0,229,160,.18);
  color: var(--mdb-bull);
}

.mdb-svg {
  width: 100%;
  height: 200px;
  display: block;
}
.mdb-svg .grid line {
  stroke: rgba(255,255,255,.04);
  stroke-width: 1;
}
.mdb-svg .candles .wick { stroke-width: 1; }
.mdb-svg .candles .body { stroke-width: 1; }
.mdb-svg .bull { fill: var(--mdb-bull); stroke: var(--mdb-bull); }
.mdb-svg .bear { fill: var(--mdb-bear); stroke: var(--mdb-bear); }
.mdb-svg .ma {
  stroke: rgba(0, 212, 255, .7);
  stroke-width: 1.5;
  fill: none;
}
.mdb-svg .lastline {
  stroke: rgba(255, 255, 255, .4);
  stroke-width: 1;
}

.mdb-chart-foot {
  display: flex;
  gap: 18px;
  padding-top: 8px;
  color: var(--mdb-text2);
  font-size: 11px;
}

.mdb-book {
  padding: 14px 12px;
}
.mdb-book-head {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--mdb-text2);
  margin-bottom: 8px;
}
.mdb-book-head > span:first-child { color: #fff; font-weight: 700; font-size: 13px; }
.mdb-book-sub { font-size: 10px; }

.mdb-book-asks, .mdb-book-bids {
  font-size: 11px;
}
.mdb-book-row {
  display: grid;
  grid-template-columns: 60px 60px 1fr;
  padding: 1px 6px;
  position: relative;
  border-radius: 2px;
}
.mdb-book-row.ask .px { color: var(--mdb-bear); }
.mdb-book-row.bid .px { color: var(--mdb-bull); }
.mdb-book-row .sz { color: var(--mdb-text2); text-align: right; }
.mdb-book-row .bar {
  position: absolute;
  top: 0;
  bottom: 0;
  z-index: -1;
  border-radius: 2px;
}
.mdb-book-row.ask .bar { background: rgba(255, 77, 109, .1); left: 0; }
.mdb-book-row.bid .bar { background: rgba(0, 229, 160, .1); right: 0; }

.mdb-book-mid {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 6px 0;
  margin: 6px 0;
  background: rgba(255,255,255,.03);
  border-radius: 4px;
  font-weight: 700;
  font-size: 14px;
}
.mdb-book-mid .up { color: var(--mdb-bull); }
.mdb-book-mid .down { color: var(--mdb-bear); }
.mdb-book-mid .lbl { color: var(--mdb-text2); font-weight: 400; font-size: 10px; }

.mdb-pnl {
  border-top: 1px solid var(--mdb-border);
  padding: 12px 16px 14px;
}
.mdb-pnl-head {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--mdb-text2);
  margin-bottom: 4px;
}
.mdb-pnl-head > span:first-child { color: #fff; font-weight: 700; }
.mdb-pnl-val.up   { color: var(--mdb-bull); font-weight: 700; }
.mdb-pnl-val.down { color: var(--mdb-bear); font-weight: 700; }
.mdb-pnl-val small { font-weight: 400; margin-left: 4px; }
.mdb-pnl-svg {
  width: 100%;
  height: 80px;
  display: block;
}
.mdb-pnl-line.up   { stroke: var(--mdb-bull); }
.mdb-pnl-line.down { stroke: var(--mdb-bear); }
.mdb-pnl-foot {
  display: flex;
  gap: 16px;
  padding-top: 6px;
  font-size: 11px;
  color: var(--mdb-text2);
}
</style>
