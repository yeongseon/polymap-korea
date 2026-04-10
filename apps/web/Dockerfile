FROM node:20-alpine AS deps

WORKDIR /app

RUN npm install -g pnpm@9

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json apps/web/package.json

RUN pnpm install --frozen-lockfile

FROM node:20-alpine AS builder

WORKDIR /app

RUN npm install -g pnpm@9

COPY --from=deps /app/ ./
COPY apps/web ./apps/web

RUN pnpm --filter web exec next build --no-lint

FROM nginx:1.27-alpine AS runner

COPY --from=builder /app/apps/web/out /usr/share/nginx/html
COPY <<'NGINX_CONF' /etc/nginx/conf.d/default.conf
server {
    listen 3000;
    root /usr/share/nginx/html;
    location / {
        try_files $uri $uri/ $uri.html /index.html;
    }
}
NGINX_CONF

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
