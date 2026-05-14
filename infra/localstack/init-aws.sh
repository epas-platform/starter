#!/bin/bash
# LocalStack Initialization Script
# Runs automatically when LocalStack is ready

set -euo pipefail

echo "=== Initializing LocalStack AWS Resources ==="

# S3 Buckets
echo "Creating S3 buckets..."
awslocal s3 mb s3://epas-prototype-uploads --region us-east-1 || true
awslocal s3 mb s3://epas-prototype-exports --region us-east-1 || true

# Set CORS for uploads bucket (frontend direct upload support)
awslocal s3api put-bucket-cors --bucket epas-prototype-uploads --cors-configuration '{
  "CORSRules": [{
    "AllowedOrigins": ["http://localhost:3000", "http://127.0.0.1:3000"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3000
  }]
}'

echo "S3 buckets created."

# Secrets Manager
echo "Creating secrets..."

# JWT signing key
awslocal secretsmanager create-secret \
  --name "epas-prototype/dev/jwt" \
  --secret-string '{"secret":"dev-jwt-secret-32-characters-minimum!","algorithm":"HS256","expiry_hours":24}' \
  --region us-east-1 || true

# Database credentials
awslocal secretsmanager create-secret \
  --name "epas-prototype/dev/database" \
  --secret-string '{"username":"epas_prototype","password":"epas_prototype","host":"postgres","port":"5432","dbname":"epas_prototype"}' \
  --region us-east-1 || true

# External API keys (placeholder for future use)
awslocal secretsmanager create-secret \
  --name "epas-prototype/dev/external-apis" \
  --secret-string '{"openai_key":"sk-placeholder","anthropic_key":"sk-placeholder"}' \
  --region us-east-1 || true

echo "Secrets created."

# Verification
echo ""
echo "=== Verification ==="
echo "S3 Buckets:"
awslocal s3 ls

echo ""
echo "Secrets:"
awslocal secretsmanager list-secrets --query 'SecretList[].Name' --output table

echo ""
echo "=== LocalStack initialization complete ==="
