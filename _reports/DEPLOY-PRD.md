# QuantLab 部署 PRD(Product Requirements Document)

> 文档版本:v2.0 · 2026-09-10(**已实施并上线,按实战结果校正**)
> 作者:主理人 + AI 协作者
> 状态:**已上线** — <https://quant-course.pages.dev>
> 关联文档:`_reports/WORK-REPORT.md`、`DEPLOY.md`(操作手册)
>
> **v2.0 主要修订**:原定 EdgeOne Pages 为主站,实战后**改判** ——
> ①EdgeOne 系统域名受加速区域限制,国内访问 401(仅 3 小时预览链接有效);
> ②Cloudflare 免费构建容器仅 2GB 内存,自构建必 OOM。
> 最终采用:**GitHub Actions 构建 + Wrangler 推送 → Cloudflare Pages 分发,平台零构建**。

---

## 0. 一页摘要(Executive Summary)

把 `D:\AI\study\quant\` 这个量化交易学习站部署到**国内可访问、稳定、免费、不备案**的线上环境。

**核心方案(实战定稿)**:**GitHub Actions 构建 + Wrangler 推送 → Cloudflare Pages 分发**。
平台侧**零构建** —— 只负责收产物、分发,不跑 `npm install`、不跑 `vitepress build`。

**核心约束**:
- 国内可访问(用户主要在中国大陆)
- 完全免费(个人非营利项目)
- 不需要 ICP 备案
- Git 自动化部署,无人工干预
- 失败 5 分钟内可回滚

**为什么不是原定的 EdgeOne(2026-09-10 实测改判)**:

| 原判断 | 实战结果 |
|---|---|
| EdgeOne 国际版免备案、国内可直连 | ❌ 系统分配的 `*.edgeone.dev` 受**加速区域**限制:含大陆区仅 3 小时预览链接有效;不含大陆区则国内直接 **401** |
| Cloudflare 作灾备 | ✅ **升为主站** —— `*.pages.dev` 长期有效、免备案 |
| 平台可从源码构建 | ❌ Cloudflare 免费容器 2 vCPU / **2 GB RAM**,本站 122 章全量构建**必 OOM**(实测 2052 MB 崩溃);EdgeOne 容器无 Python |

**实际达成**:
- 79 MB 构建产物 → Cloudflare 全球 CDN
- Actions 全绿 2m 33s,**503 个预计算产物零丢失**
- push 即自动上线,无需人工干预

---

## 1. 背景与目标

### 1.1 背景

QuantLab 是一个 122 章、24 万字、439 个 Python 案例的 VitePress 学习站。当前只在本地有三种产物(线上 dist、portable、离线 HTML),用户无法直接通过 URL 访问。

**当前痛点**:
- 想分享给同事/朋友必须发文件,微信 19.3MB 单文件勉强能传但慢
- 在公司内网无法跑 node 时,同事访问不到
- 没有"公开 URL"对外引流
- 章节更新无法推送

### 1.2 目标

| 目标 | 衡量指标 | 优先级 |
|---|---|---|
| 国内可访问 | 95% 用户首屏 < 3s | P0 |
| 永久免费 | 单账户不超免费额度 | P0 |
| 自动部署 | push 后 5 分钟内新版本上线 | P0 |
| 不需备案 | 上线前不需 ICP 流程 | P0 |
| 稳定运行 | 月可用性 > 99% | P1 |
| 易维护 | 部署文档任何人能看懂 | P1 |

### 1.3 非目标(明确不做)

- **不做实名认证/ICP 备案**:个人项目、个人非营利;备案需 15-30 天且流程复杂
- **不做自定义域名绑定(初期)**:Cloudflare 自带 `*.pages.dev` 子域名长期有效且免备案(已用 `quant-course.pages.dev` 上线),后续如要 `quantlab.xinming.cn` 再说
- **不做边缘函数**:静态站点足够,SSR/Vercel Functions 不在范围
- **不做付费 CDN**:免费额度足够(5GB 总项目大小,本工程构建产物 79MB 完全够)
- **不做账号系统/评论**:纯只读内容站

---

## 2. 平台选型

### 2.1 候选平台对比(2026-09 现状)

| 平台 | 免费额度 | 国内访问 | 备案要求 | Git 部署 | 综合评分 |
|---|---|---|---|---|---|
| **Cloudflare Pages** | 100 站点、500 构建/月 | ★★★(联通 300ms+,需 IP 优选) | 否 | ✅ GitHub | ✅ **已采用并上线** |
| EdgeOne Pages 国际版 | 5GB 项目大小、无限流量 | ★(系统域名国内 401 / 仅 3 小时预览有效) | 否 | ✅ GitHub | 暂缓(待备案域名) |
| Vercel | 100GB 带宽/月 | ★★(`*.vercel.app` 国内常被屏蔽) | 否 | ✅ GitHub | 不推荐 |
| Netlify | 100GB 带宽/月 | ★★(类似 Vercel) | 否 | ✅ GitHub | 不推荐 |
| GitHub Pages | 1GB、100GB 带宽 | ★(国内常被墙) | 否 | ✅ GitHub | 不推荐 |
| 腾讯云 COS+CDN | 50GB COS | ★★★★★(国内极快) | **是** | 手动上传 | 受备案限制 |
| 阿里云 OSS+CDN | 40GB OSS | ★★★★★(国内极快) | **是** | 手动上传 | 受备案限制 |
| Gitee Pages | 5GB | ★★★(国内快) | 否 | ✅ Gitee | Gitee Pages 已下线 |

**数据来源**:
- EdgeOne Pages:腾讯云官方文档 + 多个独立博主实测
- Cloudflare Pages:用户反馈联通线路晚高峰 800ms+
- Vercel/Netlify:`*.vercel.app`/`*.netlify.app` 域名被 DNS 污染

### 2.2 ⚠️ 决定成败的隐藏约束：加速区域（2026-09-08 实测修正）

**这是选型时最容易漏掉、但直接决定"能不能访问"的一项。** EdgeOne Pages 创建项目时必须选加速区域，
区域决定了系统分配的域名能否长期公开访问（官方文档 `pages.edgeone.ai/zh/document/domain-overview`）：

| 加速区域 | 系统分配的域名（`*.edgeone.dev` 等） | 绑定自定义域名 |
|---|---|---|
| **中国大陆可用区** | ❌ **只能用控制台「预览」按钮生成的链接，有效期 3 小时，超时返回 401** | 需工信部备案 |
| **全球可用区（含中国大陆）** | ❌ 同上，仅 3 小时预览链接 | 需工信部备案 |
| **全球可用区（不含中国大陆）** | ❌ **中国大陆网络返回 401**（海外正常） | ✅ **无需备案** |

**实测证据**（2026-09-08，`quant-course.edgeone.dev`）：

```http
HTTP/1.1 401 Authorization Required
X-EOP-MSG: eo_time missing
Server: edgeone makers
```
响应体：
```
401: UNAUTHORIZED
Access Restricted or Authentication Expired.
Site Visitor: Please contact the site administrator to obtain a valid access link.
Site Owner: Click "Preview" in the console for a new link.
            For "Global (MLC excluded)" projects, check your network environment.
```

**三条推论（推翻了初版 PRD 的乐观假设）**：

1. **「免备案 + 国内可访问」在 EdgeOne Pages 上不成立**。不选中国大陆区→国内 401；
   选了→只能靠 3 小时预览链接临时访问，等于不能公开分享。
2. **初版 PRD 写的「国际版免备案、国内 200ms」是错的**，那是把「国际版账号（edgeone.ai 控制台）」
   与「加速区域不含中国大陆」两件事混为一谈。账号国际版只解决"不强制实名"，不解决域名访问限制。
3. **唯一稳定的公开访问路径 = 绑定自定义域名**。若域名已备案可任选区域；
   若未备案只能选「全球（不含中国大陆）」，国内仍会被拦。

**决策影响**：本项目的上线方式必须重新评估，见 §2.4。

### 2.3 选 EdgeOne Pages 的理由（在"有已备案域名"前提下方才成立）

1. **国内访问优于 Cloudflare**：EdgeOne 亚洲节点对联通/移动做专门优化，实测延迟 ~200ms，而 Cloudflare 联通线路经常 800ms+（实测来自迁移博主）
2. **完全免费**：5GB 项目大小，本工程 79MB 远低于上限
3. **GitHub 集成完善**：与 Cloudflare Pages 逻辑一致，迁移成本低

> ⚠️ 上述优势的前提是**绑定一个已备案的自定义域名**。仅用系统分配域名时，
> 无论是 3 小时预览链接还是国内 401，都不满足"培训站点长期可访问"的目标。

### 2.4 修正后的方案选择

| 方案 | 前提 | 国内访问 | 成本 | 结论 |
|---|---|---|---|---|
| **A. EdgeOne + 已备案自定义域名** | 有备案域名 | ★★★★★ | ¥0（域名已有） | 暂缓（待有备案域名） |
| **B. Cloudflare Pages 直接上线** | 无 | ★★★（联通晚高峰可能慢） | ¥0 | ✅ **已选定（2026-09-08）** |
| C. EdgeOne + 未备案域名 | 已购域名未备案 | ❌ 401 | ¥0 | 不可行 |
| D. 接受 3 小时预览链接 | 无 | 时断时续 | ¥0 | 仅临时演示 |
| E. 走备案流程 | 有域名 + 愿意等 10-20 天 | ★★★★★ | 域名费 | 长期备选 |

**决策记录**：2026-09-08 用户选定 **方案 B（Cloudflare Pages）**；
2026-09-10 **完成上线**，线上地址 <https://quant-course.pages.dev>。
EdgeOne 项目保留，待日后如有已备案域名可切回方案 A。

### 2.5 ⚠️ 实施要点（2026-09-10 实战校正：推翻「Git 集成」）

原计划「Cloudflare Git 集成 + dist 分支 + 构建命令留空」**实战失败三次，已废弃**：

| 尝试 | 结果 |
|---|---|
| Git 集成 + `dist` 分支 | ❌ `npm ci` EUSAGE（dist 分支没有 package.json / lock）；且新版界面**无 Production branch 编辑项**，分支建错即锁死 |
| Git 集成 + `master` + `npm install` | ❌ **OOM**：堆内存涨到 2052 MB 崩溃。Cloudflare 免费容器只有 **2GB RAM** |

**定稿做法：Actions 构建 + Wrangler 推送（平台零构建）**

1. **不能用控制台拖拽上传** —— 拖拽上限 1,000 个文件，本工程产物 4,393 个，超限 4 倍多。
   （Wrangler CLI 上限 20,000，够用。）单文件上限 25 MiB 不构成问题（最大 2.3 MiB），
   **卡点是文件数量不是体积**。
2. **构建全部放在 GitHub Actions**（`ubuntu-latest`，**7GB 内存** + 有 Python），约 100 秒完成；
   检测到仓库已有 ≥480 个预计算产物就跳过 precompute（20min → 4min）。
3. **产物用 `wrangler pages deploy` 推送**，Cloudflare 只分发、不构建。
   凭证走仓库 Secret：`CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`。
4. **`gh` CLI 在本机不可用**（443 被墙），改用**空 commit + SSH push** 触发部署。

### 2.6 Cloudflare Pages（实际主站，原「灾备」）

Cloudflare 已从「备选灾备」**升为实际主站**：

- `*.pages.dev` 域名长期有效、免备案、无 3 小时限制（相对 EdgeOne 的决定性优势）
- 无限带宽
- 联通用户可通过 IP 优选改善体验（社区方案成熟）
- **唯一缺点**：免费版无国内节点，联通线路晚高峰可能慢；个别地区有被墙概率

---

## 3. 部署架构

### 3.1 整体架构

```
┌─────────────┐
│  GitHub Repo │  ←  源代码(guide/, components/, scripts/, package.json)
└──────┬──────┘
       │ git push main
       ▼
┌──────────────────┐
│ EdgeOne Pages CI │  ←  自动触发构建
│  环境:Node 20    │     命令:npm ci && npm run build
│                  │     输出:.vitepress/dist
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  EdgeOne CDN     │  ←  全球边缘节点(亚洲 2300+,全球 3200+)
│  quantlab.edgeone.app  │     国内访问 200ms+
└──────┬───────────┘
       │
       ▼
  ┌──────────┐
  │  用户浏览器 │
  └──────────┘
```

### 3.2 与已有工程的契合度

工程已有的 `package.json` 已有 `build` 命令:

```json
{
  "scripts": {
    "dev": "vitepress dev",
    "build": "node scripts/extract-py-fences.mjs && node scripts/precompute-py-outputs.mjs && python scripts/build-code-index.py && vitepress build && node scripts/relativize-dist.mjs",
    "precompute": "node scripts/precompute-py-outputs.mjs",
    "offline": "python scripts/build-single-html.py"
  }
}
```

**EdgeOne Pages 部署设置**:
- Build 命令:`npm run build`
- Build 输出目录:`.vitepress/dist`
- Node 版本:`20`(与本地一致)
- 环境变量:无需

**不需要任何工程代码改动**——这是 SSG 的优势。

---

## 4. CI/CD 流程

### 4.1 自动化部署流程

```
开发者 push 到 main
    ↓
GitHub 触发 webhook 到 EdgeOne Pages
    ↓
EdgeOne Pages 在隔离容器中:
    1. git clone (深度 1)
    2. npm ci (安装依赖)
    3. npm run build (含 precompute)
    4. 把 .vitepress/dist 部署到 CDN
    ↓
CDN 节点更新(30 秒内全球生效)
    ↓
用户访问 https://quantlab.edgeone.app 看到最新版本
```

### 4.2 部署命令详解

| 步骤 | 时间 | 失败处理 |
|---|---|---|
| git clone | 5-10s | 网络问题 → 重试 3 次,失败则构建报错 |
| npm ci | 30-60s | 锁文件不一致 → 构建报错,提示"npm install 重生成 lockfile" |
| extract-py-fences | 60-30s | 极端罕见,可能是 markdown 解析失败 |
| precompute-py-outputs | 8-10 min | Python 包缺失 → 单个 fence 失败不影响整体,标 note |
| vitepress build | 3-5 min | 配置错误或语法错误 → 立即构建失败,通知开发者 |
| relativize-dist | 5-10s | 路由结构变化时 |

**总构建时间**:约 12-20 分钟,EdgeOne Pages 默认超时 30 分钟,留有余量。

### 4.3 预计算优化的可选改进(若构建超 30 分钟)

- 增量构建:只对 git diff 中变化的 fence 重跑
- 并发数从 8 提升到 16(EdgeOne Pages 容器资源足够)
- 缓存 `_auto/` 目录(下次构建直接复用未变化的)

---

## 5. 域名与品牌

### 5.1 初期方案(零成本)

- 子域名:`quantlab.edgeone.app`(EdgeOne Pages 自动分配)
- 优势:免费、自动 HTTPS、立即可用
- 缺点:品牌识别度弱(`edgeone.app` 字样)、SEO 友好度低

### 5.2 中期方案(可选,如预算允许)

- 备案后绑定:`quantlab.xinming.cn` 或 `quantlab.cn`
- 需要 ICP 备案(15-30 天)
- 需要 EdgeOne 国内版(实名认证 + 备案)
- 优势:品牌识别度高、SEO 友好、可在国内版走国内 CDN(更快)

### 5.3 长期方案

- 购买国际域名:`quantlab.studio` / `quantlab.dev` / `quantlab.academy`(约 $10-15/年)
- 任意 DNS 服务商(Cloudflare / DNSPod)
- 仍走 EdgeOne Pages 国际版(免备案)

**建议**:先用 5.1 跑 3-6 个月,确认访问量稳定后再考虑 5.3。**不推荐 5.2**(备案流程太长,且失去免备案优势)。

---

## 6. 监控与运维

### 6.1 监控项

| 指标 | 工具 | 告警阈值 |
|---|---|---|
| 部署状态 | EdgeOne Pages Dashboard | 构建失败 → 邮件通知 |
| 可用性 | EdgeOne Pages 内置监控 | 月不可用 > 1% |
| 流量 | EdgeOne Pages Dashboard | 超 80% 限额告警(目前基本不可能) |
| 国内访问延迟 | 第三方工具(UptimeRobot / Better Uptime) | 联通/移动 > 500ms |

### 6.2 回滚策略

```
发现严重问题
    ↓
    ├─ A. 立即在 EdgeOne Pages 控制台点击"回滚到上一个版本"(30 秒生效)
    │
    └─ B. git revert 修复 + push main(15-20 分钟生效)
```

**默认 A**;B 用于需要保留修复记录的场景。

### 6.3 故障应对预案

| 故障 | 表现 | 应对 |
|---|---|---|
| EdgeOne Pages 服务故障 | 全球不可访问 | 切换到 Cloudflare Pages 镜像(DNS CNAME 改指) |
| GitHub 故障 | 无法 push | 在 EdgeOne Pages 直接上传 .vitepress/dist 包 |
| 联通网络恶化 | 联通用户访问慢 | 配置 Cloudflare Pages + IP 优选 |
| 构建超时 | precompute 太慢 | 启用增量构建 |

---

## 7. 安全与合规

### 7.1 安全措施

- **HTTPS 自动**:EdgeOne Pages 默认提供,Let's Encrypt 证书自动续期
- **DDoS 防护**:EdgeOne 内置基础 DDoS 防护(免费版包含)
- **WAF 规则**:基础 CC 攻击防护(自适应频控)
- **不暴露源码**:GitHub 仓库可设为 public(教学性内容本就希望公开)或 private(若含个人敏感)

### 7.2 合规

- **不收录个人隐私**:课程无登录、无评论、不收集任何用户信息
- **不提供投资建议**:每章开头明确声明"本文为教学用途,不构成投资建议"
- **不违反金融监管**:不展示实盘交易、不提供量化策略代码用于真实交易(仅教学框架)
- **开源协议**:整站 MIT(代码) + CC-BY-SA 4.0(内容)

### 7.3 风险

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| 内容被误读为投资建议 | 低 | 法律 | 每章免责声明 + 站点底部固定声明 |
| 被恶意爬取 | 中 | 资源浪费 | EdgeOne 内置 CC 防护足够 |
| 域名被墙 | 低 | 用户流失 | 域名不备案无墙风险(国际版) |
| 学术不端 | 低 | 信誉 | 文档顶部明确引用来源,延伸阅读列出原始文献 |

---

## 8. 成本估算

| 项 | 费用 | 周期 |
|---|---|---|
| EdgeOne Pages 国际版 | ¥0 | 永久 |
| GitHub 仓库(public) | ¥0 | 永久 |
| Cloudflare Pages(灾备) | ¥0 | 永久 |
| 域名(若启用 5.3) | ¥80 | 首年 |
| **总计** | **¥0(初期) / ¥80/年(中期)** | |

---

## 9. 里程碑与时间线

| 阶段 | 时间 | 产出 | 验收标准 |
|---|---|---|---|
| M1:准备 | Day 1 | GitHub 仓库就绪、EdgeOne 账号开通 | 仓库可正常 push |
| M2:首次部署 | Day 2 | 站点上线,公开 URL 可访问 | 国内访问 < 3s,所有页面无 404 |
| M3:验证 | Day 3-5 | 邀请 5-10 位内测用户体验 | 用户能流畅访问所有 122 章 |
| M4:优化 | Day 6-7 | 接入监控、CDN 缓存调优 | 可用性 > 99%,延迟 < 300ms |
| M5:正式发布 | Day 8 | 对外宣传(朋友圈、量化社区) | 日访问 > 50 |
| M6:迭代 | 持续 | 根据反馈迭代内容 | 用户满意度 > 80% |

---

## 10. 验收标准

### 10.1 功能验收

> **2026-09-10 实测**:已上线 <https://quant-course.pages.dev>。
> 抽样验证通过:1.3 凯利案例结果表格 + 科学计数法 + SVG 图表、首页 6 大模块与交互组件、
> **503 个预计算产物无「暂无运行结果」**。全量 122 章 / 439 案例建议按下面清单复核。

- [ ] 所有 122 章均可访问
- [ ] 所有 439 个代码案例都有运行结果(蓝色 note 或真实输出)
- [ ] 所有 23 个交互组件(ECharts/Vue)正常工作
- [ ] 站内搜索可用(VitePress local search)
- [ ] 移动端响应式正确

### 10.2 性能验收

- [ ] 首屏加载 < 3s(国内主要运营商)
- [ ] 章节切换 < 1s
- [ ] PDF 下载(如启用)< 10s

### 10.3 可用性验收

- [ ] 7×24 可访问
- [ ] 月不可用 < 1%
- [ ] 部署失败 5 分钟内发现并通知

---

## 11. 风险与决策点

### 11.1 主要决策点(需用户确认)

| 决策 | 选项 | 推荐 |
|---|---|---|
| 平台 | A. EdgeOne Pages B. Cloudflare Pages | **B**(已决策 2026-09-08,已上线 2026-09-10) |
| 域名 | A. `*.edgeone.app` 子域名 B. 购买国际域名 | **A 起步** |
| 仓库可见性 | A. Public B. Private | **A**(教学内容本就希望公开) |
| 是否做灾备 | A. 是 B. 否 | **A**(Cloudflare Pages 几乎零成本) |
| 是否立即做监控 | A. 是 B. 否 | **B 起步**(先观察,有需要再加) |

### 11.2 不可控风险

- EdgeOne Pages 国际版政策变化(如开始收费或关闭)
- GitHub 国内访问受限持续恶化
- Python 依赖(如 numba)未来版本不再兼容 Linux 容器环境

---

## 12. 附录

### 12.1 ⚠️ 已废弃:让平台从源码构建(EdgeOne / Cloudflare 都行不通)

初版写的「平台导入仓库 → 构建命令 `npm run build` → 输出 `.vitepress/dist`」
**实战证明不可行**,两个致命原因:

1. **容器没有 Python** —— 跑不了 precompute,439 个案例的运行结果会全丢。
   (本站虽已把 503 个产物提交进仓库绕开了这点,但见第 2 条。)
2. **内存不够** —— Cloudflare 免费构建实例只有 **2GB RAM**,
   本站 122 章全量构建实测**堆内存涨到 2052 MB 时 OOM 崩溃**。

> EdgeOne 另有一层限制:系统分配的 `*.edgeone.dev` 要么只有 3 小时预览链接,
> 要么国内直接 401。故 EdgeOne 整体**暂缓**,待有已备案域名再启用。

### 12.2 ✅ 实际采用:Cloudflare Pages 部署步骤(Actions 构建 + Wrangler 推送)

```
1. Cloudflare 控制台 → My Profile → API Tokens → Create Token
   模板选 "Edit Cloudflare Workers" → 得到 CLOUDFLARE_API_TOKEN
2. 控制台首页右侧栏复制 Account ID(或看地址栏 dash.cloudflare.com/<32位>)
3. GitHub 仓库 → Settings → Secrets and variables → Actions:
   - Secrets:   CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID
   - Variables: CLOUDFLARE_PROJECT = quant-course
4. 确认仓库已有 wrangler.toml(assets 指向 .vitepress/dist)
5. 删掉之前建的 Cloudflare Git 集成项目(避免两条部署路径并存)
6. 触发部署(本机 gh 不可用,走 SSH):
     git commit --allow-empty -m "ci: 触发部署" && git push origin master
7. Actions 自动跑: npm ci → vitepress build → wrangler pages deploy
8. 约 2-3 分钟后得到 https://quant-course.pages.dev
```

> 日常更新只需 `git push`,全自动。注意:改了 ```python 代码块要先本地重跑预计算再提交。

### 12.3 参考资料

- EdgeOne Pages 官方文档:https://edgeone.ai/document
- 迁移实战博客:https://iliu.org/posts/migrated-my-blog-to-edgeone-pages/
- Vue3 组件库部署案例:https://developer.cloud.tencent.com/article/2560845
- Cloudflare Pages 文档:https://developers.cloudflare.com/pages

---

## 13. 评审签字

| 角色 | 姓名 | 签字 | 日期 |
|---|---|---|---|
| 产品负责人 | 辛浩铭 | ✅ 已确认上线 | 2026-09-10 |
| 技术评审 | AI 协作者 | ✅ 方案设计 + 实战校正(v2.0) | 2026-09-10 |
| 运维负责人 | GitHub Actions(自动化) | ✅ 已跑通,全绿 | 2026-09-10 |

---

> 文档结束。如有修改请直接在 PR 中 review 并标注。