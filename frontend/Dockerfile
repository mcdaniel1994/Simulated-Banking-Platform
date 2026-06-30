# syntax=docker/dockerfile:1

FROM node:22-alpine AS frontend-builder

WORKDIR /workspace/frontend

# Install exactly the dependency graph reviewed in package-lock.json.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend ./
RUN npm run build

FROM nginx:1.28-alpine AS gateway

# The official entrypoint renders templates with runtime environment values before nginx starts.
COPY deploy/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=frontend-builder /workspace/frontend/dist /usr/share/nginx/html

EXPOSE 80 443
