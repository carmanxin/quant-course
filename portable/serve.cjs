/*
 * QuantLab 便携服务器（零依赖，Node.js 内置模块）
 * ---------------------------------------------------------------
 * 作用：
 *   1. 把 dist/ 目录作为静态资源根目录，启动一个微型 HTTP 服务
 *   2. 默认端口 5173，端口被占用时自动递增
 *   3. 自动打开默认浏览器
 *   4. 显示启动横幅 + 关闭提示
 *
 * 使用：
 *   node serve.js            # 启动 + 自动打开浏览器
 *   node serve.js --no-open  # 只启动服务，不开浏览器
 *   node serve.js --port 80  # 自定义端口
 *
 * 依赖：Node.js >= 14（任何现代版本均可）
 * ---------------------------------------------------------------
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

// ============ 配置 ============
function parsePort() {
  // 优先级: --port N > process.env.PORT > 默认 5173
  const i = process.argv.indexOf('--port');
  if (i !== -1 && process.argv[i + 1]) {
    const p = parseInt(process.argv[i + 1], 10);
    if (!isNaN(p) && p > 0 && p < 65536) return p;
  }
  return parseInt(process.env.PORT || '5173', 10);
}
const DEFAULT_PORT = parsePort();
// 站点根目录：serve.cjs 所在目录下的 dist/
const DIST_DIR = path.join(__dirname, 'dist');
const OPEN_BROWSER = !process.argv.includes('--no-open');

// ============ MIME 类型 ============
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.htm':  'text/html; charset=utf-8',
  '.js':   'application/javascript; charset=utf-8',
  '.mjs':  'application/javascript; charset=utf-8',
  '.css':  'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg':  'image/svg+xml',
  '.png':  'image/png',
  '.jpg':  'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif':  'image/gif',
  '.ico':  'image/x-icon',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2':'font/woff2',
  '.ttf':  'font/ttf',
  '.wasm': 'application/wasm',
  '.map':  'application/json; charset=utf-8',
  '.txt':  'text/plain; charset=utf-8',
  '.py':   'text/x-python; charset=utf-8',
  '.md':   'text/markdown; charset=utf-8',
};

// ============ 工具函数 ============
function safeJoin(root, rel) {
  // 防止路径穿越
  const resolved = path.resolve(root, '.' + rel);
  if (!resolved.startsWith(path.resolve(root))) return null;
  return resolved;
}

function send404(res) {
  res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>404</title>
<style>body{font-family:-apple-system,system-ui,sans-serif;max-width:640px;margin:60px auto;padding:0 24px;color:#0B1220}
h1{font-size:64px;margin:0;color:#00E5A0}p{color:#475569;line-height:1.6}
a{color:#7C3AED;text-decoration:none}a:hover{text-decoration:underline}</style></head>
<body><h1>404</h1><p>页面走丢了。这个地址可能拼错了,或者资源已被移除。</p>
<p><a href="/">← 返回首页</a></p></body></html>`);
}

function tryFile(res, absPath, fallback = null) {
  fs.stat(absPath, (err, stat) => {
    if (err) {
      if (fallback) return tryFile(res, fallback);
      return send404(res);
    }
    if (stat.isDirectory()) {
      // 目录 → 找 index.html
      const indexPath = path.join(absPath, 'index.html');
      return tryFile(res, indexPath, fallback);
    }
    const ext = path.extname(absPath).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    res.writeHead(200, {
      'Content-Type': type,
      'Cache-Control': 'no-cache',
    });
    fs.createReadStream(absPath).pipe(res);
  });
}

// ============ 启动横幅 ============
const BANNER = `
╔══════════════════════════════════════════════════════════════╗
║                  QuantLab 便携学习平台                         ║
║                  Quant Trading Course (offline)                ║
╚══════════════════════════════════════════════════════════════╝
`;

// ============ 启动服务器（端口递增） ============
function startServer(port, callback) {
  const server = http.createServer((req, res) => {
    const parsed = url.parse(req.url);
    let pathname = decodeURIComponent(parsed.pathname || '/');

    // 默认 / → /index.html
    if (pathname === '/') pathname = '/index.html';

    // 安全路径检查
    const absPath = safeJoin(DIST_DIR, pathname);
    if (!absPath) return send404(res);

    tryFile(res, absPath);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      // 端口占用，递增
      console.error(`⚠  端口 ${port} 已被占用，尝试 ${port + 1}...`);
      startServer(port + 1, callback);
    } else {
      console.error('✖  启动失败：', err.message);
      process.exit(1);
    }
  });

  server.listen(port, '127.0.0.1', () => {
    callback(port);
  });
}

// ============ 自动打开浏览器 ============
function openBrowser(url) {
  const { exec } = require('child_process');
  const cmd = process.platform === 'darwin'
    ? `open "${url}"`
    : process.platform === 'win32'
    ? `start "" "${url}"`
    : `xdg-open "${url}"`;
  exec(cmd, (err) => {
    if (err) {
      console.log(`ℹ  自动打开浏览器失败，请手动访问：${url}`);
    }
  });
}

// ============ 关闭提示 ============
function setupShutdown() {
  const onExit = () => {
    console.log('\n👋  正在关闭 QuantLab 便携服务...');
    console.log('   （关闭窗口或按 Ctrl+C 退出）');
    process.exit(0);
  };
  process.on('SIGINT', onExit);
  process.on('SIGTERM', onExit);
}

// ============ 启动 ============
console.log(BANNER);
setupShutdown();
startServer(DEFAULT_PORT, (port) => {
  const url = `http://127.0.0.1:${port}/`;
  console.log(`✓  QuantLab 已就绪`);
  console.log(`   地址：${url}`);
  console.log(`   模式：完全离线（无网络依赖）`);
  console.log(`   关闭：Ctrl+C 或直接关闭窗口\n`);
  if (OPEN_BROWSER) {
    console.log('🚀  正在打开浏览器...');
    setTimeout(() => openBrowser(url), 400);
  } else {
    console.log('ℹ  已跳过自动打开浏览器（使用 --no-open 标志）');
    console.log(`   请手动访问：${url}\n`);
  }
});