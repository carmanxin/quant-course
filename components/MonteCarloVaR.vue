<template>
  <div class="card">
    <h4>📉 蒙特卡洛VaR计算器</h4>
    <div class="input-group">
      <label>初始资金($) <input v-model.number="initial" type="number" step="1000"></label>
      <label>年化收益(%) <input v-model.number="mu" type="number" step="0.1"></label>
      <label>年化波动(%) <input v-model.number="sigma" type="number" step="0.1"></label>
      <label>持仓天数 <input v-model.number="days" type="number" min="1"></label>
      <label>置信水平(%) <input v-model.number="conf" type="number" min="90" max="99"></label>
      <button @click="run">计算VaR</button>
    </div>
    <p class="result-text" style="color:#e2e8f0" v-if="result">
      {{ conf }}%置信度，{{ days }}天VaR：<strong>${{ result.varVal.toFixed(2) }}</strong>，CVaR：<strong>${{ result.cvar.toFixed(2) }}</strong>
    </p>
    <div ref="chartRef" class="chart-container" style="height:220px"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useData } from 'vitepress'
import { normalRandom } from './useRandom'

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const { isDark } = useData()

const initial = ref(100000), mu = ref(8), sigma = ref(20), days = ref(30), conf = ref(95)
interface VaRResult { varVal: number; cvar: number }
const result = ref<VaRResult | null>(null)

function run() {
  const init = initial.value
  const drift = (mu.value / 100 - 0.5 * Math.pow(sigma.value / 100, 2)) / 252
  const vol = sigma.value / 100 / Math.sqrt(252)
  const d = days.value, c = conf.value / 100
  const nSims = 5000

  const finals: number[] = []
  const samplePath = [init]
  let sp = init

  for (let s = 0; s < nSims; s++) {
    let p = init
    for (let t = 0; t < d; t++) p *= Math.exp(drift + vol * normalRandom(0, 1))
    finals.push(p)
    if (s === 0) {
      sp = init
      for (let t = 1; t <= d; t++) {
        sp *= Math.exp(drift + vol * normalRandom(0, 1))
        samplePath.push(sp)
      }
    }
  }

  finals.sort((a, b) => a - b)
  const varVal = init - finals[Math.floor((1 - c) * nSims)]
  const tail = finals.slice(0, Math.floor((1 - c) * nSims))
  const cvar = tail.length ? init - (tail.reduce((a, b) => a + b, 0) / tail.length) : 0
  result.value = { varVal, cvar }

  chart?.setOption({
    grid: { left: 50, right: 20, top: 15, bottom: 30 },
    xAxis: { type: 'category', show: false },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [{ type: 'line', data: samplePath, showSymbol: false, lineStyle: { color: '#f59e0b', width: 2 } }]
  }, { notMerge: true })
}

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value, isDark.value ? 'dark' : undefined)
    run()
    window.addEventListener('resize', () => chart?.resize())
    watch(isDark, () => {
      chart?.dispose()
      if (chartRef.value) {
        chart = echarts.init(chartRef.value, isDark.value ? 'dark' : undefined)
        run()
      }
    })
  }
})
</script>
