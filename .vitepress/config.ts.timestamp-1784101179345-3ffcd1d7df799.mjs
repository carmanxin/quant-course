// .vitepress/config.ts
import { defineConfig } from "file:///D:/AI/study/quant/node_modules/vitepress/dist/node/index.js";
var sidebar = [
  {
    text: "\u6A21\u5757\u4E00\uFF1A\u91CF\u5316\u4EA4\u6613\u5168\u666F\u4E0E\u884C\u4E1A\u8BA4\u77E5",
    collapsed: false,
    items: [
      { text: "1.1 \u53D1\u5C55\u53F2\u4E0E\u751F\u6001", link: "/guide/m01-overview/1.1-history" },
      { text: "1.2 \u7B56\u7565\u5206\u7C7B", link: "/guide/m01-overview/1.2-strategy-types" },
      { text: "1.3 \u91CF\u5316\u601D\u7EF4\u6838\u5FC3", link: "/guide/m01-overview/1.3-quant-mindset" },
      { text: "1.4 \u73B0\u5B9E\u6311\u6218", link: "/guide/m01-overview/1.4-challenges" },
      { text: "1.5 \u884C\u4E1A\u683C\u5C40 2024-2026", link: "/guide/m01-overview/1.5-industry-2026" },
      { text: "1.6 \u5C97\u4F4D\u56FE\u8C31\u4E0E\u80FD\u529B\u6A21\u578B", link: "/guide/m01-overview/1.6-career-map" },
      { text: "1.7 \u5B66\u4E60\u8DEF\u5F84\u4E0E\u5751\u70B9", link: "/guide/m01-overview/1.7-learning-roadmap" }
    ]
  },
  {
    text: "\u6A21\u5757\u4E8C\uFF1A\u91D1\u878D\u57FA\u7840\u4E0E\u6570\u7406\u5DE5\u5177",
    collapsed: true,
    items: [
      { text: "2.1 \u5E02\u573A\u5FAE\u89C2\u7ED3\u6784", link: "/guide/m02-finance-math/2.1-microstructure" },
      { text: "2.2 \u8D44\u4EA7\u5B9A\u4EF7\u57FA\u7840", link: "/guide/m02-finance-math/2.2-asset-pricing" },
      { text: "2.3 \u6982\u7387\u7EDF\u8BA1\u4E0E\u76F8\u5173\u6027", link: "/guide/m02-finance-math/2.3-prob-stats" },
      { text: "2.4 \u65F6\u95F4\u5E8F\u5217\u5206\u6790", link: "/guide/m02-finance-math/2.4-time-series" },
      { text: "2.5 \u7EBF\u6027\u6A21\u578B\u4E0E\u6B63\u5219\u5316", link: "/guide/m02-finance-math/2.5-linear-models" }
    ]
  },
  {
    text: "\u6A21\u5757\u4E09\uFF1APython \u91CF\u5316\u7F16\u7A0B\u4E0E\u6570\u636E\u5DE5\u7A0B",
    collapsed: true,
    items: [
      { text: "3.1 Python\u6570\u636E\u6808", link: "/guide/m03-python-data/3.1-python-stack" },
      { text: "3.2 \u6570\u636E\u83B7\u53D6\u4E0E\u6E05\u6D17", link: "/guide/m03-python-data/3.2-data-cleaning" },
      { text: "3.3 \u6027\u80FD\u4F18\u5316", link: "/guide/m03-python-data/3.3-performance" },
      { text: "3.4 \u91D1\u878D\u6570\u636E\u7279\u8272\u5904\u7406", link: "/guide/m03-python-data/3.4-fin-data" },
      { text: "3.5 \u53EF\u89C6\u5316\u4E0E\u63A2\u7D22", link: "/guide/m03-python-data/3.5-visualization" }
    ]
  },
  {
    text: "\u6A21\u5757\u56DB\uFF1A\u56DE\u6D4B\u6846\u67B6\u4E0E\u7EE9\u6548\u8BC4\u4F30",
    collapsed: true,
    items: [
      { text: "4.1 \u56DE\u6D4B\u5F15\u64CE\u539F\u7406", link: "/guide/m04-backtest/4.1-engine" },
      { text: "4.2 \u4EA4\u6613\u6210\u672C\u5EFA\u6A21", link: "/guide/m04-backtest/4.2-cost-model" },
      { text: "4.3 \u7EE9\u6548\u6307\u6807\u5168\u666F", link: "/guide/m04-backtest/4.3-metrics" },
      { text: "4.4 \u56DE\u6D4B\u9677\u9631\u4E0E\u5BF9\u7B56", link: "/guide/m04-backtest/4.4-pitfalls" },
      { text: "4.5 \u7EDF\u8BA1\u68C0\u9A8C", link: "/guide/m04-backtest/4.5-stat-tests" },
      { text: "4.6 \u4E3B\u6D41\u56DE\u6D4B\u6846\u67B6\u6A2A\u8BC4", link: "/guide/m04-backtest/4.6-frameworks-comparison" },
      { text: "4.7 \u5B8C\u6574\u4E8B\u4EF6\u9A71\u52A8\u56DE\u6D4B\u5B9E\u6218", link: "/guide/m04-backtest/4.7-event-driven-full" },
      { text: "4.8 \u5408\u6210\u6570\u636E\u56DE\u6D4B", link: "/guide/m04-backtest/4.8-synthetic-data" },
      { text: "4.9 \u591A\u7B56\u7565\u7EC4\u5408\u56DE\u6D4B", link: "/guide/m04-backtest/4.9-multi-strategy" },
      { text: "4.10 Walk-Forward \u6EDA\u52A8\u56DE\u6D4B", link: "/guide/m04-backtest/4.10-walk-forward" }
    ]
  },
  {
    text: "\u6A21\u5757\u4E94\uFF1A\u7B56\u7565\u5F00\u53D1\u5DE5\u574A",
    collapsed: true,
    items: [
      { text: "5.1 \u56E0\u5B50\u6295\u8D44\u4F53\u7CFB", link: "/guide/m05-strategies/5.1-factors" },
      { text: "5.2 \u53CC\u5747\u7EBF\u7B56\u7565\u6A21\u62DF", link: "/guide/m05-strategies/5.2-dual-ma" },
      { text: "5.3 \u7EDF\u8BA1\u5957\u5229", link: "/guide/m05-strategies/5.3-stat-arb" },
      { text: "5.4 CTA\u8D8B\u52BF\u8DDF\u8E2A", link: "/guide/m05-strategies/5.4-cta" },
      { text: "5.5 \u4E8B\u4EF6\u9A71\u52A8\u7B56\u7565", link: "/guide/m05-strategies/5.5-event-driven" },
      { text: "5.6 \u591A\u56E0\u5B50\u7EC4\u5408\u4E0E\u62E9\u65F6", link: "/guide/m05-strategies/5.6-multi-factor" }
    ]
  },
  {
    text: "\u6A21\u5757\u516D\uFF1A\u6295\u8D44\u7EC4\u5408\u7BA1\u7406\u4E0E\u4F18\u5316",
    collapsed: true,
    items: [
      { text: "6.1 \u5747\u503C-\u65B9\u5DEE\u4F18\u5316", link: "/guide/m06-portfolio/6.1-mvo" },
      { text: "6.2 \u98CE\u9669\u5E73\u4EF7\u4E0E\u5206\u6563\u5EA6", link: "/guide/m06-portfolio/6.2-risk-parity" },
      { text: "6.3 \u52A8\u6001\u6743\u91CD\u7BA1\u7406", link: "/guide/m06-portfolio/6.3-kelly" },
      { text: "6.4 \u7EA6\u675F\u5904\u7406", link: "/guide/m06-portfolio/6.4-constraints" },
      { text: "6.5 \u538B\u529B\u6D4B\u8BD5\u4E0EVaR", link: "/guide/m06-portfolio/6.5-var" }
    ]
  },
  {
    text: "\u6A21\u5757\u4E03\uFF1A\u6267\u884C\u7B97\u6CD5\u4E0E\u5FAE\u89C2\u7ED3\u6784",
    collapsed: true,
    items: [
      { text: "7.1 \u8BA2\u5355\u7C7B\u578B\u4E0E\u98CE\u9669", link: "/guide/m07-execution/7.1-order-types" },
      { text: "7.2 \u7B97\u6CD5\u6267\u884C\u539F\u7406", link: "/guide/m07-execution/7.2-algo-execution" },
      { text: "7.3 \u505A\u5E02\u7B56\u7565\u601D\u60F3", link: "/guide/m07-execution/7.3-market-making" },
      { text: "7.4 \u9AD8\u9891\u4EA4\u6613\u7B80\u4ECB", link: "/guide/m07-execution/7.4-hft" },
      { text: "7.5 \u6267\u884C\u6210\u672C\u5206\u6790", link: "/guide/m07-execution/7.5-tca" }
    ]
  },
  {
    text: "\u6A21\u5757\u516B\uFF1A\u673A\u5668\u5B66\u4E60\u4E0E\u53E6\u7C7B\u6570\u636E",
    collapsed: true,
    items: [
      { text: "8.1 \u76D1\u7763\u5B66\u4E60\u9009\u80A1", link: "/guide/m08-ml-alt-data/8.1-supervised" },
      { text: "8.2 \u65E0\u76D1\u7763\u4E0E\u964D\u7EF4", link: "/guide/m08-ml-alt-data/8.2-unsupervised" },
      { text: "8.3 NLP\u5E94\u7528", link: "/guide/m08-ml-alt-data/8.3-nlp" },
      { text: "8.4 \u53E6\u7C7B\u6570\u636E", link: "/guide/m08-ml-alt-data/8.4-alt-data" },
      { text: "8.5 \u8FC7\u62DF\u5408\u9632\u5FA1", link: "/guide/m08-ml-alt-data/8.5-overfitting" }
    ]
  },
  {
    text: "\u6A21\u5757\u4E5D\uFF1A\u5B9E\u76D8\u90E8\u7F72\u4E0E\u7CFB\u7EDF\u67B6\u6784",
    collapsed: true,
    items: [
      { text: "9.1 \u91CF\u5316\u7CFB\u7EDF\u8BBE\u8BA1", link: "/guide/m09-live-trading/9.1-system-design" },
      { text: "9.2 \u5B9E\u65F6\u6570\u636E\u7BA1\u9053", link: "/guide/m09-live-trading/9.2-data-pipeline" },
      { text: "9.3 \u6A21\u62DF\u4E0E\u5B9E\u76D8\u5BF9\u63A5", link: "/guide/m09-live-trading/9.3-broker-api" },
      { text: "9.4 \u7B56\u7565\u76D1\u63A7\u4E0E\u8FD0\u7EF4", link: "/guide/m09-live-trading/9.4-monitoring" },
      { text: "9.5 \u5408\u89C4\u4E0E\u76D1\u7BA1", link: "/guide/m09-live-trading/9.5-compliance" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\uFF1A\u524D\u6CBF\u4E13\u9898\u4E0E\u804C\u4E1A\u6210\u957F",
    collapsed: true,
    items: [
      { text: "10.1 \u5F3A\u5316\u5B66\u4E60\u4EA4\u6613", link: "/guide/m10-frontier/10.1-rl" },
      { text: "10.2 \u751F\u6210\u5F0FAI", link: "/guide/m10-frontier/10.2-gen-ai" },
      { text: "10.3 \u6697\u6C60", link: "/guide/m10-frontier/10.3-dark-pool" },
      { text: "10.4 \u56E2\u961F\u5206\u5DE5", link: "/guide/m10-frontier/10.4-career" },
      { text: "10.5 \u7EC8\u6781\u9879\u76EE", link: "/guide/m10-frontier/10.5-final-project" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u4E00\uFF1A\u671F\u6743\u4E0E\u884D\u751F\u54C1\u5B9A\u4EF7\u8FDB\u9636",
    collapsed: true,
    items: [
      { text: "11.1 \u671F\u6743 Greeks \u8BE6\u89E3", link: "/guide/m11-derivatives/11.1-greeks" },
      { text: "11.2 \u6CE2\u52A8\u7387\u66F2\u9762\u4E0E\u5957\u5229", link: "/guide/m11-derivatives/11.2-vol-surface" },
      { text: "11.3 \u5947\u5F02\u671F\u6743\u4E0E\u7ED3\u6784\u5316\u4EA7\u54C1", link: "/guide/m11-derivatives/11.3-exotic-options" },
      { text: "11.4 \u4E8C\u53C9\u6811\u4E0E\u6709\u9650\u5DEE\u5206\u6CD5", link: "/guide/m11-derivatives/11.4-tree-fdm" },
      { text: "11.5 \u8499\u7279\u5361\u6D1B\u5B9A\u4EF7\u8FDB\u9636", link: "/guide/m11-derivatives/11.5-mc-pricing" },
      { text: "11.6 \u671F\u6743\u5E02\u573A\u57FA\u7840", link: "/guide/m11-derivatives/11.6-options-market" },
      { text: "11.7 \u9690\u542B\u6CE2\u52A8\u7387 vs \u5386\u53F2\u6CE2\u52A8\u7387", link: "/guide/m11-derivatives/11.7-iv-vs-hv" },
      { text: "11.8 \u6CE2\u52A8\u7387\u4EA4\u6613\u7B56\u7565", link: "/guide/m11-derivatives/11.8-vol-trading" },
      { text: "11.9 \u5957\u4FDD\u7B56\u7565\u5B9E\u6218", link: "/guide/m11-derivatives/11.9-hedging-practice" },
      { text: "11.10 \u573A\u5185\u671F\u6743\u7B56\u7565\u4E2D\u56FD A \u80A1", link: "/guide/m11-derivatives/11.10-china-listed-options" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u4E8C\uFF1A\u56FA\u5B9A\u6536\u76CA\u91CF\u5316",
    collapsed: true,
    items: [
      { text: "12.1 \u6536\u76CA\u7387\u66F2\u7EBF\u5EFA\u6A21", link: "/guide/m12-fixed-income/12.1-yield-curve" },
      { text: "12.2 \u4E45\u671F\u4E0E\u51F8\u5EA6\u514D\u75AB", link: "/guide/m12-fixed-income/12.2-duration-convexity" },
      { text: "12.3 \u5229\u7387\u4E92\u6362\u4E0E\u4E92\u6362\u671F\u6743", link: "/guide/m12-fixed-income/12.3-irs-swaption" },
      { text: "12.4 \u4FE1\u7528\u5229\u5DEE\u4E0ECDS", link: "/guide/m12-fixed-income/12.4-credit-spread" },
      { text: "12.5 MBS\u4E0E\u8D44\u4EA7\u8BC1\u5238\u5316", link: "/guide/m12-fixed-income/12.5-mbs" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u4E09\uFF1A\u52A0\u5BC6\u8D27\u5E01\u91CF\u5316",
    collapsed: true,
    items: [
      { text: "13.1 \u94FE\u4E0A\u6570\u636E\u5206\u6790", link: "/guide/m13-crypto/13.1-onchain" },
      { text: "13.2 \u8D44\u91D1\u8D39\u7387\u4E0E\u5957\u5229", link: "/guide/m13-crypto/13.2-funding-rate" },
      { text: "13.3 MEV\u4E0E\u4EA4\u6613\u6392\u5E8F", link: "/guide/m13-crypto/13.3-mev" },
      { text: "13.4 DEX\u6D41\u52A8\u6027\u505A\u5E02", link: "/guide/m13-crypto/13.4-dex-mm" },
      { text: "13.5 \u6C38\u7EED\u5408\u7EA6\u7B56\u7565", link: "/guide/m13-crypto/13.5-perps" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u56DB\uFF1A\u5E02\u573A\u5FAE\u89C2\u7ED3\u6784\u6DF1\u5EA6",
    collapsed: true,
    items: [
      { text: "14.1 \u8BA2\u5355\u6D41\u6BD2\u6027\u6A21\u578B", link: "/guide/m14-microstructure-deep/14.1-toxicity" },
      { text: "14.2 Kyle\u4E0EGlosten-Milgrom", link: "/guide/m14-microstructure-deep/14.2-information-models" },
      { text: "14.3 \u6700\u4F18\u6267\u884C\u7406\u8BBA", link: "/guide/m14-microstructure-deep/14.3-optimal-execution" },
      { text: "14.4 \u9650\u4EF7\u8BA2\u5355\u7C3F\u52A8\u529B\u5B66", link: "/guide/m14-microstructure-deep/14.4-lob-dynamics" },
      { text: "14.5 \u9AD8\u9891\u505A\u5E02\u7B56\u7565\u8FDB\u9636", link: "/guide/m14-microstructure-deep/14.5-hft-mm-advanced" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u4E94\uFF1A\u5B8F\u89C2\u7ECF\u6D4E\u91CF\u5316",
    collapsed: true,
    items: [
      { text: "15.1 \u5B8F\u89C2\u56E0\u5B50\u6A21\u578B", link: "/guide/m15-macro/15.1-macro-factors" },
      { text: "15.2 \u7F8E\u8054\u50A8\u653F\u7B56\u91CF\u5316", link: "/guide/m15-macro/15.2-fed-policy" },
      { text: "15.3 \u901A\u80C0\u9884\u671F\u5EFA\u6A21", link: "/guide/m15-macro/15.3-inflation" },
      { text: "15.4 \u7ECF\u6D4E\u5468\u671F\u62E9\u65F6", link: "/guide/m15-macro/15.4-cycle-timing" },
      { text: "15.5 \u8DE8\u8D44\u4EA7\u5B8F\u89C2\u7B56\u7565", link: "/guide/m15-macro/15.5-cross-asset" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u516D\uFF1A\u98CE\u9669\u7BA1\u7406\u4F53\u7CFB",
    collapsed: true,
    items: [
      { text: "16.1 \u98CE\u9669\u5206\u89E3\u4E0E\u5F52\u56E0", link: "/guide/m16-risk-management/16.1-risk-decomposition" },
      { text: "16.2 \u6781\u503C\u7406\u8BBA\u4E0E\u5C3E\u90E8\u98CE\u9669", link: "/guide/m16-risk-management/16.2-evt-tail" },
      { text: "16.3 \u538B\u529B\u6D4B\u8BD5\u4E0E\u60C5\u666F\u5206\u6790", link: "/guide/m16-risk-management/16.3-stress-testing" },
      { text: "16.4 \u5DF4\u585E\u5C14\u534F\u8BAE\u4E0E\u76D1\u7BA1\u8D44\u672C", link: "/guide/m16-risk-management/16.4-basel" },
      { text: "16.5 \u5C3E\u90E8\u5BF9\u51B2\u7B56\u7565", link: "/guide/m16-risk-management/16.5-tail-hedge" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u4E03\uFF1A\u91CF\u5316\u6570\u636E\u5DE5\u7A0B",
    collapsed: true,
    items: [
      { text: "17.1 Tick\u6570\u636E\u5E93\u8BBE\u8BA1", link: "/guide/m17-data-engineering/17.1-tick-db" },
      { text: "17.2 \u5B9E\u65F6ETL\u7BA1\u9053", link: "/guide/m17-data-engineering/17.2-realtime-etl" },
      { text: "17.3 \u6570\u636E\u8D28\u91CF\u76D1\u63A7", link: "/guide/m17-data-engineering/17.3-data-quality" },
      { text: "17.4 \u6279\u5904\u7406\u4E0E\u6D41\u5904\u7406", link: "/guide/m17-data-engineering/17.4-batch-streaming" },
      { text: "17.5 \u7279\u5F81\u5B58\u50A8(Feature Store)", link: "/guide/m17-data-engineering/17.5-feature-store" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u516B\uFF1A\u7B56\u7565\u751F\u547D\u5468\u671F\u7BA1\u7406",
    collapsed: true,
    items: [
      { text: "18.1 \u7B56\u7565\u5B75\u5316\u4E0E\u8BC4\u5BA1", link: "/guide/m18-strategy-lifecycle/18.1-incubation" },
      { text: "18.2 \u6A21\u62DF\u76D8\u4E0E\u5B9E\u76D8\u8FC7\u6E21", link: "/guide/m18-strategy-lifecycle/18.2-paper-to-live" },
      { text: "18.3 A/B\u6D4B\u8BD5\u4E0E\u91D1\u4E1D\u96C0\u53D1\u5E03", link: "/guide/m18-strategy-lifecycle/18.3-ab-testing" },
      { text: "18.4 \u7B56\u7565\u7EE9\u6548\u5F52\u56E0", link: "/guide/m18-strategy-lifecycle/18.4-attribution" },
      { text: "18.5 \u7B56\u7565\u9000\u5F79\u4E0E\u590D\u76D8", link: "/guide/m18-strategy-lifecycle/18.5-retirement" }
    ]
  },
  {
    text: "\u6A21\u5757\u5341\u4E5D\uFF1A\u4E2D\u56FDA\u80A1\u7279\u8272\u91CF\u5316",
    collapsed: true,
    items: [
      { text: "19.1 \u6DA8\u8DCC\u505C\u677F\u7B56\u7565", link: "/guide/m19-a-share/19.1-limit-up" },
      { text: "19.2 \u6253\u65B0\u7B56\u7565\u5206\u6790", link: "/guide/m19-a-share/19.2-ipo" },
      { text: "19.3 \u884C\u4E1A\u8F6E\u52A8\u6A21\u578B", link: "/guide/m19-a-share/19.3-sector-rotation" },
      { text: "19.4 \u5317\u5411\u8D44\u91D1\u4E0E\u9F99\u864E\u699C", link: "/guide/m19-a-share/19.4-northbound" },
      { text: "19.5 \u653F\u7B56\u56E0\u5B50\u4E0E\u4E8B\u4EF6\u9A71\u52A8", link: "/guide/m19-a-share/19.5-policy-events" }
    ]
  },
  {
    text: "\u6A21\u5757\u4E8C\u5341\uFF1A\u91CF\u5316\u9762\u8BD5\u51C6\u5907",
    collapsed: true,
    items: [
      { text: "20.1 \u6570\u5B66\u4E0E\u7EDF\u8BA1\u9762\u8BD5\u9898", link: "/guide/m20-interview-prep/20.1-math-stats" },
      { text: "20.2 \u7F16\u7A0B\u4E0E\u7B97\u6CD5\u9898", link: "/guide/m20-interview-prep/20.2-coding" },
      { text: "20.3 \u91D1\u878D\u4E0E\u7B56\u7565\u9898", link: "/guide/m20-interview-prep/20.3-finance" },
      { text: "20.4 \u8111\u7B4B\u6025\u8F6C\u5F2F\u4E0E\u884C\u4E3A\u9762", link: "/guide/m20-interview-prep/20.4-brain-teasers" },
      { text: "20.5 \u6A21\u62DF\u9762\u8BD5\u4E0E\u590D\u76D8", link: "/guide/m20-interview-prep/20.5-mock-interview" },
      { text: "20.6 \u9AD8\u9891\u9762\u8BD5\u9898(\u4E2D\u5916\u673A\u6784)", link: "/guide/m20-interview-prep/20.6-real-interviews" },
      { text: "20.7 C++ \u91CF\u5316\u9762\u8BD5\u4E13\u9898", link: "/guide/m20-interview-prep/20.7-cpp-quant" },
      { text: "20.8 Research \u9879\u76EE\u5305\u88C5", link: "/guide/m20-interview-prep/20.8-resume-portfolio" }
    ]
  }
];
var config_default = defineConfig({
  title: "QuantLab \xB7 \u91CF\u5316\u4EA4\u6613\u7CFB\u7EDF\u8BBE\u8BA1\u4E0E\u5B9E\u8DF5",
  description: "FinTech \u98CE\u683C\u7684\u91CF\u5316\u4EA4\u6613\u5B66\u4E60\u5E73\u53F0 \xB7 10 \u5927\u6A21\u5757 \xB7 50+ \u7AE0\u8282 \xB7 9 \u4E2A\u4EA4\u4E92\u5F0F\u8BA1\u7B97\u5668",
  lang: "zh-CN",
  appearance: true,
  head: [
    ["link", { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" }],
    ["meta", { name: "theme-color", content: "#00E5A0" }],
    ["meta", { name: "description", content: "FinTech \u98CE\u683C\u7684\u91CF\u5316\u4EA4\u6613\u5B66\u4E60\u5E73\u53F0" }],
    // 优先使用本地 Pyodide（位于 /pyodide/pyodide.js，由 public/pyodide/ 静态发布）
    // 在线时浏览器仍可通过下方 CDN 兜底（如果本地缺失）
    ["script", { src: "/pyodide/pyodide.js" }]
  ],
  themeConfig: {
    sidebar,
    nav: [
      { text: "\u8BFE\u7A0B\u9996\u9875", link: "/" },
      { text: "\u6A21\u5757\u6982\u89C8", link: "/guide/" }
    ],
    search: {
      provider: "local",
      options: {
        translations: {
          button: { buttonText: "\u641C\u7D22", buttonAriaLabel: "\u641C\u7D22\u6587\u6863" },
          modal: { noResultsText: "\u65E0\u7ED3\u679C", resetButtonTitle: "\u6E05\u9664", displayDetails: "\u663E\u793A\u8BE6\u60C5", footer: { selectText: "\u9009\u62E9", closeText: "\u5173\u95ED" } }
        }
      }
    },
    docFooter: { prev: "\u4E0A\u4E00\u7AE0", next: "\u4E0B\u4E00\u7AE0" },
    darkModeSwitchLabel: "\u4E3B\u9898\u5207\u6362",
    sidebarMenuLabel: "\u83DC\u5355",
    returnToTopLabel: "\u56DE\u5230\u9876\u90E8",
    outline: { label: "\u672C\u9875\u76EE\u5F55" }
  },
  markdown: {
    math: true
  },
  ignoreDeadLinks: true,
  // 便携版输出位置（避免与 .vitepress/dist 的 safe-delete 冲突）
  outDir: process.env.QPORTABLE ? "portable/dist" : ".vitepress/dist"
});
export {
  config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsiLnZpdGVwcmVzcy9jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxBSVxcXFxzdHVkeVxcXFxxdWFudFxcXFwudml0ZXByZXNzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJEOlxcXFxBSVxcXFxzdHVkeVxcXFxxdWFudFxcXFwudml0ZXByZXNzXFxcXGNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovQUkvc3R1ZHkvcXVhbnQvLnZpdGVwcmVzcy9jb25maWcudHNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlcHJlc3MnXG5cbmNvbnN0IHNpZGViYXIgPSBbXG4gICAge1xuICAgICAgdGV4dDogJ1x1NkEyMVx1NTc1N1x1NEUwMFx1RkYxQVx1OTFDRlx1NTMxNlx1NEVBNFx1NjYxM1x1NTE2OFx1NjY2Rlx1NEUwRVx1ODg0Q1x1NEUxQVx1OEJBNFx1NzdFNScsXG4gICAgICBjb2xsYXBzZWQ6IGZhbHNlLFxuICAgICAgaXRlbXM6IFtcbiAgICAgICAgeyB0ZXh0OiAnMS4xIFx1NTNEMVx1NUM1NVx1NTNGMlx1NEUwRVx1NzUxRlx1NjAwMScsIGxpbms6ICcvZ3VpZGUvbTAxLW92ZXJ2aWV3LzEuMS1oaXN0b3J5JyB9LFxuICAgICAgICB7IHRleHQ6ICcxLjIgXHU3QjU2XHU3NTY1XHU1MjA2XHU3QzdCJywgbGluazogJy9ndWlkZS9tMDEtb3ZlcnZpZXcvMS4yLXN0cmF0ZWd5LXR5cGVzJyB9LFxuICAgICAgICB7IHRleHQ6ICcxLjMgXHU5MUNGXHU1MzE2XHU2MDFEXHU3RUY0XHU2ODM4XHU1RkMzJywgbGluazogJy9ndWlkZS9tMDEtb3ZlcnZpZXcvMS4zLXF1YW50LW1pbmRzZXQnIH0sXG4gICAgICAgIHsgdGV4dDogJzEuNCBcdTczQjBcdTVCOUVcdTYzMTFcdTYyMTgnLCBsaW5rOiAnL2d1aWRlL20wMS1vdmVydmlldy8xLjQtY2hhbGxlbmdlcycgfSxcbiAgICAgICAgeyB0ZXh0OiAnMS41IFx1ODg0Q1x1NEUxQVx1NjgzQ1x1NUM0MCAyMDI0LTIwMjYnLCBsaW5rOiAnL2d1aWRlL20wMS1vdmVydmlldy8xLjUtaW5kdXN0cnktMjAyNicgfSxcbiAgICAgICAgeyB0ZXh0OiAnMS42IFx1NUM5N1x1NEY0RFx1NTZGRVx1OEMzMVx1NEUwRVx1ODBGRFx1NTI5Qlx1NkEyMVx1NTc4QicsIGxpbms6ICcvZ3VpZGUvbTAxLW92ZXJ2aWV3LzEuNi1jYXJlZXItbWFwJyB9LFxuICAgICAgICB7IHRleHQ6ICcxLjcgXHU1QjY2XHU0RTYwXHU4REVGXHU1Rjg0XHU0RTBFXHU1NzUxXHU3MEI5JywgbGluazogJy9ndWlkZS9tMDEtb3ZlcnZpZXcvMS43LWxlYXJuaW5nLXJvYWRtYXAnIH0sXG4gICAgICBdXG4gICAgfSxcbiAge1xuICAgIHRleHQ6ICdcdTZBMjFcdTU3NTdcdTRFOENcdUZGMUFcdTkxRDFcdTg3OERcdTU3RkFcdTc4NDBcdTRFMEVcdTY1NzBcdTc0MDZcdTVERTVcdTUxNzcnLFxuICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICBpdGVtczogW1xuICAgICAgeyB0ZXh0OiAnMi4xIFx1NUUwMlx1NTczQVx1NUZBRVx1ODlDMlx1N0VEM1x1Njc4NCcsIGxpbms6ICcvZ3VpZGUvbTAyLWZpbmFuY2UtbWF0aC8yLjEtbWljcm9zdHJ1Y3R1cmUnIH0sXG4gICAgICB7IHRleHQ6ICcyLjIgXHU4RDQ0XHU0RUE3XHU1QjlBXHU0RUY3XHU1N0ZBXHU3ODQwJywgbGluazogJy9ndWlkZS9tMDItZmluYW5jZS1tYXRoLzIuMi1hc3NldC1wcmljaW5nJyB9LFxuICAgICAgeyB0ZXh0OiAnMi4zIFx1Njk4Mlx1NzM4N1x1N0VERlx1OEJBMVx1NEUwRVx1NzZGOFx1NTE3M1x1NjAyNycsIGxpbms6ICcvZ3VpZGUvbTAyLWZpbmFuY2UtbWF0aC8yLjMtcHJvYi1zdGF0cycgfSxcbiAgICAgIHsgdGV4dDogJzIuNCBcdTY1RjZcdTk1RjRcdTVFOEZcdTUyMTdcdTUyMDZcdTY3OTAnLCBsaW5rOiAnL2d1aWRlL20wMi1maW5hbmNlLW1hdGgvMi40LXRpbWUtc2VyaWVzJyB9LFxuICAgICAgeyB0ZXh0OiAnMi41IFx1N0VCRlx1NjAyN1x1NkEyMVx1NTc4Qlx1NEUwRVx1NkI2M1x1NTIxOVx1NTMxNicsIGxpbms6ICcvZ3VpZGUvbTAyLWZpbmFuY2UtbWF0aC8yLjUtbGluZWFyLW1vZGVscycgfSxcbiAgICBdXG4gIH0sXG4gIHtcbiAgICB0ZXh0OiAnXHU2QTIxXHU1NzU3XHU0RTA5XHVGRjFBUHl0aG9uIFx1OTFDRlx1NTMxNlx1N0YxNlx1N0EwQlx1NEUwRVx1NjU3MFx1NjM2RVx1NURFNVx1N0EwQicsXG4gICAgY29sbGFwc2VkOiB0cnVlLFxuICAgIGl0ZW1zOiBbXG4gICAgICB7IHRleHQ6ICczLjEgUHl0aG9uXHU2NTcwXHU2MzZFXHU2ODA4JywgbGluazogJy9ndWlkZS9tMDMtcHl0aG9uLWRhdGEvMy4xLXB5dGhvbi1zdGFjaycgfSxcbiAgICAgIHsgdGV4dDogJzMuMiBcdTY1NzBcdTYzNkVcdTgzQjdcdTUzRDZcdTRFMEVcdTZFMDVcdTZEMTcnLCBsaW5rOiAnL2d1aWRlL20wMy1weXRob24tZGF0YS8zLjItZGF0YS1jbGVhbmluZycgfSxcbiAgICAgIHsgdGV4dDogJzMuMyBcdTYwMjdcdTgwRkRcdTRGMThcdTUzMTYnLCBsaW5rOiAnL2d1aWRlL20wMy1weXRob24tZGF0YS8zLjMtcGVyZm9ybWFuY2UnIH0sXG4gICAgICB7IHRleHQ6ICczLjQgXHU5MUQxXHU4NzhEXHU2NTcwXHU2MzZFXHU3Mjc5XHU4MjcyXHU1OTA0XHU3NDA2JywgbGluazogJy9ndWlkZS9tMDMtcHl0aG9uLWRhdGEvMy40LWZpbi1kYXRhJyB9LFxuICAgICAgeyB0ZXh0OiAnMy41IFx1NTNFRlx1ODlDNlx1NTMxNlx1NEUwRVx1NjNBMlx1N0QyMicsIGxpbms6ICcvZ3VpZGUvbTAzLXB5dGhvbi1kYXRhLzMuNS12aXN1YWxpemF0aW9uJyB9LFxuICAgIF1cbiAgfSxcbiAge1xuICAgIHRleHQ6ICdcdTZBMjFcdTU3NTdcdTU2REJcdUZGMUFcdTU2REVcdTZENEJcdTY4NDZcdTY3QjZcdTRFMEVcdTdFRTlcdTY1NDhcdThCQzRcdTRGMzAnLFxuICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICBpdGVtczogW1xuICAgICAgeyB0ZXh0OiAnNC4xIFx1NTZERVx1NkQ0Qlx1NUYxNVx1NjRDRVx1NTM5Rlx1NzQwNicsIGxpbms6ICcvZ3VpZGUvbTA0LWJhY2t0ZXN0LzQuMS1lbmdpbmUnIH0sXG4gICAgICB7IHRleHQ6ICc0LjIgXHU0RUE0XHU2NjEzXHU2MjEwXHU2NzJDXHU1RUZBXHU2QTIxJywgbGluazogJy9ndWlkZS9tMDQtYmFja3Rlc3QvNC4yLWNvc3QtbW9kZWwnIH0sXG4gICAgICB7IHRleHQ6ICc0LjMgXHU3RUU5XHU2NTQ4XHU2MzA3XHU2ODA3XHU1MTY4XHU2NjZGJywgbGluazogJy9ndWlkZS9tMDQtYmFja3Rlc3QvNC4zLW1ldHJpY3MnIH0sXG4gICAgICB7IHRleHQ6ICc0LjQgXHU1NkRFXHU2RDRCXHU5Njc3XHU5NjMxXHU0RTBFXHU1QkY5XHU3QjU2JywgbGluazogJy9ndWlkZS9tMDQtYmFja3Rlc3QvNC40LXBpdGZhbGxzJyB9LFxuICAgICAgeyB0ZXh0OiAnNC41IFx1N0VERlx1OEJBMVx1NjhDMFx1OUE4QycsIGxpbms6ICcvZ3VpZGUvbTA0LWJhY2t0ZXN0LzQuNS1zdGF0LXRlc3RzJyB9LFxuICAgICAgeyB0ZXh0OiAnNC42IFx1NEUzQlx1NkQ0MVx1NTZERVx1NkQ0Qlx1Njg0Nlx1NjdCNlx1NkEyQVx1OEJDNCcsIGxpbms6ICcvZ3VpZGUvbTA0LWJhY2t0ZXN0LzQuNi1mcmFtZXdvcmtzLWNvbXBhcmlzb24nIH0sXG4gICAgICB7IHRleHQ6ICc0LjcgXHU1QjhDXHU2NTc0XHU0RThCXHU0RUY2XHU5QTcxXHU1MkE4XHU1NkRFXHU2RDRCXHU1QjlFXHU2MjE4JywgbGluazogJy9ndWlkZS9tMDQtYmFja3Rlc3QvNC43LWV2ZW50LWRyaXZlbi1mdWxsJyB9LFxuICAgICAgeyB0ZXh0OiAnNC44IFx1NTQwOFx1NjIxMFx1NjU3MFx1NjM2RVx1NTZERVx1NkQ0QicsIGxpbms6ICcvZ3VpZGUvbTA0LWJhY2t0ZXN0LzQuOC1zeW50aGV0aWMtZGF0YScgfSxcbiAgICAgIHsgdGV4dDogJzQuOSBcdTU5MUFcdTdCNTZcdTc1NjVcdTdFQzRcdTU0MDhcdTU2REVcdTZENEInLCBsaW5rOiAnL2d1aWRlL20wNC1iYWNrdGVzdC80LjktbXVsdGktc3RyYXRlZ3knIH0sXG4gICAgICB7IHRleHQ6ICc0LjEwIFdhbGstRm9yd2FyZCBcdTZFREFcdTUyQThcdTU2REVcdTZENEInLCBsaW5rOiAnL2d1aWRlL20wNC1iYWNrdGVzdC80LjEwLXdhbGstZm9yd2FyZCcgfSxcbiAgICBdXG4gIH0sXG4gIHtcbiAgICB0ZXh0OiAnXHU2QTIxXHU1NzU3XHU0RTk0XHVGRjFBXHU3QjU2XHU3NTY1XHU1RjAwXHU1M0QxXHU1REU1XHU1NzRBJyxcbiAgICBjb2xsYXBzZWQ6IHRydWUsXG4gICAgaXRlbXM6IFtcbiAgICAgIHsgdGV4dDogJzUuMSBcdTU2RTBcdTVCNTBcdTYyOTVcdThENDRcdTRGNTNcdTdDRkInLCBsaW5rOiAnL2d1aWRlL20wNS1zdHJhdGVnaWVzLzUuMS1mYWN0b3JzJyB9LFxuICAgICAgeyB0ZXh0OiAnNS4yIFx1NTNDQ1x1NTc0N1x1N0VCRlx1N0I1Nlx1NzU2NVx1NkEyMVx1NjJERicsIGxpbms6ICcvZ3VpZGUvbTA1LXN0cmF0ZWdpZXMvNS4yLWR1YWwtbWEnIH0sXG4gICAgICB7IHRleHQ6ICc1LjMgXHU3RURGXHU4QkExXHU1OTU3XHU1MjI5JywgbGluazogJy9ndWlkZS9tMDUtc3RyYXRlZ2llcy81LjMtc3RhdC1hcmInIH0sXG4gICAgICB7IHRleHQ6ICc1LjQgQ1RBXHU4RDhCXHU1MkJGXHU4RERGXHU4RTJBJywgbGluazogJy9ndWlkZS9tMDUtc3RyYXRlZ2llcy81LjQtY3RhJyB9LFxuICAgICAgeyB0ZXh0OiAnNS41IFx1NEU4Qlx1NEVGNlx1OUE3MVx1NTJBOFx1N0I1Nlx1NzU2NScsIGxpbms6ICcvZ3VpZGUvbTA1LXN0cmF0ZWdpZXMvNS41LWV2ZW50LWRyaXZlbicgfSxcbiAgICAgIHsgdGV4dDogJzUuNiBcdTU5MUFcdTU2RTBcdTVCNTBcdTdFQzRcdTU0MDhcdTRFMEVcdTYyRTlcdTY1RjYnLCBsaW5rOiAnL2d1aWRlL20wNS1zdHJhdGVnaWVzLzUuNi1tdWx0aS1mYWN0b3InIH0sXG4gICAgXVxuICB9LFxuICB7XG4gICAgdGV4dDogJ1x1NkEyMVx1NTc1N1x1NTE2RFx1RkYxQVx1NjI5NVx1OEQ0NFx1N0VDNFx1NTQwOFx1N0JBMVx1NzQwNlx1NEUwRVx1NEYxOFx1NTMxNicsXG4gICAgY29sbGFwc2VkOiB0cnVlLFxuICAgIGl0ZW1zOiBbXG4gICAgICB7IHRleHQ6ICc2LjEgXHU1NzQ3XHU1MDNDLVx1NjVCOVx1NURFRVx1NEYxOFx1NTMxNicsIGxpbms6ICcvZ3VpZGUvbTA2LXBvcnRmb2xpby82LjEtbXZvJyB9LFxuICAgICAgeyB0ZXh0OiAnNi4yIFx1OThDRVx1OTY2OVx1NUU3M1x1NEVGN1x1NEUwRVx1NTIwNlx1NjU2M1x1NUVBNicsIGxpbms6ICcvZ3VpZGUvbTA2LXBvcnRmb2xpby82LjItcmlzay1wYXJpdHknIH0sXG4gICAgICB7IHRleHQ6ICc2LjMgXHU1MkE4XHU2MDAxXHU2NzQzXHU5MUNEXHU3QkExXHU3NDA2JywgbGluazogJy9ndWlkZS9tMDYtcG9ydGZvbGlvLzYuMy1rZWxseScgfSxcbiAgICAgIHsgdGV4dDogJzYuNCBcdTdFQTZcdTY3NUZcdTU5MDRcdTc0MDYnLCBsaW5rOiAnL2d1aWRlL20wNi1wb3J0Zm9saW8vNi40LWNvbnN0cmFpbnRzJyB9LFxuICAgICAgeyB0ZXh0OiAnNi41IFx1NTM4Qlx1NTI5Qlx1NkQ0Qlx1OEJENVx1NEUwRVZhUicsIGxpbms6ICcvZ3VpZGUvbTA2LXBvcnRmb2xpby82LjUtdmFyJyB9LFxuICAgIF1cbiAgfSxcbiAge1xuICAgIHRleHQ6ICdcdTZBMjFcdTU3NTdcdTRFMDNcdUZGMUFcdTYyNjdcdTg4NENcdTdCOTdcdTZDRDVcdTRFMEVcdTVGQUVcdTg5QzJcdTdFRDNcdTY3ODQnLFxuICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICBpdGVtczogW1xuICAgICAgeyB0ZXh0OiAnNy4xIFx1OEJBMlx1NTM1NVx1N0M3Qlx1NTc4Qlx1NEUwRVx1OThDRVx1OTY2OScsIGxpbms6ICcvZ3VpZGUvbTA3LWV4ZWN1dGlvbi83LjEtb3JkZXItdHlwZXMnIH0sXG4gICAgICB7IHRleHQ6ICc3LjIgXHU3Qjk3XHU2Q0Q1XHU2MjY3XHU4ODRDXHU1MzlGXHU3NDA2JywgbGluazogJy9ndWlkZS9tMDctZXhlY3V0aW9uLzcuMi1hbGdvLWV4ZWN1dGlvbicgfSxcbiAgICAgIHsgdGV4dDogJzcuMyBcdTUwNUFcdTVFMDJcdTdCNTZcdTc1NjVcdTYwMURcdTYwRjMnLCBsaW5rOiAnL2d1aWRlL20wNy1leGVjdXRpb24vNy4zLW1hcmtldC1tYWtpbmcnIH0sXG4gICAgICB7IHRleHQ6ICc3LjQgXHU5QUQ4XHU5ODkxXHU0RUE0XHU2NjEzXHU3QjgwXHU0RUNCJywgbGluazogJy9ndWlkZS9tMDctZXhlY3V0aW9uLzcuNC1oZnQnIH0sXG4gICAgICB7IHRleHQ6ICc3LjUgXHU2MjY3XHU4ODRDXHU2MjEwXHU2NzJDXHU1MjA2XHU2NzkwJywgbGluazogJy9ndWlkZS9tMDctZXhlY3V0aW9uLzcuNS10Y2EnIH0sXG4gICAgXVxuICB9LFxuICB7XG4gICAgdGV4dDogJ1x1NkEyMVx1NTc1N1x1NTE2Qlx1RkYxQVx1NjczQVx1NTY2OFx1NUI2Nlx1NEU2MFx1NEUwRVx1NTNFNlx1N0M3Qlx1NjU3MFx1NjM2RScsXG4gICAgY29sbGFwc2VkOiB0cnVlLFxuICAgIGl0ZW1zOiBbXG4gICAgICB7IHRleHQ6ICc4LjEgXHU3NkQxXHU3NzYzXHU1QjY2XHU0RTYwXHU5MDA5XHU4MEExJywgbGluazogJy9ndWlkZS9tMDgtbWwtYWx0LWRhdGEvOC4xLXN1cGVydmlzZWQnIH0sXG4gICAgICB7IHRleHQ6ICc4LjIgXHU2NUUwXHU3NkQxXHU3NzYzXHU0RTBFXHU5NjREXHU3RUY0JywgbGluazogJy9ndWlkZS9tMDgtbWwtYWx0LWRhdGEvOC4yLXVuc3VwZXJ2aXNlZCcgfSxcbiAgICAgIHsgdGV4dDogJzguMyBOTFBcdTVFOTRcdTc1MjgnLCBsaW5rOiAnL2d1aWRlL20wOC1tbC1hbHQtZGF0YS84LjMtbmxwJyB9LFxuICAgICAgeyB0ZXh0OiAnOC40IFx1NTNFNlx1N0M3Qlx1NjU3MFx1NjM2RScsIGxpbms6ICcvZ3VpZGUvbTA4LW1sLWFsdC1kYXRhLzguNC1hbHQtZGF0YScgfSxcbiAgICAgIHsgdGV4dDogJzguNSBcdThGQzdcdTYyREZcdTU0MDhcdTk2MzJcdTVGQTEnLCBsaW5rOiAnL2d1aWRlL20wOC1tbC1hbHQtZGF0YS84LjUtb3ZlcmZpdHRpbmcnIH0sXG4gICAgXVxuICB9LFxuICB7XG4gICAgdGV4dDogJ1x1NkEyMVx1NTc1N1x1NEU1RFx1RkYxQVx1NUI5RVx1NzZEOFx1OTBFOFx1N0Y3Mlx1NEUwRVx1N0NGQlx1N0VERlx1NjdCNlx1Njc4NCcsXG4gICAgY29sbGFwc2VkOiB0cnVlLFxuICAgIGl0ZW1zOiBbXG4gICAgICB7IHRleHQ6ICc5LjEgXHU5MUNGXHU1MzE2XHU3Q0ZCXHU3RURGXHU4QkJFXHU4QkExJywgbGluazogJy9ndWlkZS9tMDktbGl2ZS10cmFkaW5nLzkuMS1zeXN0ZW0tZGVzaWduJyB9LFxuICAgICAgeyB0ZXh0OiAnOS4yIFx1NUI5RVx1NjVGNlx1NjU3MFx1NjM2RVx1N0JBMVx1OTA1MycsIGxpbms6ICcvZ3VpZGUvbTA5LWxpdmUtdHJhZGluZy85LjItZGF0YS1waXBlbGluZScgfSxcbiAgICAgIHsgdGV4dDogJzkuMyBcdTZBMjFcdTYyREZcdTRFMEVcdTVCOUVcdTc2RDhcdTVCRjlcdTYzQTUnLCBsaW5rOiAnL2d1aWRlL20wOS1saXZlLXRyYWRpbmcvOS4zLWJyb2tlci1hcGknIH0sXG4gICAgICB7IHRleHQ6ICc5LjQgXHU3QjU2XHU3NTY1XHU3NkQxXHU2M0E3XHU0RTBFXHU4RkQwXHU3RUY0JywgbGluazogJy9ndWlkZS9tMDktbGl2ZS10cmFkaW5nLzkuNC1tb25pdG9yaW5nJyB9LFxuICAgICAgeyB0ZXh0OiAnOS41IFx1NTQwOFx1ODlDNFx1NEUwRVx1NzZEMVx1N0JBMScsIGxpbms6ICcvZ3VpZGUvbTA5LWxpdmUtdHJhZGluZy85LjUtY29tcGxpYW5jZScgfSxcbiAgICBdXG4gIH0sXG4gIHtcbiAgICB0ZXh0OiAnXHU2QTIxXHU1NzU3XHU1MzQxXHVGRjFBXHU1MjREXHU2Q0JGXHU0RTEzXHU5ODk4XHU0RTBFXHU4MDRDXHU0RTFBXHU2MjEwXHU5NTdGJyxcbiAgICBjb2xsYXBzZWQ6IHRydWUsXG4gICAgaXRlbXM6IFtcbiAgICAgIHsgdGV4dDogJzEwLjEgXHU1RjNBXHU1MzE2XHU1QjY2XHU0RTYwXHU0RUE0XHU2NjEzJywgbGluazogJy9ndWlkZS9tMTAtZnJvbnRpZXIvMTAuMS1ybCcgfSxcbiAgICAgIHsgdGV4dDogJzEwLjIgXHU3NTFGXHU2MjEwXHU1RjBGQUknLCBsaW5rOiAnL2d1aWRlL20xMC1mcm9udGllci8xMC4yLWdlbi1haScgfSxcbiAgICAgIHsgdGV4dDogJzEwLjMgXHU2Njk3XHU2QzYwJywgbGluazogJy9ndWlkZS9tMTAtZnJvbnRpZXIvMTAuMy1kYXJrLXBvb2wnIH0sXG4gICAgICB7IHRleHQ6ICcxMC40IFx1NTZFMlx1OTYxRlx1NTIwNlx1NURFNScsIGxpbms6ICcvZ3VpZGUvbTEwLWZyb250aWVyLzEwLjQtY2FyZWVyJyB9LFxuICAgICAgeyB0ZXh0OiAnMTAuNSBcdTdFQzhcdTY3ODFcdTk4NzlcdTc2RUUnLCBsaW5rOiAnL2d1aWRlL20xMC1mcm9udGllci8xMC41LWZpbmFsLXByb2plY3QnIH0sXG4gICAgXVxuICB9LFxuICB7XG4gICAgdGV4dDogJ1x1NkEyMVx1NTc1N1x1NTM0MVx1NEUwMFx1RkYxQVx1NjcxRlx1Njc0M1x1NEUwRVx1ODg0RFx1NzUxRlx1NTRDMVx1NUI5QVx1NEVGN1x1OEZEQlx1OTYzNicsXG4gICAgY29sbGFwc2VkOiB0cnVlLFxuICAgIGl0ZW1zOiBbXG4gICAgICB7IHRleHQ6ICcxMS4xIFx1NjcxRlx1Njc0MyBHcmVla3MgXHU4QkU2XHU4OUUzJywgbGluazogJy9ndWlkZS9tMTEtZGVyaXZhdGl2ZXMvMTEuMS1ncmVla3MnIH0sXG4gICAgICB7IHRleHQ6ICcxMS4yIFx1NkNFMlx1NTJBOFx1NzM4N1x1NjZGMlx1OTc2Mlx1NEUwRVx1NTk1N1x1NTIyOScsIGxpbms6ICcvZ3VpZGUvbTExLWRlcml2YXRpdmVzLzExLjItdm9sLXN1cmZhY2UnIH0sXG4gICAgICB7IHRleHQ6ICcxMS4zIFx1NTk0N1x1NUYwMlx1NjcxRlx1Njc0M1x1NEUwRVx1N0VEM1x1Njc4NFx1NTMxNlx1NEVBN1x1NTRDMScsIGxpbms6ICcvZ3VpZGUvbTExLWRlcml2YXRpdmVzLzExLjMtZXhvdGljLW9wdGlvbnMnIH0sXG4gICAgICB7IHRleHQ6ICcxMS40IFx1NEU4Q1x1NTNDOVx1NjgxMVx1NEUwRVx1NjcwOVx1OTY1MFx1NURFRVx1NTIwNlx1NkNENScsIGxpbms6ICcvZ3VpZGUvbTExLWRlcml2YXRpdmVzLzExLjQtdHJlZS1mZG0nIH0sXG4gICAgICB7IHRleHQ6ICcxMS41IFx1ODQ5OVx1NzI3OVx1NTM2MVx1NkQxQlx1NUI5QVx1NEVGN1x1OEZEQlx1OTYzNicsIGxpbms6ICcvZ3VpZGUvbTExLWRlcml2YXRpdmVzLzExLjUtbWMtcHJpY2luZycgfSxcbiAgICAgIHsgdGV4dDogJzExLjYgXHU2NzFGXHU2NzQzXHU1RTAyXHU1NzNBXHU1N0ZBXHU3ODQwJywgbGluazogJy9ndWlkZS9tMTEtZGVyaXZhdGl2ZXMvMTEuNi1vcHRpb25zLW1hcmtldCcgfSxcbiAgICAgIHsgdGV4dDogJzExLjcgXHU5NjkwXHU1NDJCXHU2Q0UyXHU1MkE4XHU3Mzg3IHZzIFx1NTM4Nlx1NTNGMlx1NkNFMlx1NTJBOFx1NzM4NycsIGxpbms6ICcvZ3VpZGUvbTExLWRlcml2YXRpdmVzLzExLjctaXYtdnMtaHYnIH0sXG4gICAgICB7IHRleHQ6ICcxMS44IFx1NkNFMlx1NTJBOFx1NzM4N1x1NEVBNFx1NjYxM1x1N0I1Nlx1NzU2NScsIGxpbms6ICcvZ3VpZGUvbTExLWRlcml2YXRpdmVzLzExLjgtdm9sLXRyYWRpbmcnIH0sXG4gICAgICB7IHRleHQ6ICcxMS45IFx1NTk1N1x1NEZERFx1N0I1Nlx1NzU2NVx1NUI5RVx1NjIxOCcsIGxpbms6ICcvZ3VpZGUvbTExLWRlcml2YXRpdmVzLzExLjktaGVkZ2luZy1wcmFjdGljZScgfSxcbiAgICAgIHsgdGV4dDogJzExLjEwIFx1NTczQVx1NTE4NVx1NjcxRlx1Njc0M1x1N0I1Nlx1NzU2NVx1NEUyRFx1NTZGRCBBIFx1ODBBMScsIGxpbms6ICcvZ3VpZGUvbTExLWRlcml2YXRpdmVzLzExLjEwLWNoaW5hLWxpc3RlZC1vcHRpb25zJyB9LFxuICAgIF1cbiAgfSxcbiAge1xuICAgIHRleHQ6ICdcdTZBMjFcdTU3NTdcdTUzNDFcdTRFOENcdUZGMUFcdTU2RkFcdTVCOUFcdTY1MzZcdTc2Q0FcdTkxQ0ZcdTUzMTYnLFxuICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICBpdGVtczogW1xuICAgICAgeyB0ZXh0OiAnMTIuMSBcdTY1MzZcdTc2Q0FcdTczODdcdTY2RjJcdTdFQkZcdTVFRkFcdTZBMjEnLCBsaW5rOiAnL2d1aWRlL20xMi1maXhlZC1pbmNvbWUvMTIuMS15aWVsZC1jdXJ2ZScgfSxcbiAgICAgIHsgdGV4dDogJzEyLjIgXHU0RTQ1XHU2NzFGXHU0RTBFXHU1MUY4XHU1RUE2XHU1MTREXHU3NUFCJywgbGluazogJy9ndWlkZS9tMTItZml4ZWQtaW5jb21lLzEyLjItZHVyYXRpb24tY29udmV4aXR5JyB9LFxuICAgICAgeyB0ZXh0OiAnMTIuMyBcdTUyMjlcdTczODdcdTRFOTJcdTYzNjJcdTRFMEVcdTRFOTJcdTYzNjJcdTY3MUZcdTY3NDMnLCBsaW5rOiAnL2d1aWRlL20xMi1maXhlZC1pbmNvbWUvMTIuMy1pcnMtc3dhcHRpb24nIH0sXG4gICAgICB7IHRleHQ6ICcxMi40IFx1NEZFMVx1NzUyOFx1NTIyOVx1NURFRVx1NEUwRUNEUycsIGxpbms6ICcvZ3VpZGUvbTEyLWZpeGVkLWluY29tZS8xMi40LWNyZWRpdC1zcHJlYWQnIH0sXG4gICAgICB7IHRleHQ6ICcxMi41IE1CU1x1NEUwRVx1OEQ0NFx1NEVBN1x1OEJDMVx1NTIzOFx1NTMxNicsIGxpbms6ICcvZ3VpZGUvbTEyLWZpeGVkLWluY29tZS8xMi41LW1icycgfSxcbiAgICBdXG4gIH0sXG4gIHtcbiAgICB0ZXh0OiAnXHU2QTIxXHU1NzU3XHU1MzQxXHU0RTA5XHVGRjFBXHU1MkEwXHU1QkM2XHU4RDI3XHU1RTAxXHU5MUNGXHU1MzE2JyxcbiAgICBjb2xsYXBzZWQ6IHRydWUsXG4gICAgaXRlbXM6IFtcbiAgICAgIHsgdGV4dDogJzEzLjEgXHU5NEZFXHU0RTBBXHU2NTcwXHU2MzZFXHU1MjA2XHU2NzkwJywgbGluazogJy9ndWlkZS9tMTMtY3J5cHRvLzEzLjEtb25jaGFpbicgfSxcbiAgICAgIHsgdGV4dDogJzEzLjIgXHU4RDQ0XHU5MUQxXHU4RDM5XHU3Mzg3XHU0RTBFXHU1OTU3XHU1MjI5JywgbGluazogJy9ndWlkZS9tMTMtY3J5cHRvLzEzLjItZnVuZGluZy1yYXRlJyB9LFxuICAgICAgeyB0ZXh0OiAnMTMuMyBNRVZcdTRFMEVcdTRFQTRcdTY2MTNcdTYzOTJcdTVFOEYnLCBsaW5rOiAnL2d1aWRlL20xMy1jcnlwdG8vMTMuMy1tZXYnIH0sXG4gICAgICB7IHRleHQ6ICcxMy40IERFWFx1NkQ0MVx1NTJBOFx1NjAyN1x1NTA1QVx1NUUwMicsIGxpbms6ICcvZ3VpZGUvbTEzLWNyeXB0by8xMy40LWRleC1tbScgfSxcbiAgICAgIHsgdGV4dDogJzEzLjUgXHU2QzM4XHU3RUVEXHU1NDA4XHU3RUE2XHU3QjU2XHU3NTY1JywgbGluazogJy9ndWlkZS9tMTMtY3J5cHRvLzEzLjUtcGVycHMnIH0sXG4gICAgXVxuICB9LFxuICB7XG4gICAgdGV4dDogJ1x1NkEyMVx1NTc1N1x1NTM0MVx1NTZEQlx1RkYxQVx1NUUwMlx1NTczQVx1NUZBRVx1ODlDMlx1N0VEM1x1Njc4NFx1NkRGMVx1NUVBNicsXG4gICAgY29sbGFwc2VkOiB0cnVlLFxuICAgIGl0ZW1zOiBbXG4gICAgICB7IHRleHQ6ICcxNC4xIFx1OEJBMlx1NTM1NVx1NkQ0MVx1NkJEMlx1NjAyN1x1NkEyMVx1NTc4QicsIGxpbms6ICcvZ3VpZGUvbTE0LW1pY3Jvc3RydWN0dXJlLWRlZXAvMTQuMS10b3hpY2l0eScgfSxcbiAgICAgIHsgdGV4dDogJzE0LjIgS3lsZVx1NEUwRUdsb3N0ZW4tTWlsZ3JvbScsIGxpbms6ICcvZ3VpZGUvbTE0LW1pY3Jvc3RydWN0dXJlLWRlZXAvMTQuMi1pbmZvcm1hdGlvbi1tb2RlbHMnIH0sXG4gICAgICB7IHRleHQ6ICcxNC4zIFx1NjcwMFx1NEYxOFx1NjI2N1x1ODg0Q1x1NzQwNlx1OEJCQScsIGxpbms6ICcvZ3VpZGUvbTE0LW1pY3Jvc3RydWN0dXJlLWRlZXAvMTQuMy1vcHRpbWFsLWV4ZWN1dGlvbicgfSxcbiAgICAgIHsgdGV4dDogJzE0LjQgXHU5NjUwXHU0RUY3XHU4QkEyXHU1MzU1XHU3QzNGXHU1MkE4XHU1MjlCXHU1QjY2JywgbGluazogJy9ndWlkZS9tMTQtbWljcm9zdHJ1Y3R1cmUtZGVlcC8xNC40LWxvYi1keW5hbWljcycgfSxcbiAgICAgIHsgdGV4dDogJzE0LjUgXHU5QUQ4XHU5ODkxXHU1MDVBXHU1RTAyXHU3QjU2XHU3NTY1XHU4RkRCXHU5NjM2JywgbGluazogJy9ndWlkZS9tMTQtbWljcm9zdHJ1Y3R1cmUtZGVlcC8xNC41LWhmdC1tbS1hZHZhbmNlZCcgfSxcbiAgICBdXG4gIH0sXG4gIHtcbiAgICB0ZXh0OiAnXHU2QTIxXHU1NzU3XHU1MzQxXHU0RTk0XHVGRjFBXHU1QjhGXHU4OUMyXHU3RUNGXHU2RDRFXHU5MUNGXHU1MzE2JyxcbiAgICBjb2xsYXBzZWQ6IHRydWUsXG4gICAgaXRlbXM6IFtcbiAgICAgIHsgdGV4dDogJzE1LjEgXHU1QjhGXHU4OUMyXHU1NkUwXHU1QjUwXHU2QTIxXHU1NzhCJywgbGluazogJy9ndWlkZS9tMTUtbWFjcm8vMTUuMS1tYWNyby1mYWN0b3JzJyB9LFxuICAgICAgeyB0ZXh0OiAnMTUuMiBcdTdGOEVcdTgwNTRcdTUwQThcdTY1M0ZcdTdCNTZcdTkxQ0ZcdTUzMTYnLCBsaW5rOiAnL2d1aWRlL20xNS1tYWNyby8xNS4yLWZlZC1wb2xpY3knIH0sXG4gICAgICB7IHRleHQ6ICcxNS4zIFx1OTAxQVx1ODBDMFx1OTg4NFx1NjcxRlx1NUVGQVx1NkEyMScsIGxpbms6ICcvZ3VpZGUvbTE1LW1hY3JvLzE1LjMtaW5mbGF0aW9uJyB9LFxuICAgICAgeyB0ZXh0OiAnMTUuNCBcdTdFQ0ZcdTZENEVcdTU0NjhcdTY3MUZcdTYyRTlcdTY1RjYnLCBsaW5rOiAnL2d1aWRlL20xNS1tYWNyby8xNS40LWN5Y2xlLXRpbWluZycgfSxcbiAgICAgIHsgdGV4dDogJzE1LjUgXHU4REU4XHU4RDQ0XHU0RUE3XHU1QjhGXHU4OUMyXHU3QjU2XHU3NTY1JywgbGluazogJy9ndWlkZS9tMTUtbWFjcm8vMTUuNS1jcm9zcy1hc3NldCcgfSxcbiAgICBdXG4gIH0sXG4gIHtcbiAgICB0ZXh0OiAnXHU2QTIxXHU1NzU3XHU1MzQxXHU1MTZEXHVGRjFBXHU5OENFXHU5NjY5XHU3QkExXHU3NDA2XHU0RjUzXHU3Q0ZCJyxcbiAgICBjb2xsYXBzZWQ6IHRydWUsXG4gICAgaXRlbXM6IFtcbiAgICAgIHsgdGV4dDogJzE2LjEgXHU5OENFXHU5NjY5XHU1MjA2XHU4OUUzXHU0RTBFXHU1RjUyXHU1NkUwJywgbGluazogJy9ndWlkZS9tMTYtcmlzay1tYW5hZ2VtZW50LzE2LjEtcmlzay1kZWNvbXBvc2l0aW9uJyB9LFxuICAgICAgeyB0ZXh0OiAnMTYuMiBcdTY3ODFcdTUwM0NcdTc0MDZcdThCQkFcdTRFMEVcdTVDM0VcdTkwRThcdTk4Q0VcdTk2NjknLCBsaW5rOiAnL2d1aWRlL20xNi1yaXNrLW1hbmFnZW1lbnQvMTYuMi1ldnQtdGFpbCcgfSxcbiAgICAgIHsgdGV4dDogJzE2LjMgXHU1MzhCXHU1MjlCXHU2RDRCXHU4QkQ1XHU0RTBFXHU2MEM1XHU2NjZGXHU1MjA2XHU2NzkwJywgbGluazogJy9ndWlkZS9tMTYtcmlzay1tYW5hZ2VtZW50LzE2LjMtc3RyZXNzLXRlc3RpbmcnIH0sXG4gICAgICB7IHRleHQ6ICcxNi40IFx1NURGNFx1NTg1RVx1NUMxNFx1NTM0Rlx1OEJBRVx1NEUwRVx1NzZEMVx1N0JBMVx1OEQ0NFx1NjcyQycsIGxpbms6ICcvZ3VpZGUvbTE2LXJpc2stbWFuYWdlbWVudC8xNi40LWJhc2VsJyB9LFxuICAgICAgeyB0ZXh0OiAnMTYuNSBcdTVDM0VcdTkwRThcdTVCRjlcdTUxQjJcdTdCNTZcdTc1NjUnLCBsaW5rOiAnL2d1aWRlL20xNi1yaXNrLW1hbmFnZW1lbnQvMTYuNS10YWlsLWhlZGdlJyB9LFxuICAgIF1cbiAgfSxcbiAge1xuICAgIHRleHQ6ICdcdTZBMjFcdTU3NTdcdTUzNDFcdTRFMDNcdUZGMUFcdTkxQ0ZcdTUzMTZcdTY1NzBcdTYzNkVcdTVERTVcdTdBMEInLFxuICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICBpdGVtczogW1xuICAgICAgeyB0ZXh0OiAnMTcuMSBUaWNrXHU2NTcwXHU2MzZFXHU1RTkzXHU4QkJFXHU4QkExJywgbGluazogJy9ndWlkZS9tMTctZGF0YS1lbmdpbmVlcmluZy8xNy4xLXRpY2stZGInIH0sXG4gICAgICB7IHRleHQ6ICcxNy4yIFx1NUI5RVx1NjVGNkVUTFx1N0JBMVx1OTA1MycsIGxpbms6ICcvZ3VpZGUvbTE3LWRhdGEtZW5naW5lZXJpbmcvMTcuMi1yZWFsdGltZS1ldGwnIH0sXG4gICAgICB7IHRleHQ6ICcxNy4zIFx1NjU3MFx1NjM2RVx1OEQyOFx1OTFDRlx1NzZEMVx1NjNBNycsIGxpbms6ICcvZ3VpZGUvbTE3LWRhdGEtZW5naW5lZXJpbmcvMTcuMy1kYXRhLXF1YWxpdHknIH0sXG4gICAgICB7IHRleHQ6ICcxNy40IFx1NjI3OVx1NTkwNFx1NzQwNlx1NEUwRVx1NkQ0MVx1NTkwNFx1NzQwNicsIGxpbms6ICcvZ3VpZGUvbTE3LWRhdGEtZW5naW5lZXJpbmcvMTcuNC1iYXRjaC1zdHJlYW1pbmcnIH0sXG4gICAgICB7IHRleHQ6ICcxNy41IFx1NzI3OVx1NUY4MVx1NUI1OFx1NTBBOChGZWF0dXJlIFN0b3JlKScsIGxpbms6ICcvZ3VpZGUvbTE3LWRhdGEtZW5naW5lZXJpbmcvMTcuNS1mZWF0dXJlLXN0b3JlJyB9LFxuICAgIF1cbiAgfSxcbiAge1xuICAgIHRleHQ6ICdcdTZBMjFcdTU3NTdcdTUzNDFcdTUxNkJcdUZGMUFcdTdCNTZcdTc1NjVcdTc1MUZcdTU0N0RcdTU0NjhcdTY3MUZcdTdCQTFcdTc0MDYnLFxuICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICBpdGVtczogW1xuICAgICAgeyB0ZXh0OiAnMTguMSBcdTdCNTZcdTc1NjVcdTVCNzVcdTUzMTZcdTRFMEVcdThCQzRcdTVCQTEnLCBsaW5rOiAnL2d1aWRlL20xOC1zdHJhdGVneS1saWZlY3ljbGUvMTguMS1pbmN1YmF0aW9uJyB9LFxuICAgICAgeyB0ZXh0OiAnMTguMiBcdTZBMjFcdTYyREZcdTc2RDhcdTRFMEVcdTVCOUVcdTc2RDhcdThGQzdcdTZFMjEnLCBsaW5rOiAnL2d1aWRlL20xOC1zdHJhdGVneS1saWZlY3ljbGUvMTguMi1wYXBlci10by1saXZlJyB9LFxuICAgICAgeyB0ZXh0OiAnMTguMyBBL0JcdTZENEJcdThCRDVcdTRFMEVcdTkxRDFcdTRFMURcdTk2QzBcdTUzRDFcdTVFMDMnLCBsaW5rOiAnL2d1aWRlL20xOC1zdHJhdGVneS1saWZlY3ljbGUvMTguMy1hYi10ZXN0aW5nJyB9LFxuICAgICAgeyB0ZXh0OiAnMTguNCBcdTdCNTZcdTc1NjVcdTdFRTlcdTY1NDhcdTVGNTJcdTU2RTAnLCBsaW5rOiAnL2d1aWRlL20xOC1zdHJhdGVneS1saWZlY3ljbGUvMTguNC1hdHRyaWJ1dGlvbicgfSxcbiAgICAgIHsgdGV4dDogJzE4LjUgXHU3QjU2XHU3NTY1XHU5MDAwXHU1Rjc5XHU0RTBFXHU1OTBEXHU3NkQ4JywgbGluazogJy9ndWlkZS9tMTgtc3RyYXRlZ3ktbGlmZWN5Y2xlLzE4LjUtcmV0aXJlbWVudCcgfSxcbiAgICBdXG4gIH0sXG4gIHtcbiAgICB0ZXh0OiAnXHU2QTIxXHU1NzU3XHU1MzQxXHU0RTVEXHVGRjFBXHU0RTJEXHU1NkZEQVx1ODBBMVx1NzI3OVx1ODI3Mlx1OTFDRlx1NTMxNicsXG4gICAgY29sbGFwc2VkOiB0cnVlLFxuICAgIGl0ZW1zOiBbXG4gICAgICB7IHRleHQ6ICcxOS4xIFx1NkRBOFx1OERDQ1x1NTA1Q1x1Njc3Rlx1N0I1Nlx1NzU2NScsIGxpbms6ICcvZ3VpZGUvbTE5LWEtc2hhcmUvMTkuMS1saW1pdC11cCcgfSxcbiAgICAgIHsgdGV4dDogJzE5LjIgXHU2MjUzXHU2NUIwXHU3QjU2XHU3NTY1XHU1MjA2XHU2NzkwJywgbGluazogJy9ndWlkZS9tMTktYS1zaGFyZS8xOS4yLWlwbycgfSxcbiAgICAgIHsgdGV4dDogJzE5LjMgXHU4ODRDXHU0RTFBXHU4RjZFXHU1MkE4XHU2QTIxXHU1NzhCJywgbGluazogJy9ndWlkZS9tMTktYS1zaGFyZS8xOS4zLXNlY3Rvci1yb3RhdGlvbicgfSxcbiAgICAgIHsgdGV4dDogJzE5LjQgXHU1MzE3XHU1NDExXHU4RDQ0XHU5MUQxXHU0RTBFXHU5Rjk5XHU4NjRFXHU2OTlDJywgbGluazogJy9ndWlkZS9tMTktYS1zaGFyZS8xOS40LW5vcnRoYm91bmQnIH0sXG4gICAgICB7IHRleHQ6ICcxOS41IFx1NjUzRlx1N0I1Nlx1NTZFMFx1NUI1MFx1NEUwRVx1NEU4Qlx1NEVGNlx1OUE3MVx1NTJBOCcsIGxpbms6ICcvZ3VpZGUvbTE5LWEtc2hhcmUvMTkuNS1wb2xpY3ktZXZlbnRzJyB9LFxuICAgIF1cbiAgfSxcbiAge1xuICAgIHRleHQ6ICdcdTZBMjFcdTU3NTdcdTRFOENcdTUzNDFcdUZGMUFcdTkxQ0ZcdTUzMTZcdTk3NjJcdThCRDVcdTUxQzZcdTU5MDcnLFxuICAgIGNvbGxhcHNlZDogdHJ1ZSxcbiAgICBpdGVtczogW1xuICAgICAgeyB0ZXh0OiAnMjAuMSBcdTY1NzBcdTVCNjZcdTRFMEVcdTdFREZcdThCQTFcdTk3NjJcdThCRDVcdTk4OTgnLCBsaW5rOiAnL2d1aWRlL20yMC1pbnRlcnZpZXctcHJlcC8yMC4xLW1hdGgtc3RhdHMnIH0sXG4gICAgICB7IHRleHQ6ICcyMC4yIFx1N0YxNlx1N0EwQlx1NEUwRVx1N0I5N1x1NkNENVx1OTg5OCcsIGxpbms6ICcvZ3VpZGUvbTIwLWludGVydmlldy1wcmVwLzIwLjItY29kaW5nJyB9LFxuICAgICAgeyB0ZXh0OiAnMjAuMyBcdTkxRDFcdTg3OERcdTRFMEVcdTdCNTZcdTc1NjVcdTk4OTgnLCBsaW5rOiAnL2d1aWRlL20yMC1pbnRlcnZpZXctcHJlcC8yMC4zLWZpbmFuY2UnIH0sXG4gICAgICB7IHRleHQ6ICcyMC40IFx1ODExMVx1N0I0Qlx1NjAyNVx1OEY2Q1x1NUYyRlx1NEUwRVx1ODg0Q1x1NEUzQVx1OTc2MicsIGxpbms6ICcvZ3VpZGUvbTIwLWludGVydmlldy1wcmVwLzIwLjQtYnJhaW4tdGVhc2VycycgfSxcbiAgICAgIHsgdGV4dDogJzIwLjUgXHU2QTIxXHU2MkRGXHU5NzYyXHU4QkQ1XHU0RTBFXHU1OTBEXHU3NkQ4JywgbGluazogJy9ndWlkZS9tMjAtaW50ZXJ2aWV3LXByZXAvMjAuNS1tb2NrLWludGVydmlldycgfSxcbiAgICAgIHsgdGV4dDogJzIwLjYgXHU5QUQ4XHU5ODkxXHU5NzYyXHU4QkQ1XHU5ODk4KFx1NEUyRFx1NTkxNlx1NjczQVx1Njc4NCknLCBsaW5rOiAnL2d1aWRlL20yMC1pbnRlcnZpZXctcHJlcC8yMC42LXJlYWwtaW50ZXJ2aWV3cycgfSxcbiAgICAgIHsgdGV4dDogJzIwLjcgQysrIFx1OTFDRlx1NTMxNlx1OTc2Mlx1OEJENVx1NEUxM1x1OTg5OCcsIGxpbms6ICcvZ3VpZGUvbTIwLWludGVydmlldy1wcmVwLzIwLjctY3BwLXF1YW50JyB9LFxuICAgICAgeyB0ZXh0OiAnMjAuOCBSZXNlYXJjaCBcdTk4NzlcdTc2RUVcdTUzMDVcdTg4QzUnLCBsaW5rOiAnL2d1aWRlL20yMC1pbnRlcnZpZXctcHJlcC8yMC44LXJlc3VtZS1wb3J0Zm9saW8nIH0sXG4gICAgXVxuICB9LFxuXVxuXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoe1xuICB0aXRsZTogJ1F1YW50TGFiIFx1MDBCNyBcdTkxQ0ZcdTUzMTZcdTRFQTRcdTY2MTNcdTdDRkJcdTdFREZcdThCQkVcdThCQTFcdTRFMEVcdTVCOUVcdThERjUnLFxuICBkZXNjcmlwdGlvbjogJ0ZpblRlY2ggXHU5OENFXHU2ODNDXHU3Njg0XHU5MUNGXHU1MzE2XHU0RUE0XHU2NjEzXHU1QjY2XHU0RTYwXHU1RTczXHU1M0YwIFx1MDBCNyAxMCBcdTU5MjdcdTZBMjFcdTU3NTcgXHUwMEI3IDUwKyBcdTdBRTBcdTgyODIgXHUwMEI3IDkgXHU0RTJBXHU0RUE0XHU0RTkyXHU1RjBGXHU4QkExXHU3Qjk3XHU1NjY4JyxcbiAgbGFuZzogJ3poLUNOJyxcbiAgYXBwZWFyYW5jZTogdHJ1ZSxcbiAgaGVhZDogW1xuICAgIFsnbGluaycsIHsgcmVsOiAnaWNvbicsIHR5cGU6ICdpbWFnZS9zdmcreG1sJywgaHJlZjogJy9mYXZpY29uLnN2ZycgfV0sXG4gICAgWydtZXRhJywgeyBuYW1lOiAndGhlbWUtY29sb3InLCBjb250ZW50OiAnIzAwRTVBMCcgfV0sXG4gICAgWydtZXRhJywgeyBuYW1lOiAnZGVzY3JpcHRpb24nLCBjb250ZW50OiAnRmluVGVjaCBcdTk4Q0VcdTY4M0NcdTc2ODRcdTkxQ0ZcdTUzMTZcdTRFQTRcdTY2MTNcdTVCNjZcdTRFNjBcdTVFNzNcdTUzRjAnIH1dLFxuICAgIC8vIFx1NEYxOFx1NTE0OFx1NEY3Rlx1NzUyOFx1NjcyQ1x1NTczMCBQeW9kaWRlXHVGRjA4XHU0RjREXHU0RThFIC9weW9kaWRlL3B5b2RpZGUuanNcdUZGMENcdTc1MzEgcHVibGljL3B5b2RpZGUvIFx1OTc1OVx1NjAwMVx1NTNEMVx1NUUwM1x1RkYwOVxuICAgIC8vIFx1NTcyOFx1N0VCRlx1NjVGNlx1NkQ0Rlx1ODlDOFx1NTY2OFx1NEVDRFx1NTNFRlx1OTAxQVx1OEZDN1x1NEUwQlx1NjVCOSBDRE4gXHU1MTVDXHU1RTk1XHVGRjA4XHU1OTgyXHU2NzlDXHU2NzJDXHU1NzMwXHU3RjNBXHU1OTMxXHVGRjA5XG4gICAgWydzY3JpcHQnLCB7IHNyYzogJy9weW9kaWRlL3B5b2RpZGUuanMnIH1dLFxuICBdLFxuICB0aGVtZUNvbmZpZzoge1xuICAgIHNpZGViYXIsXG4gICAgbmF2OiBbXG4gICAgICB7IHRleHQ6ICdcdThCRkVcdTdBMEJcdTk5OTZcdTk4NzUnLCBsaW5rOiAnLycgfSxcbiAgICAgIHsgdGV4dDogJ1x1NkEyMVx1NTc1N1x1Njk4Mlx1ODlDOCcsIGxpbms6ICcvZ3VpZGUvJyB9LFxuICAgIF0sXG4gICAgc2VhcmNoOiB7XG4gICAgICBwcm92aWRlcjogJ2xvY2FsJyxcbiAgICAgIG9wdGlvbnM6IHtcbiAgICAgICAgdHJhbnNsYXRpb25zOiB7XG4gICAgICAgICAgYnV0dG9uOiB7IGJ1dHRvblRleHQ6ICdcdTY0MUNcdTdEMjInLCBidXR0b25BcmlhTGFiZWw6ICdcdTY0MUNcdTdEMjJcdTY1ODdcdTY4NjMnIH0sXG4gICAgICAgICAgbW9kYWw6IHsgbm9SZXN1bHRzVGV4dDogJ1x1NjVFMFx1N0VEM1x1Njc5QycsIHJlc2V0QnV0dG9uVGl0bGU6ICdcdTZFMDVcdTk2NjQnLCBkaXNwbGF5RGV0YWlsczogJ1x1NjYzRVx1NzkzQVx1OEJFNlx1NjBDNScsIGZvb3RlcjogeyBzZWxlY3RUZXh0OiAnXHU5MDA5XHU2MkU5JywgY2xvc2VUZXh0OiAnXHU1MTczXHU5NUVEJyB9IH1cbiAgICAgICAgfVxuICAgICAgfVxuICAgIH0sXG4gICAgZG9jRm9vdGVyOiB7IHByZXY6ICdcdTRFMEFcdTRFMDBcdTdBRTAnLCBuZXh0OiAnXHU0RTBCXHU0RTAwXHU3QUUwJyB9LFxuICAgIGRhcmtNb2RlU3dpdGNoTGFiZWw6ICdcdTRFM0JcdTk4OThcdTUyMDdcdTYzNjInLFxuICAgIHNpZGViYXJNZW51TGFiZWw6ICdcdTgzRENcdTUzNTUnLFxuICAgIHJldHVyblRvVG9wTGFiZWw6ICdcdTU2REVcdTUyMzBcdTk4NzZcdTkwRTgnLFxuICAgIG91dGxpbmU6IHsgbGFiZWw6ICdcdTY3MkNcdTk4NzVcdTc2RUVcdTVGNTUnIH0sXG4gIH0sXG4gIG1hcmtkb3duOiB7XG4gICAgbWF0aDogdHJ1ZSxcbiAgfSxcbiAgaWdub3JlRGVhZExpbmtzOiB0cnVlLFxuICAvLyBcdTRGQkZcdTY0M0FcdTcyNDhcdThGOTNcdTUxRkFcdTRGNERcdTdGNkVcdUZGMDhcdTkwN0ZcdTUxNERcdTRFMEUgLnZpdGVwcmVzcy9kaXN0IFx1NzY4NCBzYWZlLWRlbGV0ZSBcdTUxQjJcdTdBODFcdUZGMDlcbiAgb3V0RGlyOiBwcm9jZXNzLmVudi5RUE9SVEFCTEUgPyAncG9ydGFibGUvZGlzdCcgOiAnLnZpdGVwcmVzcy9kaXN0Jyxcbn0pXG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQXNRLFNBQVMsb0JBQW9CO0FBRW5TLElBQU0sVUFBVTtBQUFBLEVBQ1o7QUFBQSxJQUNFLE1BQU07QUFBQSxJQUNOLFdBQVc7QUFBQSxJQUNYLE9BQU87QUFBQSxNQUNMLEVBQUUsTUFBTSw0Q0FBYyxNQUFNLGtDQUFrQztBQUFBLE1BQzlELEVBQUUsTUFBTSxnQ0FBWSxNQUFNLHlDQUF5QztBQUFBLE1BQ25FLEVBQUUsTUFBTSw0Q0FBYyxNQUFNLHdDQUF3QztBQUFBLE1BQ3BFLEVBQUUsTUFBTSxnQ0FBWSxNQUFNLHFDQUFxQztBQUFBLE1BQy9ELEVBQUUsTUFBTSwwQ0FBc0IsTUFBTSx3Q0FBd0M7QUFBQSxNQUM1RSxFQUFFLE1BQU0sOERBQWlCLE1BQU0scUNBQXFDO0FBQUEsTUFDcEUsRUFBRSxNQUFNLGtEQUFlLE1BQU0sMkNBQTJDO0FBQUEsSUFDMUU7QUFBQSxFQUNGO0FBQUEs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
