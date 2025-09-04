#!/bin/bash

# Backend Deployment Script
# Usage: ./deploy.sh [dev|prod]

ENV=${1:-dev}

echo "🚀 Deploying Backend - Environment: $ENV"
echo "========================================"

# Check if environment file exists
if [ "$ENV" = "prod" ]; then
    ENV_FILE=".env.production"
    echo "📦 Production deployment..."
else
    ENV_FILE=".env.development"
    echo "🔧 Development deployment..."
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Environment file $ENV_FILE not found!"
    echo "   Please create it from .env.example"
    exit 1
fi

# Copy environment file
echo "📋 Copying environment configuration..."
cp "$ENV_FILE" .env

# Install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Run migrations for production
if [ "$ENV" = "prod" ]; then
    echo "🗄️  Running database migrations..."
    python -c "
from database import engine, Base
from models import *
print('Creating PostgreSQL schema...')
Base.metadata.create_all(bind=engine)
print('✅ Schema created successfully!')
"
    
    echo "📊 Populating master data..."
    python manage_master_data.py populate
fi

# Start service
if [ "$ENV" = "prod" ]; then
    echo "🔄 Restarting production service..."
    sudo systemctl restart invoicegen
    echo "✅ Production backend deployed!"
    echo "   Check status: sudo systemctl status invoicegen"
else
    echo "🔧 Starting development server..."
    echo "   Backend will be available at: http://localhost:8000"
    python main.py
fi
