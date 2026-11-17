// server.js - Zero-dependency Node.js production & dev server for Fly.io
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 8080;
const PUBLIC_DIR = __dirname;
const INDEX_PATH = path.join(PUBLIC_DIR, 'index.html');
const DEV_PATH = path.join(PUBLIC_DIR, 'morphogenesis_fractals_aperiodicity_natural_order.html');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon'
};

const server = http.createServer((req, res) => {
  const urlObj = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = urlObj.pathname;

  if (pathname === '/healthz') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({
      status: 'ok',
      engine: 'morphogenesis-webgl',
      endpoints: {
        production: '/',
        development: '/dev',
        dev_file: '/morphogenesis_fractals_aperiodicity_natural_order.html'
      }
    }));
  }

  // Routing: /dev or /preview points to the development morphogenesis file
  const isDevRoute = (pathname === '/dev' || pathname === '/dev/' || pathname === '/preview' || pathname === '/preview/');
  let targetFile = INDEX_PATH;
  let envHeader = 'production';

  if (isDevRoute) {
    targetFile = DEV_PATH;
    envHeader = 'development';
  } else if (pathname === '/' || pathname === '') {
    targetFile = INDEX_PATH;
    envHeader = 'production';
  } else {
    // Sanitize path for static asset requests (e.g. /locales/en.json, /morphogenesis_fractals_aperiodicity_natural_order.html)
    const safePath = path.normalize(decodeURI(pathname)).replace(/^(\.\.[\/\\])+/, '');
    const requestedFile = path.join(PUBLIC_DIR, safePath);
    if (fs.existsSync(requestedFile) && fs.statSync(requestedFile).isFile()) {
      targetFile = requestedFile;
      if (requestedFile === DEV_PATH) {
        envHeader = 'development';
      }
    } else {
      targetFile = INDEX_PATH;
    }
  }

  const ext = path.extname(targetFile).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';

  fs.readFile(targetFile, (err, data) => {
    if (err) {
      res.writeHead(500);
      return res.end('Error loading resource');
    }
    res.writeHead(200, {
      'Content-Type': contentType,
      'Cache-Control': isDevRoute ? 'no-cache, no-store, must-revalidate' : 'public, max-age=3600',
      'X-Environment': envHeader
    });
    res.end(data);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Morphogenesis WebGL Engine listening on http://0.0.0.0:${PORT}`);
  console.log(`  -> Production endpoint:  http://0.0.0.0:${PORT}/`);
  console.log(`  -> Development endpoint: http://0.0.0.0:${PORT}/dev`);
});
