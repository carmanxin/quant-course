<template>
  <div class="card">
    <h4>📊 因子IC分析模拟器</h4>
    <button @click="run">运行IC分析</button>
    <div v-if="result" class="result-text" style="margin:12px 0">
      <p>IC 均值：<strong>{{ result.icMean.toFixed(4) }}</strong>，IC 标准差：<strong>{{ result.icStd.toFixed(4) }}</strong>，IR：<strong>{{ result.ir.toFixed(2) }}</strong></p>
    </div>
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

interface ICResult { icMean: number; icStd: number; ir: number }
const result = ref<ICResult | null>(null)

function run() {
  const periods = 50, stocks = 100
  const factor: number[][] = [], ret: number[][] = []
  for (let t = 0; t < periods; t++) {
    const f: number[] = [], r: number[] = []
    for (let s = 0; s < stocks; s++) {
      f.push(normalRandom(0, 0.1))
      r.push(0.02 * f[s] + normalRandom(0, 0.05))
    }
    factor.push(f); ret.push(r)
  }

  const rank = (arr: number[]) =>
    arr.map((v, i) => [v, i] as [number, number])
      .sort((a, b) => a[0] - b[0])
      .map((_, i, arr) => { arr[i][0] = i + 1; return arr[i] })
      .sort((a, b) => a[1] - b[1])
      .map(x => x[0])

  const ic: number[] = []
  for (let t = 0; t < periods; t++) {
    const rankF = rank(factor[t]), rankR = rank(ret[t])
    const d2 = rankF.reduce((sum, rf, i) => sum + (rf - rankR[i]) ** 2, 0)
    ic.push(1 - (6 * d2) / (stocks * (stocks * stocks - 1)))
  }

  const icMean = ic.reduce((a, b) => a + b, 0) / periods
  const icStd = Math.sqrt(ic.reduce((s, v) => s + (v - icMean) ** 2, 0) / periods)
  const ir = icStd ? icMean / icStd : 0
  result.value = { icMean, icStd, ir }

  chart?.setOption({
    grid: { left: 50, right: 20, top: 15, bottom: 30 },
    xAxis: { type: 'category', show: false },
    yAxis: { type: 'value', axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [{ type: 'line', data: ic, showSymbol: false, lineStyle: { color: '#a78bfa', width: 2 } }]
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
