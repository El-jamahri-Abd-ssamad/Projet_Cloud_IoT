#!/bin/bash

# Script de déploiement device-management

set -e

echo "🚀 Device Management - Deployment Script"
echo "======================================="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonctions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Vérifier les prérequis
check_requirements() {
    log_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_info "✓ Docker and Docker Compose are installed"
}

# Vérifier la configuration
check_env() {
    log_info "Checking environment..."
    
    if [ ! -f ".env" ]; then
        log_warning ".env file not found, creating from .env.example"
        cp .env.example .env
        log_warning "Please update .env with your configuration"
    fi
    
    log_info "✓ Environment configured"
}

# Build l'image Docker
build_image() {
    log_info "Building Docker image..."
    docker-compose build
    log_info "✓ Docker image built successfully"
}

# Démarrer les services
start_services() {
    log_info "Starting services..."
    docker-compose up -d
    log_info "✓ Services started"
}

# Vérifier la santé des services
health_check() {
    log_info "Checking service health..."
    
    local max_retries=30
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            log_info "✓ Device Management API is healthy"
            return 0
        fi
        
        retry=$((retry + 1))
        sleep 2
    done
    
    log_error "Health check failed after $max_retries attempts"
    return 1
}

# Afficher les logs
show_logs() {
    log_info "Recent logs:"
    docker-compose logs --tail=20 device-management
}

# Arrêter les services
stop_services() {
    log_info "Stopping services..."
    docker-compose down
    log_info "✓ Services stopped"
}

# Nettoyer
cleanup() {
    log_info "Cleaning up..."
    docker-compose down -v
    log_info "✓ Cleanup complete"
}

# Main menu
main_menu() {
    echo ""
    echo "Select an option:"
    echo "1) Deploy (build & start)"
    echo "2) Start services"
    echo "3) Stop services"
    echo "4) View logs"
    echo "5) Health check"
    echo "6) Full cleanup"
    echo "7) Exit"
    echo ""
    read -p "Choose [1-7]: " choice
    
    case $choice in
        1)
            check_requirements
            check_env
            build_image
            start_services
            health_check
            show_logs
            ;;
        2)
            check_requirements
            check_env
            start_services
            ;;
        3)
            stop_services
            ;;
        4)
            show_logs
            ;;
        5)
            health_check
            ;;
        6)
            cleanup
            ;;
        7)
            exit 0
            ;;
        *)
            log_error "Invalid option"
            ;;
    esac
}

# Script principal
if [ "$1" == "deploy" ]; then
    check_requirements
    check_env
    build_image
    start_services
    health_check
    show_logs
elif [ "$1" == "stop" ]; then
    stop_services
elif [ "$1" == "clean" ]; then
    cleanup
elif [ "$1" == "health" ]; then
    health_check
elif [ "$1" == "logs" ]; then
    show_logs
else
    main_menu
fi

log_info "Done!"
