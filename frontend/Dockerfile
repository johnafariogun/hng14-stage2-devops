# Multi-stage build for Frontend service
FROM node:18-alpine as builder

WORKDIR /build

# Copy package files
COPY package.json package-lock.json* ./

# Install production dependencies only
RUN npm ci --omit=dev

# Production stage
FROM node:18-alpine

WORKDIR /app

# Create non-root user for security
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser

# Copy only necessary files from builder
COPY --from=builder --chown=appuser:appuser /build/node_modules ./node_modules
COPY --chown=appuser:appuser app.js .
COPY --chown=appuser:appuser views ./views

# Set environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    API_URL=http://api:8000

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Run the application
CMD ["node", "app.js"]
