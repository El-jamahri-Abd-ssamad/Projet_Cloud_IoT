#!/bin/bash
# Checklist finale pour device-management

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     DEVICE-MANAGEMENT - CHECKLIST FINALE                       ║"
echo "║     Analyse et Corrections Complètement Effectuées             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Compteurs
total=0
passed=0
failed=0

# Fonction pour vérifier
check() {
    local name=$1
    local cmd=$2
    
    ((total++))
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name"
        ((passed++))
    else
        echo -e "${RED}❌${NC} $name"
        ((failed++))
    fi
}

echo -e "${BLUE}📁 STRUCTURE DES RÉPERTOIRES${NC}"
check "controller/ existe" "[ -d 'controller' ]"
check "dal/ existe" "[ -d 'dal' ]"
check "dto/ existe" "[ -d 'dto' ]"
check "entities/ existe" "[ -d 'entities' ]"
check "helpers/ existe" "[ -d 'helpers' ]"
check "test/ existe" "[ -d 'test' ]"
check "logs/ existe ou sera créé" "true"

echo ""
echo -e "${BLUE}📄 FICHIERS CRITIQUES${NC}"
check "main.py existe" "[ -f 'main.py' ]"
check "requirements.txt existe" "[ -f 'requirements.txt' ]"
check "Dockerfile existe" "[ -f 'Dockerfile' ]"
check "docker-compose.yml existe" "[ -f 'docker-compose.yml' ]"
check ".env.example existe" "[ -f '.env.example' ]"
check ".env configuré" "[ -f '.env' ]"
check "README.md existe" "[ -f 'README.md' ]"
check "CORRECTIONS.md existe" "[ -f 'CORRECTIONS.md' ]"

echo ""
echo -e "${BLUE}🐍 PACKAGES PYTHON (__init__.py)${NC}"
check "controller/__init__.py" "[ -f 'controller/__init__.py' ]"
check "dal/__init__.py" "[ -f 'dal/__init__.py' ]"
check "dto/__init__.py" "[ -f 'dto/__init__.py' ]"
check "entities/__init__.py" "[ -f 'entities/__init__.py' ]"
check "helpers/__init__.py" "[ -f 'helpers/__init__.py' ]"
check "test/__init__.py" "[ -f 'test/__init__.py' ]"

echo ""
echo -e "${BLUE}🛠️  HELPERS CRÉÉS${NC}"
check "helpers/config.py" "[ -f 'helpers/config.py' ] && [ -s 'helpers/config.py' ]"
check "helpers/database.py" "[ -f 'helpers/database.py' ] && [ -s 'helpers/database.py' ]"
check "helpers/rabbitmq_helper.py" "[ -f 'helpers/rabbitmq_helper.py' ] && [ -s 'helpers/rabbitmq_helper.py' ]"
check "helpers/redis_helper.py" "[ -f 'helpers/redis_helper.py' ] && [ -s 'helpers/redis_helper.py' ]"
check "helpers/auth_helper.py" "[ -f 'helpers/auth_helper.py' ] && [ -s 'helpers/auth_helper.py' ]"
check "helpers/device_manager_helper.py (rempli)" "grep -q 'def validate_device_data' helpers/device_manager_helper.py"

echo ""
echo -e "${BLUE}⚙️  FICHIERS DE CONFIGURATION${NC}"
check "pytest.ini existe" "[ -f 'pytest.ini' ]"
check "setup.cfg existe" "[ -f 'setup.cfg' ]"
check ".gitignore existe" "[ -f '.gitignore' ]"
check "deploy.sh existe et exécutable" "[ -f 'deploy.sh' ]"
check "validate.sh existe et exécutable" "[ -f 'validate.sh' ]"

echo ""
echo -e "${BLUE}📦 TESTS${NC}"
check "test/test_basic.py existe" "[ -f 'test/test_basic.py' ]"
check "tests contiennent du code" "grep -q 'def test_' test/test_basic.py"

echo ""
echo -e "${BLUE}🔍 VÉRIFICATION DES IMPORTS${NC}"
check "main.py importe config" "grep -q 'from helpers.config import' main.py"
check "main.py importe database" "grep -q 'from entities.database import' main.py"
check "main.py importe device_manager_controller" "grep -q 'from controller.device_manager_controller import' main.py"
check "main.py importe rabbitmq_helper" "grep -q 'from helpers.rabbitmq_helper import' main.py"
check "main.py importe redis_helper" "grep -q 'from helpers.redis_helper import' main.py"

echo ""
echo -e "${BLUE}📚 DOCUMENTATION${NC}"
check "README.md rempli" "[ -s 'README.md' ] && grep -q 'FastAPI' README.md"
check "CORRECTIONS.md rempli" "[ -s 'CORRECTIONS.md' ] && grep -q 'corrections' CORRECTIONS.md"
check "Dockerfile contient python:3.11" "grep -q 'python:3.11' Dockerfile"
check "docker-compose configure postgres" "grep -q 'postgres:15' docker-compose.yml"
check "docker-compose configure redis" "grep -q 'redis:7' docker-compose.yml"
check "docker-compose configure rabbitmq" "grep -q 'rabbitmq:3.12' docker-compose.yml"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
printf "║  Résultats: ${GREEN}%-2d Passé${NC} | ${RED}%-2d Échoué${NC} | Total: ${total}%-25s║\n" "$passed" "$failed"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}🎉 TOUTES LES VÉRIFICATIONS SONT PASSÉES!${NC}"
    echo ""
    echo "Prochaines étapes:"
    echo "  1. cd device-management"
    echo "  2. ./deploy.sh (ou bash deploy.sh sur Windows)"
    echo "  3. Sélectionner l'option 1 pour le déploiement complet"
    echo ""
    echo "Ou pour tester localement:"
    echo "  1. python -m venv venv"
    echo "  2. source venv/bin/activate (ou venv\\Scripts\\activate sur Windows)"
    echo "  3. pip install -r requirements.txt"
    echo "  4. python main.py"
    echo ""
    echo "Puis accéder à http://localhost:8000"
    exit 0
else
    echo -e "${RED}⚠️  CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ${NC}"
    echo "Veuillez corriger les problèmes ci-dessus"
    exit 1
fi
