# MultiSportsBettingPlatform - Production Dockerfile
# Multi-stage build for optimized production deployment

# Stage 1: Base Python environment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements_minimal.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Backend application
FROM base as backend

# Copy application code
COPY src/ ./src/
COPY *.py ./
COPY .env* ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "run.py"]

# Stage 3: Frontend build
FROM node:18-alpine as frontend-builder

# Set working directory
WORKDIR /app

# Copy package files
COPY sports-betting-kendo-react/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY sports-betting-kendo-react/src/ ./src/
COPY sports-betting-kendo-react/public/ ./public/

# Build the application
RUN npm run build

# Stage 4: Production frontend
FROM nginx:alpine as frontend

# Copy built application
COPY --from=frontend-builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Stage 5: Analytics service
FROM base as analytics

# Copy analytics code
COPY advanced_analytics_system.py ./
COPY real_sports_data_integration.py ./
COPY backend_integration_system_fixed.py ./

# Create analytics user
RUN useradd --create-home --shell /bin/bash analytics && \
    chown -R analytics:analytics /app
USER analytics

# Expose analytics port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import advanced_analytics_system; print('Analytics OK')" || exit 1

# Start analytics service
CMD ["python", "advanced_analytics_system.py"]

# Stage 6: Redis cache
FROM redis:7-alpine as cache

# Copy Redis configuration
COPY redis.conf /usr/local/etc/redis/redis.conf

# Expose Redis port
EXPOSE 6379

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD redis-cli ping || exit 1

# Stage 7: Database
FROM postgres:15-alpine as database

# Set environment variables
ENV POSTGRES_DB=multisports_betting \
    POSTGRES_USER=betting_user \
    POSTGRES_PASSWORD=secure_password_2024

# Copy database initialization scripts
COPY database/init.sql /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD pg_isready -U betting_user -d multisports_betting || exit 1

# Stage 8: Monitoring
FROM prom/prometheus:latest as monitoring

# Copy Prometheus configuration
COPY monitoring/prometheus.yml /etc/prometheus/prometheus.yml

# Expose Prometheus port
EXPOSE 9090

# Stage 9: Final production image
FROM base as production

# Copy all necessary files
COPY --from=backend /app /app/backend
COPY --from=frontend /usr/share/nginx/html /app/frontend
COPY --from=analytics /app /app/analytics

# Copy production scripts
COPY scripts/start-production.sh /app/
COPY scripts/health-check.sh /app/

# Make scripts executable
RUN chmod +x /app/start-production.sh /app/health-check.sh

# Set working directory
WORKDIR /app

# Expose all necessary ports
EXPOSE 8000 8001 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD /app/health-check.sh || exit 1

# Start production services
CMD ["/app/start-production.sh"] 