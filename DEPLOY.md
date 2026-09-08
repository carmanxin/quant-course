# QuantLab 上线部署手册

> 版本 v1.0 · 2026-09-08
> 面向：主理人本人（以及未来接手这个工程的人）
> 目标：把 `D:\AI\study\quant\` 这个本地站点变成一个任何人打开链接就能访问的线上网站
> 前置文档：`_reports/DEPLOY-PRD.md`（为什么选这个平台）、`_reports/WORK-REPORT.md`（工程全貌）

---

## 0. 三分钟看清全貌

### 0.1 这个站的特殊之处（决定了部署方式）

QuantLab 不是普通的静态站。它的 439 个 Python 案例的**运行结果**（数字、表格、图表）是**在你本机提前跑出来的**，不是浏览器里跑的。

```
你本机                                     线上
──────                                   ────
npm run build
  ├─ extract-py-fences   抽取代码块
  ├─ precompute          ← Python 真跑一遍，结果存成 JSON/SVG
  ├─ build-code-index    建索引
  └─ vitepress build     ← 把结果"烤"进 HTML
       ↓
  .vitepress/dist  ──────── 上传 ────────→  CDN → 用户浏览器
```

**结论**：线上**只需要一个能放静态文件的地方**，不需要 Python、不需要 Node、不需要服务器。这既是好事（免费托管都能用），也是约束（**必须在有 Python 的地方构建**）。

### 0.2 三条路线，按需选一条

| 路线 | 做法 | 耗时 | 适合 |
|---|---|---|---|
| **A. GitHub Actions 自动部署**（推荐） | push 代码 → 自动构建 → 自动上线 | 首次 40 分钟，之后每次 push 全自动 | 长期维护 |
| **B. 控制台手动传 ZIP** | 本地 `npm run build` → 打包 → 拖上传 | 首次 15 分钟，每次更新 5 分钟 | 只想快点上线看看 |
| **C. 平台 Git 集成** | 平台直接拉仓库自己构建 | 首次 30 分钟 | **不推荐**（见 0.3） |

### 0.3 为什么不推荐 C（平台自己构建）

EdgeOne Pages 和 Cloudflare Pages 的构建容器里**没有 Python**，跑不了 `precompute`，439 个案例的运行结果会全部丢失，页面只剩代码没有输出。

路线 A 之所以可行，是因为 **GitHub Actions 的 runner 有 Python**，我们在那里构建完，再把成品交给平台。

> 如果你确实想用 C，必须先在本地跑好 `precompute`，把 `public/code/` 产物提交进仓库，然后把平台的构建命令改成 `npx vitepress build`（跳过 precompute）。可行，但不如 A 省事。

---

## 0.5 最快路径：让 AI 代配置

本机已装 **GitHub CLI (`gh` v2.97)**，所以绝大部分操作 AI 可以直接跑命令完成。
你只需要做 **4 件必须本人做的事**（都涉及账号/授权/密钥，AI 无法代劳），合计约 15 分钟：

| # | 你要做的 | 为什么必须你做 | 大约 |
|---|---|---|---|
| 1 | 注册 GitHub 账号（已有则跳过） | 邮箱验证 | 3 min |
| 2 | 注册 EdgeOne 账号 <https://edgeone.ai> | 邮箱验证 | 3 min |
| 3 | 本地跑一次 `gh auth login`（浏览器点授权） | OAuth 授权 | 2 min |
| 4 | 生成 EdgeOne API Token 并交给 AI / 自己填进 Secret | 密钥只显示一次 | 3 min |

**第 3 步之后**，AI 可以接管这些（你不用管）：

```bash
gh repo create quant-course --public --source=. --push   # 建仓库 + push
gh secret set EDGEONE_API_TOKEN                          # 写密钥
gh workflow run deploy.yml                               # 触发首次构建
gh run watch                                             # 盯日志
```

**最省事的协作方式**：

1. 你先完成上面 4 步
2. 告诉 AI：「GitHub 用户名是 XXX，EdgeOne Token 是 YYY，开始部署」
3. AI 跑完剩下的，把线上 URL 交给你

> **关于 Token 的安全**：EdgeOne API Token 只能部署 Pages 项目，泄露风险有限，但仍是凭据。
> 更稳妥的做法是**你自己填进 GitHub Secret**（网页点 3 下），然后把 `gh auth login` 之后的活交给 AI。
> 这样 AI 全程不接触你的任何密钥。

---

## 1. 准备工作

### 1.1 检查本地状态

打开 Git Bash，进入工程目录：

```bash
cd /d/AI/study/quant
git status --porcelain | wc -l     # 看有多少未提交改动
git remote -v                      # 看有没有远程仓库（现在是空的）
git branch --show-current          # 当前分支（现在是 master）
```

> ⚠️ 当前有 **665 个未提交改动**。路线 A 和 C 都要求代码提交到 GitHub，先别急，第 2 步会处理。

### 1.2 申请账号（两个，都是免费、免备案、免绑卡）

**① GitHub**（已有可跳过）
- 地址 <https://github.com/signup>
- 只需邮箱

**② EdgeOne Pages 国际版**
- 地址 **<https://edgeone.ai>**（注意是 `.ai`，不是腾讯云国内的 `console.cloud.tencent.com`）
- 国际版 = 海外节点 = **免 ICP 备案**
- 注册只需邮箱，不需要实名、不需要绑卡

> ⚠️ 千万别走腾讯云国内控制台（`console.cloud.tencent.com/edgeone/pages`）建项目——国内版会要求 ICP 备案，未备案会被回 401 拒绝访问。

### 1.3 拿 EdgeOne API Token

1. 登录 <https://edgeone.ai> → 右上角头像 → **API Token**
2. 点 **Create Token**，名字随便填（如 `github-actions`）
3. 复制生成的 token（**只显示一次**，先粘到记事本里）

---

## 2. 路线 A：GitHub Actions 自动部署（推荐）

### 步骤 A1 — 把代码推到 GitHub

**A1.1 在 GitHub 建空仓库**

1. <https://github.com/new>
2. Repository name：`quant-course`
3. 选 **Public**（public 仓库的 Actions 时长免费 unlimited；private 每月只有 2000 分钟，本工程单次构建 20 分钟，很费）
   > 如果内容不想公开，选 Private 也行，注意额度
4. **不要**勾选 "Add a README"、"Add .gitignore"、"Choose a license"（本地已有）
5. 点 Create repository

**A1.2 本地提交并推送**

```bash
cd /d/AI/study/quant

# 1) 确认 .gitignore 已排除无关产物（已配置好，再确认一次）
cat .gitignore

# 2) 提交全部改动
git add -A
git commit -m "chore: sync local work before online deployment"

# 3) 关联远程仓库（把 <你的用户名> 换成 GitHub 用户名）
git remote add origin https://github.com/<你的用户名>/quant-course.git

# 4) 推送
git branch -M main
git push -u origin main
```

> 首次 push 会弹窗要 GitHub 账号密码。**密码要填 Personal Access Token**，不是登录密码：
> GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token → 勾 `repo` → 生成 → 复制。

**A1.3 确认推送完整**

```bash
git ls-files | wc -l          # 应该 > 259
ls .github/workflows/         # 应该有 deploy.yml
cat requirements-ci.txt | head -3
```

如果 `public/code/` 下的产物（4012 个文件）没被提交，CI 会自己跑 precompute（慢 20 分钟）。想让 CI 快一点，可以把产物也提交：

```bash
git add -f public/code
git commit -m "chore: commit precomputed python outputs"
git push
```

> 权衡：提交 `public/code`（19 MB）后 CI 构建从 ~20 分钟降到 ~4 分钟，且结果 100% 与本地一致；代价是仓库变大、每次改 md 后要记得本地重跑 precompute 再提交。**不做也能上线**，只是慢。

### 步骤 A2 — 配置仓库密钥

1. 打开 `https://github.com/<你的用户名>/quant-course/settings/secrets/actions`
2. 点 **New repository secret**
3. Name 填 `EDGEONE_API_TOKEN`，Value 粘贴 1.3 拿到的 token
4. 点 Add secret

（可选，灾备）再加两个：

| Name | Value 来源 |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Cloudflare → My Profile → API Tokens → Create Token → 模板选 "Edit Cloudflare Workers" |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 控制台首页右侧栏 Account ID |

> 没配的 secret 对应的部署步骤会自动跳过，不会让工作流失败。可以先把主站跑通，灾备以后再加。

### 步骤 A3 — 首次触发构建

1. 打开仓库的 **Actions** 标签页
2. 左侧选 **Build & Deploy**
3. 右侧点 **Run workflow** → 分支选 `main` → 点绿色 Run workflow
4. 点进正在跑的任务看日志

**各阶段耗时参考**：

| 阶段 | 耗时 | 说明 |
|---|---|---|
| 安装 Node 依赖 | 1-2 min | 有 npm cache |
| 安装 Python 依赖 | 2-3 min | 只在需要 precompute 时 |
| precompute | 8-15 min | **最慢**，有产物则跳过 |
| vitepress build | 3-5 min | |
| 部署 EdgeOne | 1-3 min | 上传 79 MB |

> 以后每次 `git push` 到 `main` 都会自动触发，不用再手动点。

### 步骤 A4 — 拿到网址

构建成功后：

1. 登录 <https://edgeone.ai> → 控制台 → **Pages**
2. 会看到一个名为 `quantlab` 的项目（CLI 自动创建的）
3. 点进去，访问链接形如 `https://quantlab-<随机串>.edgeone.app`
4. 也可以在 Actions 日志的 "Deploy to EdgeOne Pages" 步骤里找到输出 URL

**打开验证**：任意点 3 个章节，确认代码块的「运行结果」里有数字和图表，而不是空白。

---

## 3. 路线 B：手动传 ZIP（最快看到效果）

不想碰 Git 的话走这条。

### 步骤 B1 — 本地构建

```bash
cd /d/AI/study/quant
npm run build
```

> 约 15-25 分钟（precompute 占大头）。产物在 `.vitepress/dist`，79 MB。

如果只想重跑一次构建、跳过 precompute（产物已有）：

```bash
npx vitepress build
```

### 步骤 B2 — 打包

```bash
cd .vitepress/dist
zip -r ../../quantlab-dist.zip .
cd ../..
ls -lh quantlab-dist.zip
```

Windows 也可以用资源管理器：进 `.vitepress\dist` → 全选 → 右键「发送到 → 压缩(zipped)文件夹」。

> 上传限制：20000 个文件以内、单文件 25 MB 以内。本工程 4393 个文件、最大 2.3 MB，远低于限制。

### 步骤 B3 — 上传

1. 登录 <https://edgeone.ai> → 控制台 → Pages → **创建项目**
2. 选 **直接上传**（Direct Upload）
3. 填项目名 `quantlab`，加速区域选**全球（不含中国大陆）**或默认
4. 把 `quantlab-dist.zip` 拖进上传区
5. 点 **开始部署**，等 30-60 秒

> ⚠️ 直接上传创建的项目**以后无法切换成 Git 集成**。要自动化部署得另建项目。所以这只适合"先看看效果"，长期还是走路线 A。

### 步骤 B4 — 以后怎么更新

重新 `npm run build` → 打 ZIP → 控制台进这个项目 → **新建部署** → 拖新 ZIP。

---

## 4. 路线 C：平台 Git 集成（需要提前提交产物）

仅在你**已经把 `public/code/` 提交进仓库**的前提下可用（否则运行结果全丢）。

EdgeOne Pages 控制台 → 创建项目 → **导入 Git 仓库** → 授权 GitHub → 选 `quant-course`：

| 配置项 | 值 |
|---|---|
| Framework | VitePress（没有就选 Other） |
| Build command | `npm ci && npx vitepress build` |
| Output directory | `.vitepress/dist` |
| Node version | 22 |
| 分支 | `main` |

注意构建命令是 `npx vitepress build` 而**不是** `npm run build`——后者会触发 precompute，而平台容器没有 Python。

---

## 5. 灾备镜像：Cloudflare Pages

配好 `CLOUDFLARE_API_TOKEN` 和 `CLOUDFLARE_ACCOUNT_ID` 两个 secret 后，工作流会自动同步部署到 `https://quantlab.pages.dev`。

**什么时候用**：EdgeOne 出故障，或者你发现联通用户访问 EdgeOne 慢。

**切换方式**（如果有自定义域名）：把域名的 CNAME 从 EdgeOne 指到 `quantlab.pages.dev`，等 DNS 生效（5-30 分钟）。

如果没自定义域名，直接把 `quantlab.pages.dev` 这个链接发给用户即可。

---

## 6. 上线验收清单

打开线上网址，逐项检查：

**功能**

- [ ] 首页能打开，侧边栏 20 个模块都在
- [ ] 随机点 5 个章节，正文、公式、表格渲染正常
- [ ] 至少 3 个案例的「运行结果」里有**真实数字**（不是空白、不是"本段代码定义：…"）
- [ ] 至少 1 个案例的图表（SVG）显示出来
- [ ] 站内搜索能用（右上角）
- [ ] 手机浏览器打开，排版没乱

**性能**

- [ ] 首屏 < 3 秒
- [ ] 章节切换 < 1 秒
- [ ] 随便点 3 个页面都没有 404

**国内访问**（重要）

- [ ] 用手机 4G/5G（非 WiFi）打开试试
- [ ] 让一位联通用户、一位移动用户各试一次
- [ ] 如果都慢，考虑换 Cloudflare Pages 或加自定义域名 + IP 优选

**一键检查命令**（把 URL 换成你自己的）：

```bash
URL=https://quantlab.edgeone.app
curl -o /dev/null -s -w "首页: HTTP %{http_code}  %{time_total}s\n" $URL/
curl -o /dev/null -s -w "章节: HTTP %{http_code}  %{time_total}s\n" $URL/guide/m01-overview/1.3-quant-mindset.html
```

---

## 7. 日常更新流程

配好路线 A 之后，日常只需要三步：

```bash
cd /d/AI/study/quant

# 1. 改内容（编辑 guide/**/*.md）

# 2. 如果改了 Python 代码块，本地重跑一次预计算（否则线上的还是老结果）
npm run precompute
python scripts/build-code-index.py

# 3. 提交推送，剩下的交给 GitHub Actions
git add -A
git commit -m "docs: 更新 XX 章节"
git push
```

5-25 分钟后线上自动更新。

> **第 2 步容易忘**。判断规则：只要你改了 ```python 代码块里的内容，就必须重跑 precompute，否则页面上的"运行结果"和代码对不上。只改文字不用跑。

---

## 8. 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| Actions 在 precompute 步骤超时 | 503 个代码块在 2 核 runner 上跑不完 | 把 `public/code` 提交进仓库（CI 会自动跳过）；或调大 `timeout-minutes` |
| 部署后页面空白 | 路径用了绝对路径但部署在子目录 | 本项目就是绝对路径，确保部署在域名根目录；或用 `relativize-dist.mjs` 转相对路径 |
| 案例没有运行结果 | CI 里没跑 precompute 或跑失败了 | 看 Actions 日志里 precompute 那一步；本地跑一遍把产物提交 |
| EdgeOne 打开提示 401 / 未备案 | 用了腾讯云国内版 | 换 <https://edgeone.ai> 国际版 |
| 部署报 "project not found" | 项目名不匹配 | CLI 传了 `-n quantlab`，检查 `vars.EDGEONE_PROJECT` |
| `npx edgeone` 报命令不存在 | npm 拉包失败 | 重试；或在 workflow 里改成 `npm i -g edgeone && edgeone pages deploy ...` |
| 国内某些运营商打不开 | 国际版节点对某些线路不友好 | 切 Cloudflare Pages 对比；或上自定义域名做分运营商解析 |
| push 后 Actions 没触发 | 分支名不匹配 | workflow 监听 `master`/`main`；`git branch --show-current` 确认 |

---

## 9. 回滚

**方法 1 — 平台控制台回滚（最快，30 秒）**

EdgeOne Pages → 进项目 → **部署记录** → 找到上一个成功版本 → 点「回滚」。

**方法 2 — git revert（留记录）**

```bash
git revert HEAD
git push
```

等 Actions 跑完自动上线。

**方法 3 — 切灾备**

把 Cloudflare Pages 的链接发给用户，或者改 DNS 指向。

---

## 10. 后续可选动作

| 动作 | 成本 | 收益 |
|---|---|---|
| 买国际域名（如 `quantlab.studio`） | ¥80/年 | 品牌识别度、方便分享、可随时换平台 |
| 加 UptimeRobot 监控 | ¥0 | 站点挂了会发邮件 |
| 加 Google / 百度统计 | ¥0 | 知道有多少人看、看哪些章节 |
| ICP 备案 + 腾讯云国内版 | ¥0 但 15-30 天 | 国内访问最快，但失去"免备案"灵活性 |
| 开启增量 precompute | 开发 2 小时 | CI 从 20 分钟降到 3 分钟 |

---

## 附录：一键验证脚本

存成 `check-deploy.sh`，改 URL 后运行：

```bash
#!/usr/bin/env bash
# 用法: bash check-deploy.sh https://quantlab.edgeone.app
URL="${1:?用法: bash check-deploy.sh <站点URL>}"
URL="${URL%/}"

pass=0; fail=0
check() {
  local name="$1" path="$2" expect="$3"
  code=$(curl -o /tmp/_c.html -s -w "%{http_code}" "$URL$path")
  if [ "$code" = "200" ] && grep -q "$expect" /tmp/_c.html; then
    echo "✅ $name"; pass=$((pass+1))
  else
    echo "❌ $name (HTTP $code, 缺少『$expect』)"; fail=$((fail+1))
  fi
}

check "首页"            "/"                                          "QuantLab"
check "1.3 量化思维"     "/guide/m01-overview/1.3-quant-mindset.html"  "凯利"
check "3.3 性能优化"     "/guide/m03-python-data/3.3-performance.html" "向量化"
check "4.1 回测引擎"     "/guide/m04-backtest/4.1-engine.html"        "backtest"

echo "----"
echo "通过 $pass / 失败 $fail"
```

---

> 手册结束。平台选型理由见 `_reports/DEPLOY-PRD.md`，分步实施计划见 `_reports/DEPLOY-CHECKLIST.md`。
