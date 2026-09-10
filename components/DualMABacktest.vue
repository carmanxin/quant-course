<template>
  <div class="card">
    <h4>📊 双均线交叉策略模拟</h4>
    <div class="input-group">
      <label>快线周期 <input v-model.number="fastPeriod" type="number" min="2" max="50"></label>
      <label>慢线周期 <input v-model.number="slowPeriod" type="number" min="5" max="100"></label>
      <button @click="run">运行回测</button>
    </div>
    <div ref="priceRef" class="chart-container" style="height:320px"></div>
    <div ref="eqRef" class="chart-container" style="height:170px"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useData } from 'vitepress'

const priceRef = ref<HTMLElement | null>(null)
const eqRef = ref<HTMLElement | null>(null)
let priceChart: echarts.ECharts | null = null
let eqChart: echarts.ECharts | null = null
const { isDark } = useData()
const fastPeriod = ref(10)
const slowPeriod = ref(30)

function run() {
  const fast = fastPeriod.value, slow = slowPeriod.value
  if (fast >= slow) {
    priceChart?.clear()
    eqChart?.clear()
    eqChart?.setOption({
      grid: { left: 50, right: 20, top: 15, bottom: 30 },
      xAxis: { type: 'category', show: false },
      yAxis: { type: 'value', axisLabel: { color: '#f87171', fontSize: 11 } },
      series: [],
      title: { text: `参数无效：快线周期 (${fast}) 必须小于慢线周期 (${slow})`, left: 'center', top: 'middle', textStyle: { color: '#f87171', fontSize: 13, fontWeight: 600 } }
    }, { notMerge: true })
    return
  }

  const prices = [100]
  for (let i = 1; i < 200; i++) prices.push(Math.max(prices[i - 1] + (Math.random() - 0.48) * 2.5, 10))

  const ma = (data: number[], period: number) => {
    const res: (number | null)[] = []
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) res.push(null)
      else res.push(data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) / period)
    }
    return res
  }
  const fma = ma(prices, fast), sma = ma(prices, slow)

  const buyPoints: [number, number][] = []
  const sellPoints: [number, number][] = []
  let pos = 0, capital = 100000
  const equity = [capital]

  for (let i = 0; i < prices.length; i++) {
    if (fma[i] && sma[i]) {
      if (fma[i]! > sma[i]! && pos === 0) { pos = 1; buyPoints.push([i, prices[i]]) }
      else if (fma[i]! < sma[i]! && pos === 1) { pos = 0; sellPoints.push([i, prices[i]]) }
    }
    if (i > 0 && pos === 1) capital *= prices[i] / prices[i - 1]
    equity.push(capital)
  }

  const baseGrid = { left: 50, right: 20, top: 15, bottom: 30 }
  priceChart?.setOption({
    grid: baseGrid,
    xAxis: { type: 'category', show: false },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [
      { type: 'line', data: prices, showSymbol: false, lineStyle: { color: '#e2e8f0', width: 1.5 }, name: '价格' },
      { type: 'line', data: fma, showSymbol: false, lineStyle: { color: '#38bdf8', width: 1 }, name: `MA${fast}` },
      { type: 'line', data: sma, showSymbol: false, lineStyle: { color: '#f472b6', width: 1 }, name: `MA${slow}` },
      { type: 'scatter', data: buyPoints, symbolSize: 8, itemStyle: { color: '#10b981', borderColor: '#fff', borderWidth: 1 }, name: '买入' },
      { type: 'scatter', data: sellPoints, symbolSize: 8, itemStyle: { color: '#ef4444', borderColor: '#fff', borderWidth: 1 }, name: '卖出' },
    ]
  }, { notMerge: true })

  eqChart?.setOption({
    grid: baseGrid,
    xAxis: { type: 'category', show: false },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [{ type: 'line', data: equity, showSymbol: false, lineStyle: { color: '#f59e0b', width: 2 } }]
  }, { notMerge: true })
}

onMounted(() => {
  const theme = isDark.value ? 'dark' : undefined
  if (priceRef.value) priceChart = echarts.init(priceRef.value, theme)
  if (eqRef.value) eqChart = echarts.init(eqRef.value, theme)
  run()
  window.addEventListener('resize', () => { priceChart?.resize(); eqChart?.resize() })
  watch(isDark, () => {
    priceChart?.dispose(); eqChart?.dispose()
    const t = isDark.value ? 'dark' : undefined
    if (priceRef.value) priceChart = echarts.init(priceRef.value, t)
    if (eqRef.value) eqChart = echarts.init(eqRef.value, t)
    run()
  })
})
</script>
