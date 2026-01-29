@echo off
REM Script pour gérer PostgreSQL sous Windows

setlocal enabledelayedexpansion

echo.
echo 🐘 PostgreSQL - Device Management
echo ==================================
echo.

if "%1"=="start" (
    echo Demarrage de PostgreSQL...
    docker-compose -f docker-compose-dev.yml up -d
    timeout /t 5 /nobreak
    echo.
    echo ✅ PostgreSQL demarré sur localhost:5432
    echo ✅ pgAdmin disponible sur http://localhost:5050 (admin/admin)
    echo.
    echo Credentials:
    echo   Host: localhost
    echo   Port: 5432
    echo   Database: device_management
    echo   User: postgres
    echo   Password: postgres
    goto :eof
)

if "%1"=="stop" (
    echo Arret de PostgreSQL...
    docker-compose -f docker-compose-dev.yml down
    echo ✅ PostgreSQL arrêté
    goto :eof
)

if "%1"=="logs" (
    docker-compose -f docker-compose-dev.yml logs -f postgres
    goto :eof
)

if "%1"=="clean" (
    echo Nettoyage complet (suppression donnees)...
    docker-compose -f docker-compose-dev.yml down -v
    echo ✅ Donnees supprimees
    goto :eof
)

if "%1"=="init" (
    echo Initialisation de la base de donnees...
    call "!CD!\.venv\Scripts\python.exe" init_db.py
    goto :eof
)

if "%1"=="run" (
    echo Demarrage de l'application...
    call "!CD!\.venv\Scripts\python.exe" main.py
    goto :eof
)

REM Sinon, afficher l'aide
echo Usage: postgres.bat [start^|stop^|logs^|clean^|init^|run]
echo.
echo   start   - Demarrer PostgreSQL (Docker)
echo   stop    - Arreter PostgreSQL
echo   logs    - Afficher les logs
echo   clean   - Arreter et supprimer les donnees
echo   init    - Initialiser la base de donnees
echo   run     - Lancer l'application
echo.
