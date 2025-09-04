#!/bin/bash

# EC2 Deployment Script
# Usage: ./deploy_to_ec2.sh [ec2-ip] [key-file]

EC2_IP=${1:-"your-ec2-ip"}
KEY_FILE=${2:-"your-key.pem"}

echo "🚀 Deploying to EC2: $EC2_IP"
echo "=================================="

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ Key file $KEY_FILE not found!"
    exit 1
fi

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf invoicegen-backend.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env*' \
    --exclude='invoicegen.db' \
    --exclude='backups' \
    --exclude='*.log' \
    .

# Upload to EC2
echo "📤 Uploading to EC2..."
scp -i "$KEY_FILE" invoicegen-backend.tar.gz ubuntu@$EC2_IP:/tmp/

# Deploy on EC2
echo "🔧 Deploying on EC2..."
ssh -i "$KEY_FILE" ubuntu@$EC2_IP << 'ENDSSH'
    # Navigate to application directory
    cd /opt/invoicegen/invoiceGen_backend
    
    # Extract new code
    tar -xzf /tmp/invoicegen-backend.tar.gz -C .
    
    # Install dependencies
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Copy production environment
    cp .env.production .env
    
    # Run migrations
    python -c "
from database import engine, Base
from models import *
print('Creating PostgreSQL schema...')
Base.metadata.create_all(bind=engine)
print('✅ Schema created successfully!')
"
    
    # Populate master data
    python manage_master_data.py populate
    
    # Restart service
    sudo systemctl restart invoicegen
    
    # Check status
    sudo systemctl status invoicegen --no-pager
    
    echo "✅ Deployment completed!"
ENDSSH

# Cleanup
rm invoicegen-backend.tar.gz

echo "🎉 EC2 deployment completed!"
