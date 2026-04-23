# 1. Build stage
FROM node:18-alpine AS builder

WORKDIR /build
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev

# 2. Production stage
FROM node:18-alpine

WORKDIR /app

# The 'node' user and group (UID/GID 1000) already exist in the base image.
# We simply set permissions for the app directory for the existing 'node' user.
RUN chown -R node:node /app

# Copy necessary files from builder
COPY --from=builder --chown=node:node /build/node_modules ./node_modules
COPY --chown=node:node app.js .
COPY --chown=node:node views ./views

ENV NODE_ENV=production \
    PORT=3000 \
    API_URL=http://api:8000

# Use the existing non-root 'node' user
USER node

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["node", "app.js"]