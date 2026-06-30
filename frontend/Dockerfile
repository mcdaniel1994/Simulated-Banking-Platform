# syntax=docker/dockerfile:1

FROM node:22-alpine AS frontend-builder

WORKDIR /workspace/frontend

# Install exactly the dependency graph reviewed in package-lock.json.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
RUN npm run build

FROM nginx:1.28-alpine AS nginx-base

COPY --from=frontend-builder /workspace/frontend/dist /usr/share/nginx/html

FROM nginx-base AS gateway

# The manual VPS target renders the public hostname and terminates TLS inside nginx.
COPY deploy/nginx/default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80 443

FROM nginx-base AS coolify-gateway

# Coolify owns public TLS; this nginx target only serves/proxies over the private Docker network.
COPY deploy/nginx/coolify.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
