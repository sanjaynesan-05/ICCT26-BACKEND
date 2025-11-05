#!/bin/bash

echo "🚀 ICCT26 PostgreSQL Setup Script (Linux/macOS)"
echo "=============================================="
echo

# Check if running on supported OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    PACKAGE_MANAGER="apt"
    SERVICE_CMD="systemctl"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    PACKAGE_MANAGER="brew"
    SERVICE_CMD="brew services"
else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "This script supports Linux and macOS only."
    exit 1
fi

echo "✅ Detected OS: $OS"

# Check if PostgreSQL is installed
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL is already installed"
    psql --version
else
    echo "❌ PostgreSQL not found"

    if [[ "$OS" == "linux" ]]; then
        echo "📦 Installing PostgreSQL on Linux..."
        sudo apt update
        sudo apt install -y postgresql postgresql-contrib
    elif [[ "$OS" == "macos" ]]; then
        echo "📦 Installing PostgreSQL on macOS..."
        if ! command -v brew &> /dev/null; then
            echo "❌ Homebrew not found. Please install Homebrew first:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        brew install postgresql@17
    fi
fi

# Start PostgreSQL service
echo
echo "🔄 Starting PostgreSQL service..."
if [[ "$OS" == "linux" ]]; then
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
elif [[ "$OS" == "macos" ]]; then
    brew services start postgresql@17
fi

# Wait a moment for service to start
sleep 3

# Check if service is running
if [[ "$OS" == "linux" ]]; then
    if sudo systemctl is-active --quiet postgresql; then
        echo "✅ PostgreSQL service is running"
    else
        echo "❌ PostgreSQL service failed to start"
        exit 1
    fi
elif [[ "$OS" == "macos" ]]; then
    if brew services list | grep postgresql | grep started &> /dev/null; then
        echo "✅ PostgreSQL service is running"
    else
        echo "❌ PostgreSQL service failed to start"
        exit 1
    fi
fi

# Set up database user and database
echo
echo "🔧 Setting up database user and database..."

# Set password for postgres user
echo "Setting postgres user password..."
if [[ "$OS" == "linux" ]]; then
    sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';" 2>/dev/null
    if [[ $? -ne 0 ]]; then
        echo "⚠️  Could not set password automatically. You may need to set it manually:"
        echo "   sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'your_password';\""
    fi
elif [[ "$OS" == "macos" ]]; then
    psql -U postgres -c "ALTER USER postgres PASSWORD 'password';" 2>/dev/null
    if [[ $? -ne 0 ]]; then
        echo "⚠️  Could not set password automatically. You may need to set it manually:"
        echo "   psql -U postgres -c \"ALTER USER postgres PASSWORD 'your_password';\""
    fi
fi

# Create database
echo "Creating icct26_db database..."
if [[ "$OS" == "linux" ]]; then
    sudo -u postgres createdb icct26_db 2>/dev/null
elif [[ "$OS" == "macos" ]]; then
    createdb icct26_db 2>/dev/null
fi

if [[ $? -eq 0 ]]; then
    echo "✅ Database 'icct26_db' created successfully"
else
    echo "⚠️  Could not create database. It may already exist."
fi

echo
echo "🎉 PostgreSQL setup complete!"
echo
echo "📋 Next steps:"
echo "1. Update DATABASE_URL in .env file if you changed the password:"
echo "   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/icct26_db"
echo "2. Run database setup: python scripts/setup_database.py"
echo "3. Start the backend: python main.py"
echo "4. Test registration: python scripts/test_registration_simple.py"
echo
echo "📖 For detailed instructions, see: POSTGRESQL_SETUP.md"
echo
echo "Press Enter to continue..."
read