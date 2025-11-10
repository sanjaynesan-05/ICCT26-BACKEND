#!/usr/bin/env bash
# ICCT26 Backend - Quick Start Commands

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   ICCT26 Cricket Tournament Registration API - Quick Start    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Install dependencies (if needed)
echo "📦 Installing dependencies (if first time):"
echo "   pip install -r requirements.txt"
echo ""

# Run the application
echo "🚀 START THE SERVER:"
echo ""
echo "   Option 1 - Using main.py directly:"
echo "   python main.py"
echo ""
echo "   Option 2 - Using uvicorn:"
echo "   uvicorn main:app --reload"
echo ""
echo "   Option 3 - Production mode:"
echo "   uvicorn main:app --host 0.0.0.0 --port 8000"
echo ""

# API Documentation
echo "📚 API DOCUMENTATION:"
echo "   • Swagger UI:  http://localhost:8000/docs"
echo "   • ReDoc:       http://localhost:8000/redoc"
echo ""

# Health Check
echo "✅ VERIFY SERVER IS RUNNING:"
echo "   curl http://localhost:8000/health"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Application entry point: main.py"
echo "Database config: database.py"
echo "ORM Models: models.py"
echo "App modules: app/ package"
echo ""
