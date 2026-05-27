# Use Node.js Alpine for minimal size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY src/package*.json ./

# Install dependencies
RUN npm install --production

# Copy server and static files
COPY src/server.js ./
COPY src/public ./public

# Copy providers.json
COPY src/providers.json ./

# Install curl for health checks
RUN apk add --no-cache curl

# Set ownership to node user (already exists in node:18-alpine)
RUN chown -R node:node /app

# Switch to non-root user
USER node

# Expose port
EXPOSE 8689

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8689/health || exit 1

# Start server
CMD ["npm", "start"]
