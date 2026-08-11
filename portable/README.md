# QuantLab 便携学习平台

> **完全离线运行** · 拷贝即用 · 适合 U 盘 / 邮件分发 / 离线学习

---

## 🚀 快速启动(Windows 用户)

1. 把整个 `portable/` 文件夹拷贝到任意位置(桌面、U 盘、网盘…)
2. **双击 `start.bat`**
3. 浏览器自动打开,开始学习

> 第一次启动需要安装 **Node.js 14+**:[下载 LTS 版本](https://nodejs.org/zh-cn/)
> 安装后再次双击 `start.bat` 即可。

---

## 🚀 快速启动(macOS / Linux 用户)

```bash
cd portable
chmod +x start.sh
./start.sh
```

首次启动同样需要 Node.js 14+:

```bash
# macOS
brew install node

# Ubuntu / Debian
sudo apt install nodejs
```

---

## 📦 文件结构

```
portable/
├── dist/                 # 网站构建产物（已含本地 Pyodide）
├── pyodide/              # 浏览器 Python 运行时（~14 MB）
├── code/                 # 教程中的 Python 示例代码
├── serve.cjs             # 微型 Node 静态服务器（零依赖）
├── start.bat             # Windows 启动脚本
├── start.sh              # macOS/Linux 启动脚本
└── README.md             # 本文件
```

**总大小** ≈ **150 MB**(可装进任何 U 盘)

---

## 🎯 包含内容

- ✅ **20 大模块 / 107 个章节** 量化交易教学课程
- ✅ **16 个新章节**(2026-07-15 补强内容)
- ✅ **完整 Python 沙箱**(浏览器中可运行所有 Python 代码示例)
- ✅ **本地 Pyodide 运行时**(无须联网下载)
- ✅ **交互式组件**:Python 沙箱、计算器、图表、quiz 小测验

---

## ⚙️ 工作原理

```
+------------------+         +-------------------+
|   浏览器          |  HTTP   |  serve.cjs         |
|  (Chrome/Edge)   +-------->|  Node 静态服务器   |
|                  |<--------+                   |
+------------------+         +-------------------+
                                     |
                                     v
                              +-------------------+
                              |  本地文件系统      |
                              |  dist/ + pyodide/ |
                              +-------------------+
```

- **完全本地**:所有资源(dist + Pyodide)都在文件夹里,**无须联网**
- **安全沙箱**:浏览器中运行的 Python 由 Pyodide 提供,不能访问你的文件系统
- **零后端**:静态文件,只读,无数据库,无登录

---

## 🔧 故障排查

### 端口 5173 被占用?

`start.bat` / `start.sh` 会**自动尝试 5174、5175…** 直到找到可用端口。

也可以手动指定:
```bash
node serve.cjs --port 8080
```

### 不想自动打开浏览器?

```bash
node serve.cjs --no-open
# 然后手动访问 http://127.0.0.1:5173
```

### 浏览器中 Python 代码跑不起来?

1. 检查 `pyodide/pyodide.js` 是否存在(应该在)
2. 按 F12 打开浏览器开发者工具查看 Console 错误
3. 99% 是浏览器安全策略:Edge/Chrome 默认允许,部分企业 IE 限制

### 双击 start.bat 一闪而过?

- 这是因为 Node.js 没装。请先安装 Node.js,再启动。
- 也可在 portable/ 目录打开命令行,运行 `node serve.cjs` 查看具体错误。

---

## 📤 拷贝方式

| 渠道 | 是否可行 | 大小 |
|:---|:---|:---:|
| U 盘 | ✅ 推荐 | 150 MB |
| 邮件附件 | ⚠️ 部分邮箱限制 25MB(可用网盘替代) | 150 MB |
| 微信/钉钉文件传输 | ❌ 通常限制 100MB,需分卷压缩 | 150 MB |
| 网盘(百度/阿里) | ✅ 推荐 | 150 MB |
| GitHub Release | ✅ 推荐发布长期支持 | 150 MB |
| 内网共享 | ✅ 拷贝一次多人共享 | 150 MB |

---

## 🆕 更新日志

### v1.0 (2026-07-15)
- 首次发布
- 20 模块 / 107 章节
- 含 16 个本轮新增章节
- 本地 Pyodide 完全离线运行

---

## 💡 后续优化(可选)

- [ ] Service Worker 预缓存 Pyodide(二次访问秒开)
- [ ] 简单计算改纯 JavaScript(免加载 Pyodide)
- [ ] 折叠式 Python 沙箱(默认显示静态代码,展开后才加载)

---

**作者** · QuantLab 团队
**许可** · 仅供学习交流使用