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

RUN pnpm --filter web build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0

COPY --from=builder /app/apps/web/.next/standalone ./
COPY --from=builder /app/apps/web/.next/static ./.next/static

EXPOSE 3000

CMD ["node", "server.js"]
