# Production Deployment Guide

## Prerequisites

### System Requirements
- Ubuntu 20.04 LTS or later
- 4 CPU cores minimum
- 8GB RAM minimum
- 50GB storage minimum
- Docker & Docker Compose installed
- Kubernetes cluster (for k8s deployment)

### Software Requirements
- Python 3.13+
- Node.js 18+
- PostgreSQL 15+ (optional)
- Nginx 1.18+ (for reverse proxy)

## Deployment Options

### Option 1: Docker Compose (Recommended for small-medium scale)

#### Step 1: Prepare environment
```bash
# Clone repository
git clone https://github.com/yourusername/telecom-outage-intelligence.git
cd telecom-outage-intelligence

# Create .env file
cat > .env << EOF
DB_PASSWORD=secure_password_here
API_URL=https://noc.yourdomain.com/api
LOG_LEVEL=INFO
EOF

# Create SSL certificates
mkdir -p ssl
# Copy your SSL certificates to ssl/ directory
```

#### Step 2: Build and start services
```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify services
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs backend
```

#### Step 3: Verify deployment
```bash
# Health check
curl http://localhost:8000/api/health

# Test frontend
curl http://localhost:3000

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Option 2: Kubernetes (Production scale)

#### Step 1: Prepare cluster
```bash
# Create namespace
kubectl create namespace production

# Create secrets
kubectl create secret generic telecom-noc-secrets \
  --from-literal=db-password=secure_password \
  -n production

# Create config
kubectl create configmap telecom-noc-config \
  --from-literal=api_url=https://noc.yourdomain.com/api \
  -n production
```

#### Step 2: Deploy application
```bash
# Push image to registry
docker tag telecom-noc:latest yourregistry/telecom-noc:latest
docker push yourregistry/telecom-noc:latest

# Deploy
kubectl apply -f k8s/deployment-prod.yaml

# Verify deployment
kubectl get deployments -n production
kubectl get pods -n production
kubectl get services -n production
```

#### Step 3: Configure ingress
```bash
# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml

# Deploy ingress
kubectl apply -f k8s/ingress-prod.yaml

# Check ingress status
kubectl get ingress -n production
```

### Option 3: Manual Deployment (Advanced)

#### Step 1: Set up backend
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn main:app -w 4 -b 0.0.0.0:8000 --timeout 60 --daemon
```

#### Step 2: Set up frontend
```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve with production server
npm install -g serve
serve -s dist -l 3000 -d
```

#### Step 3: Configure reverse proxy
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/telecom-noc
sudo ln -s /etc/nginx/sites-available/telecom-noc /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Start nginx
sudo systemctl restart nginx
```

## Configuration

### Environment Variables

#### Backend (.env)
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/telecom_noc

# API
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
CORS_ORIGINS=https://noc.yourdomain.com

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=noc.yourdomain.com
```

#### Frontend (.env.production)
```
VITE_API_URL=https://noc.yourdomain.com/api
VITE_ENV=production
VITE_ENABLE_DEBUG=false
```

### Nginx Configuration

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name noc.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name noc.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API proxy
    location /api/ {
        proxy_pass http://backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Monitoring & Logging

### Health Checks
```bash
# Backend health
curl https://noc.yourdomain.com/api/health

# Response
{
  "status": "healthy",
  "version": "0.8.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Metrics
```bash
# Prometheus metrics
curl https://noc.yourdomain.com/api/metrics
```

### Logging
```bash
# View backend logs
docker-compose logs backend

# View frontend logs
docker-compose logs frontend

# View nginx logs
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

### Performance Monitoring
```bash
# CPU usage
docker stats

# Memory usage
docker-compose exec backend free -h

# Disk usage
df -h
```

## Backup & Recovery

### Database Backup
```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U noc_user telecom_noc > backup.sql

# Restore
docker-compose exec db psql -U noc_user telecom_noc < backup.sql
```

### Data Files Backup
```bash
# Backup CSV data
tar -czf data_backup.tar.gz backend/data/

# Restore
tar -xzf data_backup.tar.gz
```

### Configuration Backup
```bash
# Backup environment and configs
tar -czf config_backup.tar.gz .env* *.conf

# Keep in secure location
```

## Scaling

### Horizontal Scaling
```bash
# Increase backend replicas
kubectl scale deployment telecom-noc-backend --replicas=5 -n production

# Increase frontend replicas
kubectl scale deployment telecom-noc-frontend --replicas=3 -n production
```

### Load Balancing
Already configured in:
- Docker Compose: nginx service
- Kubernetes: Ingress controller

## Security Hardening

### SSL/TLS
```bash
# Generate certificates (Let's Encrypt)
certbot certonly --standalone -d noc.yourdomain.com

# Verify SSL
ssl-test-cli https://noc.yourdomain.com
```

### Rate Limiting
```nginx
# Add to nginx config
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;

location /api/ {
    limit_req zone=api burst=50 nodelay;
}
```

### Firewall
```bash
# UFW rules
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs backend

# Check port conflicts
netstat -tlnp | grep 8000

# Restart services
docker-compose down
docker-compose up -d
```

### High memory usage
```bash
# Check memory limits
docker stats

# Restart service
docker-compose restart backend

# Increase memory limit in docker-compose.yml
```

### Database connection issues
```bash
# Test connection
psql -h localhost -U noc_user -d telecom_noc -c "SELECT 1"

# Check database logs
docker-compose logs db
```

### API not responding
```bash
# Health check
curl http://localhost:8000/api/health

# Check backend status
docker-compose ps backend

# View backend logs
docker-compose logs backend
```

## Update Procedure

### Blue-Green Deployment
```bash
# Deploy new version alongside current
docker build -t telecom-noc:v0.9.0 .

# Run new version on different port
docker run -p 8001:8000 telecom-noc:v0.9.0

# Test new version
curl http://localhost:8001/api/health

# Switch traffic with nginx
# Update upstream to point to new version
# Reload nginx
sudo systemctl reload nginx

# Stop old version
docker stop <old-container-id>
```

### Rolling Update (Kubernetes)
```bash
# Update image
kubectl set image deployment/telecom-noc-backend \
  backend=yourregistry/telecom-noc:v0.9.0 \
  -n production

# Monitor rollout
kubectl rollout status deployment/telecom-noc-backend -n production

# Rollback if needed
kubectl rollout undo deployment/telecom-noc-backend -n production
```

## Support & Escalation

For issues contact: devops@yourdomain.com

On-call escalation:
1. Try troubleshooting steps above
2. Check monitoring dashboards
3. Review recent changes
4. Contact platform team
5. If database issue: contact DBA team
