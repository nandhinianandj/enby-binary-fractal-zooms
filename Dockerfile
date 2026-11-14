# Dockerfile - Lightweight Alpine Node.js image for Fly.io
FROM node:20-alpine
WORKDIR /app
COPY package.json server.js index.html ./
EXPOSE 8080
ENV NODE_ENV=production
ENV PORT=8080
CMD ["node", "server.js"]
