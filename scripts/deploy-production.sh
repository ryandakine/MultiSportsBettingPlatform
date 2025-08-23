#!/bin/bash

# MultiSports Betting Platform - Production Deployment Script
# This script handles the complete production deployment process

set -e  # Exit on any error

# Configuration
PROJECT_NAME="multisports-betting-platform"
NAMESPACE="production"
REGISTRY="ghcr.io"
IMAGE_TAG="${1:-latest}"
ENVIRONMENT="production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if helm is installed
    if ! command -v helm &> /dev/null; then
        log_error "helm is not installed. Please install helm first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed. Please install docker first."
        exit 1
    fi
    
    # Check kubectl connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create namespace
create_namespace() {
    log_info "Creating namespace: $NAMESPACE"
    
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Namespace created/verified"
}

# Deploy secrets
deploy_secrets() {
    log_info "Deploying secrets..."
    
    # Create secrets from environment variables or files
    kubectl create secret generic multisports-secrets \
        --namespace=$NAMESPACE \
        --from-literal=secret-key="${SECRET_KEY:-production-secret-key-change-in-production}" \
        --from-literal=database-url="${DATABASE_URL:-postgresql://betting_user:secure_password_2024@multisports-database-service:5432/multisports_betting}" \
        --from-literal=db-user="${DB_USER:-betting_user}" \
        --from-literal=db-password="${DB_PASSWORD:-secure_password_2024}" \
        --from-literal=grafana-password="${GRAFANA_PASSWORD:-admin123}" \
        --from-literal=redis-password="${REDIS_PASSWORD:-redis_password_2024}" \
        --from-literal=jwt-secret="${JWT_SECRET:-json-web-token-secret-key-2024}" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Secrets deployed"
}

# Deploy database
deploy_database() {
    log_info "Deploying PostgreSQL database..."
    
    kubectl apply -f k8s/deployment.yaml -n $NAMESPACE
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    kubectl wait --for=condition=ready pod -l app=multisports-database -n $NAMESPACE --timeout=300s
    
    log_success "Database deployed and ready"
}

# Deploy cache
deploy_cache() {
    log_info "Deploying Redis cache..."
    
    kubectl apply -f k8s/deployment.yaml -n $NAMESPACE
    
    # Wait for cache to be ready
    log_info "Waiting for cache to be ready..."
    kubectl wait --for=condition=ready pod -l app=multisports-cache -n $NAMESPACE --timeout=300s
    
    log_success "Cache deployed and ready"
}

# Deploy backend services
deploy_backend() {
    log_info "Deploying backend services..."
    
    # Update image tags
    kubectl set image deployment/multisports-backend \
        backend=$REGISTRY/$PROJECT_NAME/backend:$IMAGE_TAG \
        -n $NAMESPACE
    
    kubectl set image deployment/multisports-analytics \
        analytics=$REGISTRY/$PROJECT_NAME/analytics:$IMAGE_TAG \
        -n $NAMESPACE
    
    # Wait for deployments to be ready
    log_info "Waiting for backend services to be ready..."
    kubectl rollout status deployment/multisports-backend -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/multisports-analytics -n $NAMESPACE --timeout=300s
    
    log_success "Backend services deployed and ready"
}

# Deploy frontend
deploy_frontend() {
    log_info "Deploying frontend..."
    
    # Update image tag
    kubectl set image deployment/multisports-frontend \
        frontend=$REGISTRY/$PROJECT_NAME/frontend:$IMAGE_TAG \
        -n $NAMESPACE
    
    # Wait for deployment to be ready
    log_info "Waiting for frontend to be ready..."
    kubectl rollout status deployment/multisports-frontend -n $NAMESPACE --timeout=300s
    
    log_success "Frontend deployed and ready"
}

# Deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    kubectl apply -f k8s/deployment.yaml -n $NAMESPACE
    
    # Wait for monitoring to be ready
    log_info "Waiting for monitoring to be ready..."
    kubectl wait --for=condition=ready pod -l app=multisports-monitoring -n $NAMESPACE --timeout=300s
    
    log_success "Monitoring stack deployed and ready"
}

# Deploy ingress and services
deploy_ingress() {
    log_info "Deploying ingress and services..."
    
    kubectl apply -f k8s/services.yaml -n $NAMESPACE
    
    log_success "Ingress and services deployed"
}

# Run health checks
health_checks() {
    log_info "Running health checks..."
    
    # Check backend health
    BACKEND_URL=$(kubectl get service multisports-backend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -n "$BACKEND_URL" ]; then
        if curl -f "http://$BACKEND_URL:8000/health" > /dev/null 2>&1; then
            log_success "Backend health check passed"
        else
            log_error "Backend health check failed"
            return 1
        fi
    fi
    
    # Check frontend health
    FRONTEND_URL=$(kubectl get service multisports-frontend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -n "$FRONTEND_URL" ]; then
        if curl -f "http://$FRONTEND_URL/health" > /dev/null 2>&1; then
            log_success "Frontend health check passed"
        else
            log_error "Frontend health check failed"
            return 1
        fi
    fi
    
    # Check database connectivity
    if kubectl exec -n $NAMESPACE deployment/multisports-backend -- pg_isready -h multisports-database-service -p 5432 > /dev/null 2>&1; then
        log_success "Database connectivity check passed"
    else
        log_error "Database connectivity check failed"
        return 1
    fi
    
    # Check cache connectivity
    if kubectl exec -n $NAMESPACE deployment/multisports-backend -- redis-cli -h multisports-cache-service ping > /dev/null 2>&1; then
        log_success "Cache connectivity check passed"
    else
        log_error "Cache connectivity check failed"
        return 1
    fi
    
    log_success "All health checks passed"
}

# Run smoke tests
smoke_tests() {
    log_info "Running smoke tests..."
    
    # Test API endpoints
    BACKEND_URL=$(kubectl get service multisports-backend-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [ -n "$BACKEND_URL" ]; then
        # Test health endpoint
        if curl -f "http://$BACKEND_URL:8000/health" > /dev/null 2>&1; then
            log_success "API health endpoint test passed"
        else
            log_error "API health endpoint test failed"
            return 1
        fi
        
        # Test user registration endpoint
        if curl -f -X POST "http://$BACKEND_URL:8000/api/auth/register" \
            -H "Content-Type: application/json" \
            -d '{"username":"test","email":"test@example.com","password":"test123"}' > /dev/null 2>&1; then
            log_success "User registration test passed"
        else
            log_warning "User registration test failed (may be expected)"
        fi
    fi
    
    log_success "Smoke tests completed"
}

# Monitor deployment
monitor_deployment() {
    log_info "Monitoring deployment..."
    
    # Check pod status
    kubectl get pods -n $NAMESPACE
    
    # Check service status
    kubectl get services -n $NAMESPACE
    
    # Check ingress status
    kubectl get ingress -n $NAMESPACE
    
    # Show logs for any failed pods
    FAILED_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running -o jsonpath='{.items[*].metadata.name}')
    if [ -n "$FAILED_PODS" ]; then
        log_warning "Found failed pods: $FAILED_PODS"
        for pod in $FAILED_PODS; do
            log_info "Logs for $pod:"
            kubectl logs $pod -n $NAMESPACE --tail=50
        done
    fi
    
    log_success "Deployment monitoring completed"
}

# Rollback function
rollback() {
    log_warning "Rolling back deployment..."
    
    # Rollback backend
    kubectl rollout undo deployment/multisports-backend -n $NAMESPACE
    kubectl rollout undo deployment/multisports-analytics -n $NAMESPACE
    kubectl rollout undo deployment/multisports-frontend -n $NAMESPACE
    
    # Wait for rollback to complete
    kubectl rollout status deployment/multisports-backend -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/multisports-analytics -n $NAMESPACE --timeout=300s
    kubectl rollout status deployment/multisports-frontend -n $NAMESPACE --timeout=300s
    
    log_success "Rollback completed"
}

# Main deployment function
main() {
    log_info "Starting production deployment for MultiSports Betting Platform"
    log_info "Environment: $ENVIRONMENT"
    log_info "Image tag: $IMAGE_TAG"
    log_info "Namespace: $NAMESPACE"
    
    # Check prerequisites
    check_prerequisites
    
    # Create namespace
    create_namespace
    
    # Deploy secrets
    deploy_secrets
    
    # Deploy infrastructure
    deploy_database
    deploy_cache
    
    # Deploy applications
    deploy_backend
    deploy_frontend
    deploy_monitoring
    
    # Deploy networking
    deploy_ingress
    
    # Run health checks
    if health_checks; then
        log_success "Health checks passed"
    else
        log_error "Health checks failed"
        rollback
        exit 1
    fi
    
    # Run smoke tests
    if smoke_tests; then
        log_success "Smoke tests passed"
    else
        log_warning "Some smoke tests failed"
    fi
    
    # Monitor deployment
    monitor_deployment
    
    log_success "Production deployment completed successfully!"
    log_info "Access your application at: https://multisports.example.com"
    log_info "API endpoint: https://api.multisports.example.com"
    log_info "Analytics: https://analytics.multisports.example.com"
    log_info "Monitoring: https://monitoring.multisports.example.com"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        health_checks
        ;;
    "monitor")
        monitor_deployment
        ;;
    "smoke")
        smoke_tests
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health|monitor|smoke} [image-tag]"
        echo "  deploy   - Deploy the application (default)"
        echo "  rollback - Rollback to previous version"
        echo "  health   - Run health checks"
        echo "  monitor  - Monitor deployment status"
        echo "  smoke    - Run smoke tests"
        exit 1
        ;;
esac 