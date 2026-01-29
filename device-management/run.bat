@echo off
REM Script de lancement de l'application Device Management

title Device Management API

echo.
echo ======================================
echo   Device Management API
echo ======================================
echo.

REM Aller dans le répertoire device-management
cd /d "%~dp0"

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

echo Lancement de l'application...
echo.
echo 🚀 Accédez à: http://localhost:8000
echo 📚 Documentation: http://localhost:8000/docs
echo 🏥 Health check: http://localhost:8000/health
echo.

REM Lancer l'application
python main.py

pause
