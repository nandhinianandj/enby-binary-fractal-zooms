// server.js - Zero-dependency Node.js production server for Fly.io
const http = require('http');
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const PORT = process.env.PORT || 8080;
const INDEX_PATH = path.join(__dirname, 'index.html');

const server = http.createServer((req, res) => {
  if (req.url === '/healthz') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'ok', engine: 'morphogenesis-webgl' }));
  }

  fs.readFile(INDEX_PATH, (err, data) => {
    if (err) {
      res.writeHead(500);
      return res.end('Error loading index.html');
    }
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
      'Content-Encoding': 'gzip'
    });
    zlib.gzip(data, (_, compressed) => res.end(compressed));
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Morphogenesis WebGL Engine listening on http://0.0.0.0:${PORT}`);
});
