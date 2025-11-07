@echo off
echo Setting up PostgreSQL for ICCT26 Backend...
echo.

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ PostgreSQL not found in PATH
    echo Please install PostgreSQL from: https://www.postgresql.org/download/windows/
    echo Then run this script again.
    pause
    exit /b 1
)

echo ✅ PostgreSQL found

REM Set PostgreSQL password
echo Setting PostgreSQL password...
psql -U postgres -c "ALTER USER postgres PASSWORD 'password';" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Could not set password. You may need to run as administrator or set it manually.
    echo Run: psql -U postgres -c "ALTER USER postgres PASSWORD 'password';"
)

REM Create database
echo Creating icct26_db database...
createdb -U postgres icct26_db 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Could not create database. It may already exist or you need different credentials.
)

echo.
echo ✅ PostgreSQL setup complete!
echo.
echo Next steps:
echo 1. Update DATABASE_URL in .env if needed
echo 2. Run: python scripts\setup_database.py
echo 3. Start server: python main.py
echo.
pause