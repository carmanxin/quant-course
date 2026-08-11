<template>
  <div class="card">
    <h4>📈 两资产有效前沿模拟器</h4>
    <div class="input-group">
      <label>资产A收益(%) <input v-model.number="retA" type="number" step="0.1"></label>
      <label>风险(%) <input v-model.number="riskA" type="number" step="0.1"></label>
      <label>资产B收益(%) <input v-model.number="retB" type="number" step="0.1"></label>
      <label>风险(%) <input v-model.number="riskB" type="number" step="0.1"></label>
      <label>相关系数 <input v-model.number="corr" type="number" step="0.1" min="-1" max="1"></label>
      <button @click="update">更新图表</button>
    </div>
    <div ref="chartRef" class="chart-container" style="height:320px"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useData } from 'vitepress'

const chartRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null
const { isDark } = useData()

const retA = ref(8), riskA = ref(15)
const retB = ref(12), riskB = ref(25)
const corr = ref(0.2)

function update() {
  const rA = retA.value / 100, sA = riskA.value / 100
  const rB = retB.value / 100, sB = riskB.value / 100
  const c = corr.value
  const cov = c * sA * sB, varA = sA * sA, varB = sB * sB

  const pts: { ret: number; std: number; w: number }[] = []
  for (let w = 0; w <= 1.01; w += 0.01) {
    const wB = 1 - w
    pts.push({
      w: +w.toFixed(2),
      ret: w * rA + wB * rB,
      std: Math.sqrt(Math.max(0, w * w * varA + wB * wB * varB + 2 * w * wB * cov))
    })
  }

  const minVarW = (varB - cov) / (varA + varB - 2 * cov)
  const minVarPt = pts.reduce((best, p) => p.std < best.std ? p : best)
  const frontier = pts.filter(p => p.ret >= minVarPt.ret)

  let maxSh = -Infinity, maxShW = 0
  frontier.forEach(p => { if (p.std > 0.0001) { const sh = p.ret / p.std; if (sh > maxSh) { maxSh = sh; maxShW = p.w } } })
  const maxShPt = pts.find(p => Math.abs(p.w - maxShW) < 0.005) || frontier[0]

  const frontierData = frontier.map(p => [p.std * 100, p.ret * 100])
  const allData = pts.map(p => [p.std * 100, p.ret * 100])
  const mvPoint: [number, number] = [minVarPt.std * 100, minVarPt.ret * 100]
  const msPoint: [number, number] = [maxShPt.std * 100, maxShPt.ret * 100]

  const assetPoints: [number, number][] = [[sA * 100, rA * 100], [sB * 100, rB * 100]]

  chart?.setOption({
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'value', name: '风险 (波动率 %)', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', name: '收益 (%)', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#94a3b8' } },
    series: [
      { type: 'scatter', data: allData, symbolSize: 2, itemStyle: { color: '#334155' }, name: '全部组合' },
      { type: 'line', data: frontierData, showSymbol: false, lineStyle: { color: '#38bdf8', width: 2 }, name: '有效前沿' },
      { type: 'scatter', data: assetPoints, symbolSize: 12, itemStyle: { color: '#f59e0b' }, name: '单一资产', label: { show: true, formatter: (p: any) => p.dataIndex === 0 ? 'A' : 'B', color: '#fff' } },
      { type: 'scatter', data: [mvPoint], symbolSize: 10, itemStyle: { color: '#10b981', borderColor: '#fff', borderWidth: 1 }, name: '最小方差' },
      { type: 'scatter', data: [msPoint], symbolSize: 10, itemStyle: { color: '#ef4444', borderColor: '#fff', borderWidth: 1 }, name: '最大夏普' },
    ]
  }, { notMerge: true })
}

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value, isDark.value ? 'dark' : undefined)
    update()
    window.addEventListener('resize', () => chart?.resize())
    watch(isDark, () => {
      chart?.dispose()
      if (chartRef.value) {
        chart = echarts.init(chartRef.value, isDark.value ? 'dark' : undefined)
        update()
      }
    })
  }
})
</script>
