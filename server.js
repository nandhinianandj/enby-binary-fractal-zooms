// server.js - Zero-dependency Node.js production server for Fly.io
const http = require('http');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const PORT = process.env.PORT || 8080;
const PUBLIC_DIR = __dirname;
const INDEX_PATH = path.join(PUBLIC_DIR, 'index.html');

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
  if (req.url === '/healthz') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'ok', engine: 'morphogenesis-webgl' }));
  }

  // Sanitize path to prevent directory traversal
  let reqPath = decodeURI(req.url.split('?')[0]);
  if (reqPath === '/' || reqPath === '') {
    reqPath = '/index.html';
  }

  const filePath = path.join(PUBLIC_DIR, path.normalize(reqPath).replace(/^(\.\.[\/\\])+/, ''));
  
  fs.stat(filePath, (err, stats) => {
    const targetFile = (err || !stats.isFile()) ? INDEX_PATH : filePath;
    const ext = path.extname(targetFile).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    fs.readFile(targetFile, (readErr, data) => {
      if (readErr) {
        res.writeHead(500);
        return res.end('Error loading resource');
      }
      res.writeHead(200, {
        'Content-Type': contentType,
        'Cache-Control': 'public, max-age=3600',
        'Content-Encoding': 'gzip'
      });
      zlib.gzip(data, (_, compressed) => res.end(compressed));
    });
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Morphogenesis WebGL Engine listening on http://0.0.0.0:${PORT}`);
});
