@echo off
echo ========================================================
echo   Starting Neo4j Graph Database for Digital Legacy Vault
echo ========================================================

docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not detected in PATH.
    echo If using Neo4j Desktop, launch Neo4j Desktop and start your database on port 7687.
    echo If using Neo4j AuraDB, configure your .env file with your cloud URI.
    pause
    exit /b 1
)

echo Starting Neo4j container via docker-compose...
docker-compose up -d

echo.
echo Neo4j is starting up!
echo - Neo4j Browser UI: http://localhost:7474 (Username: neo4j, Password: password123)
echo - Bolt Connection:  bolt://localhost:7687
echo.
echo Please wait 10-15 seconds for Neo4j initialization before starting the backend.
pause
