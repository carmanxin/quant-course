import * as echarts from 'echarts'
import { ref, onMounted, onUnmounted, watch, type Ref } from 'vue'
import { useData } from 'vitepress'

export function useECharts(options: Ref<any>) {
  const chartRef = ref<HTMLElement | null>(null)
  let chart: echarts.ECharts | null = null

  const { isDark } = useData()

  const getTheme = () => isDark.value ? 'dark' : undefined

  const initChart = () => {
    if (chartRef.value) {
      chart?.dispose()
      chart = echarts.init(chartRef.value, getTheme())
      chart.setOption(options.value)
    }
  }

  const updateChart = () => {
    if (chart) {
      chart.setOption(options.value, { notMerge: true })
    } else {
      initChart()
    }
  }

  onMounted(() => {
    initChart()
    window.addEventListener('resize', () => chart?.resize())
  })

  onUnmounted(() => {
    window.removeEventListener('resize', () => chart?.resize())
    chart?.dispose()
  })

  watch(options, updateChart, { deep: true })
  watch(isDark, () => {
    // Re-init chart on theme change
    initChart()
  })

  return { chartRef, updateChart, isDark }
}
