# QuantLab 上线实施 Checklist（Day 0 – Day 7）

> 版本 v1.0 · 2026-09-08
> 配套文档：`DEPLOY.md`（操作手册）、`_reports/DEPLOY-PRD.md`（平台选型）
> 用法：每天开工前打开这一节，做完一项勾一项。每节末尾的「验收」必须全绿才能进下一天。

---

## 总览

| Day | 主题 | 预计投入 | 产出 |
|---|---|---|---|
| **Day 0** | 决策与准备 | 30 min | 账号齐备、方案确认 |
| **Day 1** | 代码上 GitHub | 1 h | 仓库就绪、产物策略定下来 |
| **Day 2** | 首次部署 | 1.5 h（含等待） | 站点上线，有公开 URL |
| **Day 3** | 验收与修复 | 1.5 h | 功能/性能全绿 |
| **Day 4** | 灾备与监控 | 1 h | Cloudflare 镜像 + 可用性监控 |
| **Day 5** | 内测 | 30 min + 等待 | 5 位真实用户反馈 |
| **Day 6** | 优化 | 1 h | 缓存/体积/体验调优 |
| **Day 7** | 发布与沉淀 | 1 h | 对外宣传 + 复盘文档 |

**可压缩**：Day 0+1+2 连着做，半天即可上线。Day 3-7 是打磨，可以慢慢来。

---

## Day 0 — 决策与准备（30 分钟）

### 0.1 确认三个决策

| # | 决策 | 推荐 | 你的选择 |
|---|---|---|---|
| D1 | 部署平台 | **Cloudflare Pages**（`*.pages.dev` 长期有效、免备案；EdgeOne 系统域名会 401，已改判） | ☑ **Cloudflare** |
| D2 | 仓库可见性 | **Public**（Actions 时长免费 unlimited） | ☐ Public ☐ Private |
| D3 | 是否提交预计算产物 `public/code/` | **是**（CI 从 20 min 降到 4 min） | ☐ 提交 ☐ 不提交 |

> **D2 说明（费用）**：**Public 仓库完全免费，且 Actions 分钟数无限**（2026 年政策，GitHub 所有计划都如此）。
> Private 仓库 Free 计划只有 **2000 Linux 分钟/月 + 500 MB artifact 存储**。
> 本工程单次构建 20 分钟（有产物则 5 分钟），Private 大约能跑 100 次/月——够用但不宽裕，
> 而且 79 MB 的构建产物留 7 天就会吃掉大半存储额度。
> **结论：选 Public，省心且零成本。**

> **D3 说明**：`public/code/` 19 MB / 4012 文件，是 439 个案例的运行结果。提交它 → CI 直接跳过 precompute，快且结果与本地 100% 一致；不提交 → CI 每次重跑，慢且约 5% 的重型依赖（torch/akshare 等）会失败。
> 代价：改了 Python 代码块后必须本地重跑 precompute 再提交，否则线上结果滞后。**建议提交**。

### 0.2 注册账号

- [ ] GitHub 账号（<https://github.com/signup>）
- [ ] Cloudflare（**<https://dash.cloudflare.com>**，注册即用，不需绑卡）
- [ ] 记下账号邮箱：`________________`

### 0.3 本地环境自检

```bash
cd /d/AI/study/quant
node -v                    # 期望 v22.x
python3 --version          # 期望 3.11+
git --version
npm -v
```

- [ ] 全部通过

### 0.4 记录当前基线

```bash
git log --oneline -1
git status --porcelain | wc -l
du -sh .vitepress/dist
```

填下来（出问题要对照）：

| 项 | 值 |
|---|---|
| 最新 commit | `____________` |
| 未提交改动数 | `______`（当前 665） |
| dist 体积 | `______`（当前 79 MB） |

**Day 0 验收**：☐ 三个决策已定 ☐ 两个账号已注册 ☐ 环境自检通过

---

## Day 1 — 代码上 GitHub（1 小时）

### 1.1 建远程空仓库

- [ ] 打开 <https://github.com/new>
- [ ] 仓库名 `quant-course`
- [ ] 可见性按 D2 选择
- [ ] **不勾选** README / .gitignore / license
- [ ] Create repository

### 1.2 清理本地工作区

```bash
cd /d/AI/study/quant

# 看清楚要提交什么（重点看有没有意外的大文件/敏感文件）
git status --porcelain | head -40
git status --porcelain | wc -l
```

- [ ] 确认没有 `.env`、密钥、个人隐私文件
- [ ] 确认 `.gitignore` 排除了 `node_modules/`、`.vitepress/dist/`、`portable/dist/`

按 D3 决定是否加产物：

```bash
# D3 = 提交
git add -A
git add -f public/code          # 若 .gitignore 误伤了它
```

```bash
# D3 = 不提交
git add -A
```

### 1.3 提交

```bash
git commit -m "chore: 上线前全量同步（122 章 + 439 案例 + 预计算产物）"
```

- [ ] 提交成功，记录 commit hash：`____________`

> 提交体积较大（19-100 MB），可能要等 1-2 分钟。

### 1.4 关联并推送

```bash
git remote add origin https://github.com/<用户名>/quant-course.git
git branch -M main
git push -u origin main
```

> 密码填 **Personal Access Token**（不是登录密码）：
> GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate → 勾 `repo`

- [ ] push 成功
- [ ] 浏览器打开仓库页，看到 `guide/`、`components/`、`scripts/`、`.github/workflows/deploy.yml`

### 1.5 确认工作流文件已入库

```bash
git ls-files .github/workflows/
git ls-files requirements-ci.txt
```

- [ ] 两个都在

### 1.6 配置 Secrets

- [ ] 打开 `https://github.com/<用户名>/quant-course/settings/secrets/actions`
- [ ] 新建 `EDGEONE_API_TOKEN`
  - 取值：Cloudflare 控制台 → My Profile → API Tokens → Create Token（模板选 Edit Cloudflare Workers）
  - 另需 Account ID：控制台首页右侧栏，或看地址栏 `dash.cloudflare.com/<这串 32 位就是>`
  - ⚠️ token 只显示一次，先粘到记事本
- [ ] （可选）新建 `CLOUDFLARE_API_TOKEN`
- [ ] （可选）新建 `CLOUDFLARE_ACCOUNT_ID`

**Day 1 验收**：☐ 仓库页能看到全部源码 ☐ `.github/workflows/deploy.yml` 已入库 ☐ 至少 `EDGEONE_API_TOKEN` 已配置

---

## Day 2 — 首次部署（1.5 小时，含等待）

### 2.1 手动触发第一次构建

- [ ] 仓库 → **Actions** 标签 → 左侧 **Build & Deploy**
- [ ] 右侧 **Run workflow** → 分支 `main` → Run workflow
- [ ] 点进任务，实时看日志

### 2.2 盯各阶段（记录实际耗时）

| 阶段 | 预计 | 你的实测 |
|---|---|---|
| Checkout + Node 依赖 | 2 min | `____` |
| Python 依赖（若跑了） | 3 min | `____` |
| extract-py-fences | 1 min | `____` |
| precompute（若跑了） | 8-15 min | `____` |
| vitepress build | 3-5 min | `____` |
| 部署 Cloudflare（wrangler pages deploy） | 1 min | `____` |
| **总计** | **4-25 min** | `____` |

- [ ] 每一步都是绿的

> 如果 precompute 那步黄了（`continue-on-error`），不算失败，但要看日志确认失败率。>10% 就说明 Python 依赖有问题，回到 D3 改成"提交产物"。

### 2.3 拿到 URL

- [ ] 登录 <https://dash.cloudflare.com> → Workers & Pages → 看到项目 `quant-course`
- [ ] 访问链接：`https://quant-course.pages.dev`
- [ ] 浏览器打开，首页正常

### 2.4 顺手做三件事

- [ ] 把 URL 存进浏览器书签
- [ ] 记到手机备忘录（方便随时发给别人）
- [ ] 域名前缀由项目名决定：仓库 Variables 里设 `CLOUDFLARE_PROJECT = quant-course` → 域名即 `quant-course.pages.dev`

**Day 2 验收**：☐ 构建全绿 ☐ 拿到 URL ☐ 首页能打开

---

## Day 3 — 验收与修复（1.5 小时）

### 3.1 功能验收（逐项打勾）

- [ ] 首页渲染正常，侧边栏 20 个模块齐全
- [ ] 随机 5 个章节，正文/公式/表格都正常
- [ ] **至少 3 个案例的「运行结果」有真实数字**
- [ ] **至少 1 个案例的图表（SVG）显示出来了**
- [ ] 站内搜索可用（右上角）
- [ ] 手机浏览器排版正常
- [ ] 上一章/下一章翻页正常
- [ ] 折叠块（如果有）能展开

### 3.2 用一键脚本体检

```bash
# 改 URL 后运行
URL=https://quant-course.pages.dev
for p in "/" "/guide/m01-overview/1.3-quant-mindset.html" "/guide/m03-python-data/3.3-performance.html" "/guide/m04-backtest/4.1-engine.html"; do
  printf "%-55s " "$p"
  curl -o /dev/null -s -w "HTTP %{http_code}  %{time_total}s\n" "$URL$p"
done
```

- [ ] 全部 HTTP 200
- [ ] 首屏 < 3s

### 3.3 抽查运行结果质量

```bash
# 线上页面里不应该出现"本段代码定义："这种裸噪音
curl -s "$URL/guide/m04-backtest/4.1-engine.html" | grep -c "本段代码定义："
```

- [ ] 结果应为 `0`

- [ ] 页面上搜索 "⚠ 暂无运行结果" 出现次数：期望 0
  ```bash
  curl -s "$URL/" > /tmp/home.html && grep -c "暂无运行结果" /tmp/home.html
  ```

### 3.4 国内访问实测（关键）

- [ ] 手机关 WiFi，用 4G/5G 打开
- [ ] 找 1 位联通用户试
- [ ] 找 1 位移动用户试
- [ ] 找 1 位电信用户试
- [ ] 记录各自首屏时间：联通 `____`s / 移动 `____`s / 电信 `____`s

> 如果某家运营商明显慢（>5s），进入 Day 6 的"换 Cloudflare 对比"环节。

### 3.5 修复清单

把发现的问题记在这：

| # | 现象 | 原因 | 处理 | 状态 |
|---|---|---|---|---|
| 1 | | | | ☐ |
| 2 | | | | ☐ |
| 3 | | | | ☐ |

**Day 3 验收**：☐ 3.1 全绿 ☐ 3.3 噪音计数为 0 ☐ 三大运营商都能打开

---

## Day 4 — 灾备与监控（1 小时）

### 4.1 Cloudflare Pages 镜像

- [ ] 注册 <https://dash.cloudflare.com/sign-up>（免费）
- [ ] 创建 API Token：My Profile → API Tokens → Create Custom Token
  - Permissions：`Account` → `Cloudflare Pages` → `Edit`
  - Account Resources：Include → 你的账号
- [ ] 复制 Account ID（控制台首页右侧栏）
- [ ] 把两个值加到 GitHub Secrets
- [ ] 手动触发一次 workflow，确认 `deploy-cloudflare` 步骤绿了
- [ ] 记下灾备 URL：`https://______________.pages.dev`

### 4.2 可用性监控

- [ ] 注册 <https://uptimerobot.com>（免费 50 个监控点，5 分钟粒度）
- [ ] Add New Monitor：
  - Type: HTTP(s)
  - URL: `https://quant-course.pages.dev`
  - Interval: 5 min
- [ ] 填告警邮箱
- [ ] 再加一个监控灾备 URL（可选）

> 站点挂了会收到邮件。免费版不支持短信/微信，需要的话可以把告警邮件转发到微信（QQ 邮箱有"微信提醒"）。

### 4.3 （可选）访问统计

- [ ] 选一个：Cloudflare Web Analytics / 百度统计 / 51.la
- [ ] 拿到统计代码
- [ ] 加到 `.vitepress/config.ts` 的 `head` 里
- [ ] push 触发重新部署

```ts
// .vitepress/config.ts
head: [
  // ... 已有配置
  ['script', { async: '', src: 'https://你的统计脚本地址' }],
]
```

**Day 4 验收**：☐ Cloudflare 镜像可访问 ☐ UptimeRobot 已监控主站

---

## Day 5 — 内测（30 分钟 + 等待反馈）

### 5.1 邀请 5-10 位内测

目标人群：量化同行、同事、对量化感兴趣的朋友。

发送模板（可直接复制）：

```
做了个量化交易学习站，122 章、24 万字、439 个可运行的 Python 案例，
从市场认知到策略回测到实盘工程全链路。

https://你的网址

纯免费、无广告、无需注册。有空帮我点几章看看：
1. 打开速度怎么样？
2. 有没有打不开或排版错乱的页面？
3. 内容上哪里讲得不清楚、或者你想看但没写到的？
```

- [ ] 发给 `____` 人

### 5.2 收集反馈

| # | 反馈人 | 类型 | 内容 | 处理 |
|---|---|---|---|---|
| 1 | | ☐速度 ☐渲染 ☐内容 | | ☐ |
| 2 | | ☐速度 ☐渲染 ☐内容 | | ☐ |
| 3 | | ☐速度 ☐渲染 ☐内容 | | ☐ |

### 5.3 归类

- [ ] 速度问题 → Day 6
- [ ] 渲染/404 → 立刻修（记 commit）
- [ ] 内容建议 → 记进 backlog，不阻塞上线

**Day 5 验收**：☐ 至少 5 人访问 ☐ 无 P0 级（打不开/白屏）反馈

---

## Day 6 — 优化（1 小时）

### 6.1 按实测结果选优化项

**如果某运营商慢（>5s）**

- [ ] A/B 对比：把 Cloudflare 的 URL 也发给该运营商用户，看哪个快
- [ ] 若国内访问慢 → 自定义域名 + 分运营商解析 / IP 优选；或待有备案域名后切 EdgeOne 国内节点
- [ ] 两家都慢 → 说明不是平台问题，看 6.2

**如果首屏慢（>3s）**

- [ ] 检查构建产物体积：`du -sh .vitepress/dist`
  - 主要大头是 `assets/chunks/@localSearchIndexroot.*.js`（2.3 MB）—— 这是站内搜索索引
- [ ] 选项 A：接受（VitePress 会懒加载，首屏实际只拉一小部分）
- [ ] 选项 B：关闭 local search 换成 Algolia（需申请，免费）—— 改动大，不建议初期做

**如果图表多导致慢**

- [ ] SVG 已是矢量，体积可控（最大 278 KB）
- [ ] 检查是否某页挂了 20+ 张图，考虑拆页

### 6.2 通用优化项（都值得做）

- [ ] 确认 Cloudflare 已开启 HTTPS（默认开；强制 HTTPS 在 SSL/TLS → Edge Certificates 设）
- [ ] 确认 `Cache-Control` 对 `assets/` 长期缓存（VitePress 默认带 hash 文件名，安全）
- [ ] Cloudflare 默认已启用 Brotli 压缩，无需额外配置
- [ ] 给 `<head>` 加 favicon（已有 `/favicon.svg`）

### 6.3 体验优化（可选）

- [ ] 首页加一个"开始学习"按钮指向第一章
- [ ] 每章底部加"上一章/下一章"已有，确认生效
- [ ] 移动端侧边栏折叠正常

**Day 6 验收**：☐ 三大运营商首屏均 < 5s ☐ 已开智能压缩

---

## Day 7 — 正式发布与沉淀（1 小时）

### 7.1 对外发布

渠道（按你的场景选）：

- [ ] 朋友圈 / 微信群
- [ ] 知乎 / 掘金 / 公众号（写篇"我做了个量化学习站"）
- [ ] 量化社区（聚宽、米筐、BigQuant 论坛）
- [ ] GitHub 仓库加 README + topic，让搜索引擎收录
- [ ] 提交到几个导航站（如"程序员的网址导航"）

发布文案要点：
> 强调三点：**全**（122 章覆盖全链路）、**可运行**（439 个案例有真实输出）、**免费无广告**。

### 7.2 补 README

- [ ] 仓库根目录 `README.md` 补充：项目介绍、在线地址、本地启动方式、目录结构、License
- [ ] 选个开源协议：代码 MIT + 内容 CC-BY-SA 4.0
- [ ] push

### 7.3 复盘：更新项目文档

- [ ] 在 `_reports/WORK-REPORT.md` 追加一节「线上部署实录」：实际耗时、踩的坑、实际访问数据
- [ ] 更新 `_reports/DEPLOY-PRD.md` 的决策表：把"推荐"改成"已选"
- [ ] 更新 `.workbuddy/memory/` 记录部署相关信息（URL、token 位置、灾备地址）

### 7.4 建立长期维护节奏

| 频率 | 动作 |
|---|---|
| 每次改内容 | 改 md →（改了代码块则 `npm run precompute`）→ commit → push → 自动上线 |
| 每周 | 看一眼 UptimeRobot 报表 |
| 每月 | 看统计：访问量、热门章节；检查 Actions 额度 |
| 每季度 | 检查平台免费政策是否变化；确认灾备镜像还能访问 |

**Day 7 验收**：☐ 已对外发布 ☐ README 补齐 ☐ 复盘文档已更新

---

## 附录 A — 紧急回滚

**最优先级：平台控制台回滚（30 秒）**

1. 打开 <https://dash.cloudflare.com> → Workers & Pages → 项目 → Deployments
2. **部署记录**（Deployments）
3. 找到上一个成功的版本 → 点「回滚」/「Rollback」

**次选：git revert**

```bash
git revert HEAD
git push
```

**末选：切灾备**

把 `https://________.pages.dev` 发给用户。

---

## 附录 B — 关键速查

| 项目 | 值 |
|---|---|
| 本地工程路径 | `D:\AI\study\quant` |
| GitHub 仓库 | `https://github.com/______/quant-course` |
| 主站 URL | `https://quant-course.pages.dev` |
| 灾备 URL | `https://________.pages.dev` |
| Cloudflare 控制台 | <https://dash.cloudflare.com> |
| Cloudflare 控制台 | <https://dash.cloudflare.com> |
| GitHub Actions | `https://github.com/______/quant-course/actions` |
| 本地构建 | `npm run build` |
| 只重跑预计算 | `npm run precompute && python scripts/build-code-index.py` |
| 重建离线 HTML | `npm run offline` |

---

## 附录 C — 决策记录

| 日期 | 决策 | 选择 | 理由 |
|---|---|---|---|
| 2026-09-08（09-10 改判） | 部署平台 | **Cloudflare Pages** | EdgeOne 系统域名国内 401；Cloudflare 自构建 2GB OOM → 改走 Actions 构建 + Wrangler 推送 |
| | 仓库可见性 | | |
| | 是否提交 public/code | | |
| | 域名策略 | 先用 `*.pages.dev` | 跑 3-6 个月再考虑买域名 |
| | | | |

---

> Checklist 结束。操作细节查 `DEPLOY.md`，平台选型理由查 `_reports/DEPLOY-PRD.md`。
