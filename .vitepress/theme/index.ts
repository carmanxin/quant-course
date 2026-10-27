import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import './style.css'

// 交互式量化计算/可视化组件
import ExpectedValueCalc from '../../components/ExpectedValueCalc.vue'
import RandomWalkChart from '../../components/RandomWalkChart.vue'
import CorrelationHeatmap from '../../components/CorrelationHeatmap.vue'
import PerformanceSimulator from '../../components/PerformanceSimulator.vue'
import ICAnalysis from '../../components/ICAnalysis.vue'
import DualMABacktest from '../../components/DualMABacktest.vue'
import EfficientFrontier from '../../components/EfficientFrontier.vue'
import KellyCalc from '../../components/KellyCalc.vue'
import MonteCarloVaR from '../../components/MonteCarloVaR.vue'
import RunLocally from '../../components/RunLocally.vue'

// FinTech 风格定制组件
import FinTechHero from '../../components/FinTechHero.vue'
import TickerBar from '../../components/TickerBar.vue'
import AnimatedButton from '../../components/AnimatedButton.vue'
import MarketDashboard from '../../components/MarketDashboard.vue'
import StaticCodeBlock from '../../components/StaticCodeBlock.vue'
import QuizBlock from '../../components/QuizBlock.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    // 计算器 / 图表组件
    app.component('ExpectedValueCalc', ExpectedValueCalc)
    app.component('RandomWalkChart', RandomWalkChart)
    app.component('CorrelationHeatmap', CorrelationHeatmap)
    app.component('PerformanceSimulator', PerformanceSimulator)
    app.component('ICAnalysis', ICAnalysis)
    app.component('DualMABacktest', DualMABacktest)
    app.component('EfficientFrontier', EfficientFrontier)
    app.component('KellyCalc', KellyCalc)
    app.component('MonteCarloVaR', MonteCarloVaR)
    // ⚠ 2026-10-26 司礼监第三令：RunLocally 此前只 import 未注册，
    //   导致 12 个页面（m03/m08/m09/m10/m15/m17）的 <RunLocally> 被当作
    //   未知自定义元素渲染，交互能力全部失效。
    app.component('RunLocally', RunLocally)
    app.component('StaticCodeBlock', StaticCodeBlock)
    // ⚠ 2026-10-26 司礼监第三令：QuizBlock 同样只 import 未注册，
    //   13 个页面的「小测验」交互态全部失效。
    app.component('QuizBlock', QuizBlock)
    // FinTech 视觉组件
    app.component('FinTechHero', FinTechHero)
    app.component('TickerBar', TickerBar)
    app.component('AnimatedButton', AnimatedButton)
    app.component('MarketDashboard', MarketDashboard)
  }
} satisfies Theme
