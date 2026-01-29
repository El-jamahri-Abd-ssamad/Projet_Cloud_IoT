#!/bin/bash
# Script de validation rapide du module device-management

echo "🔍 Validation du module device-management"
echo "=========================================="

# Vérifier la structure des répertoires
check_structure() {
    echo ""
    echo "📁 Vérification de la structure..."
    
    dirs=("controller" "dal" "dto" "entities" "helpers" "test")
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo "  ✅ $dir/"
        else
            echo "  ❌ $dir/ MANQUANT"
            return 1
        fi
    done
    return 0
}

# Vérifier les fichiers critiques
check_files() {
    echo ""
    echo "📄 Vérification des fichiers..."
    
    files=(
        "main.py"
        "requirements.txt"
        "Dockerfile"
        "docker-compose.yml"
        ".env.example"
        "README.md"
        "CORRECTIONS.md"
        "pytest.ini"
        "setup.cfg"
        ".gitignore"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo "  ✅ $file"
        else
            echo "  ❌ $file MANQUANT"
            return 1
        fi
    done
    return 0
}

# Vérifier les __init__.py
check_inits() {
    echo ""
    echo "🐍 Vérification des __init__.py..."
    
    packages=("controller" "dal" "dto" "entities" "helpers" "test")
    for pkg in "${packages[@]}"; do
        if [ -f "$pkg/__init__.py" ]; then
            echo "  ✅ $pkg/__init__.py"
        else
            echo "  ❌ $pkg/__init__.py MANQUANT"
            return 1
        fi
    done
    return 0
}

# Vérifier les helpers
check_helpers() {
    echo ""
    echo "🛠️  Vérification des helpers..."
    
    helpers=(
        "helpers/config.py"
        "helpers/database.py"
        "helpers/rabbitmq_helper.py"
        "helpers/redis_helper.py"
        "helpers/auth_helper.py"
        "helpers/device_manager_helper.py"
    )
    
    for helper in "${helpers[@]}"; do
        if [ -f "$helper" ]; then
            size=$(wc -c < "$helper")
            if [ "$size" -gt 100 ]; then
                echo "  ✅ $helper ($(($size/1024))KB)"
            else
                echo "  ⚠️  $helper (vide ou quasi-vide)"
            fi
        else
            echo "  ❌ $helper MANQUANT"
            return 1
        fi
    done
    return 0
}

# Vérifier les imports
check_imports() {
    echo ""
    echo "📦 Vérification des imports dans main.py..."
    
    if grep -q "from helpers.config import" main.py; then
        echo "  ✅ Import config.py"
    else
        echo "  ❌ Import config.py MANQUANT"
        return 1
    fi
    
    if grep -q "from entities.database import" main.py; then
        echo "  ✅ Import database.py"
    else
        echo "  ❌ Import database.py MANQUANT"
        return 1
    fi
    
    if grep -q "from controller.device_manager_controller import" main.py; then
        echo "  ✅ Import device_manager_controller"
    else
        echo "  ❌ Import device_manager_controller MANQUANT"
        return 1
    fi
    
    return 0
}

# Résumé
echo ""
all_ok=true

check_structure || all_ok=false
check_files || all_ok=false
check_inits || all_ok=false
check_helpers || all_ok=false
check_imports || all_ok=false

echo ""
echo "=========================================="
if $all_ok; then
    echo "✅ Toutes les vérifications sont passées!"
    echo ""
    echo "🚀 Prochaines étapes:"
    echo "  1. Copier .env.example en .env"
    echo "  2. Configurer les variables d'environnement"
    echo "  3. Lancer: ./deploy.sh"
    exit 0
else
    echo "❌ Certaines vérifications ont échoué"
    exit 1
fi
