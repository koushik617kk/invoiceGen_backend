#!/bin/bash

# Deploy to EC2 and migrate data
# Usage: ./deploy_to_ec2.sh your-ec2-ip your-key.pem

EC2_IP=$1
KEY_FILE=$2

if [ -z "$EC2_IP" ] || [ -z "$KEY_FILE" ]; then
    echo "Usage: ./deploy_to_ec2.sh <EC2_IP> <KEY_FILE>"
    echo "Example: ./deploy_to_ec2.sh 3.15.123.45 my-key.pem"
    exit 1
fi

echo "🚀 Deploying to EC2: $EC2_IP"

# 1. Copy database file
echo "📁 Copying SQLite database..."
scp -i $KEY_FILE invoicegen.db ec2-user@$EC2_IP:/home/ec2-user/

# 2. Copy migration script
echo "📄 Copying migration script..."
scp -i $KEY_FILE migrate_sqlite_to_postgres.py ec2-user@$EC2_IP:/home/ec2-user/

# 3. Run migration on EC2
echo "🔄 Running migration on EC2..."
ssh -i $KEY_FILE ec2-user@$EC2_IP << 'EOF'
    cd /home/ec2-user
    python3 migrate_sqlite_to_postgres.py
EOF

echo "✅ Deployment and migration completed!"