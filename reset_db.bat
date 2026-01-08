@echo off
echo ==========================================
echo      WIPING DATABASE AND RESTARTING
echo ==========================================

echo [1/2] Stopping containers and removing data volume...
docker compose down -v

echo.
echo [2/2] Starting containers...
docker compose up -d

echo.
echo ==========================================
echo      DATABASE RESET COMPLETE!
echo ==========================================
echo You can now reload the web page.
pause
