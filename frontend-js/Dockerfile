# File Path: /frontend-js/Dockerfile
# Description: Reproducible source-build frontend image with an Nginx runtime.
# Main Features:
#   - Builds dist from the checked-in pnpm lockfile inside the image
#   - Copies only the build output into the read-only Nginx runtime
#   - Proxies /api/v1 to the backend Compose service

FROM docker.m.daocloud.io/library/node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS build

WORKDIR /app

RUN npm install --global pnpm@11.11.0

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY index.html vite.config.js ./
COPY public ./public
COPY scripts ./scripts
COPY src ./src

ARG VITE_API_BASE_URL=/api/v1
ARG VITE_PROXY_TARGET=http://backend:8000
ARG VITE_REQUEST_TIMEOUT=10000
ARG VITE_FRONTEND_MOCK_ENABLED=false
ARG VITE_SUPERVISOR_PAGE_ACCESS_JSON=[]
ARG VITE_OPERATOR_PAGE_ACCESS_JSON=[]
ARG VITE_LOGIN_DEMO_ACCOUNTS_ENABLED=false
ARG VITE_BRAND_LOGO_FILE=demo-organization-logo.svg
ARG VITE_BRAND_LOGO_ALIGN=center
ARG VITE_BRAND_GLOW_LEFT=light
ARG VITE_BRAND_GLOW_CENTER=accent
ARG VITE_BRAND_GLOW_RIGHT=accent
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_PROXY_TARGET=${VITE_PROXY_TARGET} \
    VITE_REQUEST_TIMEOUT=${VITE_REQUEST_TIMEOUT} \
    VITE_FRONTEND_MOCK_ENABLED=${VITE_FRONTEND_MOCK_ENABLED} \
    VITE_SUPERVISOR_PAGE_ACCESS_JSON=${VITE_SUPERVISOR_PAGE_ACCESS_JSON} \
    VITE_OPERATOR_PAGE_ACCESS_JSON=${VITE_OPERATOR_PAGE_ACCESS_JSON} \
    VITE_LOGIN_DEMO_ACCOUNTS_ENABLED=${VITE_LOGIN_DEMO_ACCOUNTS_ENABLED} \
    VITE_BRAND_LOGO_FILE=${VITE_BRAND_LOGO_FILE} \
    VITE_BRAND_LOGO_ALIGN=${VITE_BRAND_LOGO_ALIGN} \
    VITE_BRAND_GLOW_LEFT=${VITE_BRAND_GLOW_LEFT} \
    VITE_BRAND_GLOW_CENTER=${VITE_BRAND_GLOW_CENTER} \
    VITE_BRAND_GLOW_RIGHT=${VITE_BRAND_GLOW_RIGHT}

RUN pnpm build

FROM nginx:1.27-alpine@sha256:65645c7bb6a0661892a8b03b89d0743208a18dd2f3f17a54ef4b76fb8e2f2a10

COPY --from=build /app/dist /usr/share/nginx/html/current
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
