#!/bin/bash

# Script de gestion PostgreSQL pour développement

echo "🐘 PostgreSQL - Device Management"
echo "=================================="

if [ "$1" == "start" ]; then
    echo "Démarrage de PostgreSQL..."
    docker-compose -f docker-compose-dev.yml up -d
    echo "✅ PostgreSQL démarré sur localhost:5432"
    echo "✅ pgAdmin disponible sur http://localhost:5050 (admin/admin)"
    echo ""
    echo "Credentials:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: device_management"
    echo "  User: postgres"
    echo "  Password: postgres"
    
elif [ "$1" == "stop" ]; then
    echo "Arrêt de PostgreSQL..."
    docker-compose -f docker-compose-dev.yml down
    echo "✅ PostgreSQL arrêté"
    
elif [ "$1" == "logs" ]; then
    docker-compose -f docker-compose-dev.yml logs -f postgres
    
elif [ "$1" == "clean" ]; then
    echo "Nettoyage complet (suppression données)..."
    docker-compose -f docker-compose-dev.yml down -v
    echo "✅ Données supprimées"
    
else
    echo "Usage: ./postgres.sh [start|stop|logs|clean]"
    echo ""
    echo "  start   - Démarrer PostgreSQL"
    echo "  stop    - Arrêter PostgreSQL"
    echo "  logs    - Afficher les logs"
    echo "  clean   - Arrêter et supprimer les données"
fi
