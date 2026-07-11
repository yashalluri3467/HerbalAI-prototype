# HerbalAI frontend — React/Vite SPA served by nginx
# Stage 1: build the production bundle
FROM node:20-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
# VITE_API_BASE_URL is left unset (default '') so the built app makes relative
# /api requests, which nginx proxies to the backend.
RUN npm run build

# Stage 2: serve the static SPA
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
