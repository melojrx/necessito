# 🚀 Deployment Checklist - Necessito Production

## Pre-Deployment Checklist

### 1. GitHub Repository Setup
- [ ] Repository secrets configured:
  - [ ] `SSH_HOST` - VPS IP address
  - [ ] `SSH_USER` - SSH user (currently root)
  - [ ] `SSH_KEY` - Private SSH key
  - [ ] `SSH_PORT` - SSH port (22 if default)
- [ ] GitHub Container Registry permissions set
- [ ] Actions have write permissions to packages

### 2. VPS Server Preparation
- [ ] Docker and Docker Compose installed
- [ ] SSH key authentication working
- [ ] Nginx global container running with shared network
- [ ] Network `nginx-global_global-network` exists
- [ ] Domain `necessito.online` pointing to VPS
- [ ] SSL certificate configured in global Nginx
- [ ] Firewall configured (ports 80, 443, 22)

### 3. Application Configuration
- [ ] `.env.prod` file created from `.env.prod.example`
- [ ] All environment variables configured:
  - [ ] `DJANGO_SECRET_KEY` (64 characters minimum)
  - [ ] `POSTGRES_PASSWORD` (strong password)
  - [ ] `EMAIL_HOST_PASSWORD` (if email sending required)
  - [ ] `DJANGO_ALLOWED_HOSTS` set to production domain
- [ ] Production settings reviewed (`core/settings/prod.py`)

### 4. Infrastructure Services
- [ ] PostgreSQL data directory permissions set
- [ ] Redis data directory permissions set
- [ ] Backup directory created (`./backups`)
- [ ] Log directory created (`./logs`)
- [ ] Static files directory created (`./staticfiles`)

## Initial Deployment Steps

### 1. Repository Clone
```bash
# On VPS as root
cd /opt
git clone https://github.com/YOUR_USERNAME/necessito.git
cd necessito
```

### 2. Environment Setup
```bash
# Copy and configure environment
cp .env.prod.example .env.prod
nano .env.prod  # Configure all variables

# Ensure script permissions
chmod +x scripts/*.sh
```

### 3. First Deployment
```bash
# Set registry image variables
export REGISTRY_IMAGE=ghcr.io/YOUR_USERNAME/necessito-web
export IMAGE_TAG=latest

# Run initial deployment
./scripts/deploy.sh
```

### 4. Post-Deployment Verification
- [ ] Health check responds: `curl -I https://necessito.online/health/`
- [ ] Application loads: `https://necessito.online`
- [ ] Admin panel accessible: `https://necessito.online/admin/`
- [ ] API documentation: `https://necessito.online/api/docs/`
- [ ] Static files serving correctly
- [ ] Media files upload working
- [ ] WebSocket connections working (chat)

## Regular Deployment Process

### 1. CI/CD Pipeline Trigger
- [ ] Push to `main` branch or manual workflow dispatch
- [ ] Tests pass in CI
- [ ] Docker image builds successfully
- [ ] Image pushed to GitHub Container Registry

### 2. Automatic Deployment
- [ ] SSH connection to VPS successful
- [ ] Scripts uploaded to VPS
- [ ] Deployment script execution
- [ ] Health check passes
- [ ] Services restart successfully

### 3. Post-Deployment Checks
- [ ] Application accessible
- [ ] Database migrations applied
- [ ] Static files updated
- [ ] All services running
- [ ] Logs show no errors
- [ ] Performance metrics normal

## Rollback Procedure

### If Deployment Fails
```bash
# On VPS
cd /opt/necessito
export REGISTRY_IMAGE=ghcr.io/YOUR_USERNAME/necessito-web
./scripts/rollback.sh
```

### Verification After Rollback
- [ ] Application accessible
- [ ] Health check passes
- [ ] Services stable
- [ ] Investigate deployment failure
- [ ] Fix issues before next deployment

## Monitoring and Maintenance

### Daily Checks
- [ ] Application health status
- [ ] Log files for errors
- [ ] Disk space usage
- [ ] Database performance
- [ ] SSL certificate validity

### Weekly Tasks
- [ ] Review security logs
- [ ] Check for available updates
- [ ] Verify backup integrity
- [ ] Monitor resource usage

### Monthly Tasks
- [ ] Security audit
- [ ] Performance optimization
- [ ] Dependency updates
- [ ] Backup rotation cleanup

## Emergency Contacts and Procedures

### Critical Issues
1. **Application Down**: Check health endpoint, review logs, consider rollback
2. **Database Issues**: Check PostgreSQL logs, verify connections
3. **SSL Certificate**: Verify certificate renewal, check global Nginx
4. **High Load**: Check resource usage, scale if necessary

### Support Contacts
- **Development Team**: [contact information]
- **Infrastructure Team**: [contact information]
- **Domain/DNS Provider**: [contact information]
- **VPS Provider**: [contact information]

## Security Checklist

### Application Security
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] CSRF protection enabled
- [ ] XSS protection enabled
- [ ] SQL injection protections
- [ ] File upload restrictions

### Infrastructure Security
- [ ] SSH key authentication only
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] Log monitoring
- [ ] Intrusion detection
- [ ] Backup encryption

## Performance Optimization

### Application Level
- [ ] Database query optimization
- [ ] Static file compression
- [ ] Cache configuration
- [ ] CDN for media files (future)

### Infrastructure Level
- [ ] Resource monitoring
- [ ] Load balancing (if needed)
- [ ] Database optimization
- [ ] Redis memory management

## Troubleshooting Guide

### Common Issues

#### 1. Health Check Fails
```bash
# Check application logs
docker compose -f docker-compose_prod.yml logs web

# Check database connection
docker compose -f docker-compose_prod.yml exec db psql -U postgres -c "SELECT 1;"

# Check Redis connection
docker compose -f docker-compose_prod.yml exec redis redis-cli ping
```

#### 2. Static Files Not Loading
```bash
# Recollect static files
./scripts/collectstatic.sh

# Check Nginx configuration
docker compose -f docker-compose_prod.yml exec nginx nginx -t
```

#### 3. Database Migration Issues
```bash
# Check migration status
docker compose -f docker-compose_prod.yml exec web python manage.py showmigrations

# Apply migrations manually
./scripts/migrate.sh
```

#### 4. SSL Certificate Issues
- Check global Nginx configuration
- Verify domain DNS records
- Check certificate expiration
- Review Let's Encrypt logs

## Documentation Updates

This checklist should be updated whenever:
- [ ] New environment variables are added
- [ ] Infrastructure changes are made
- [ ] Security configurations are updated
- [ ] New services are added
- [ ] Deployment process changes

---

**Last Updated**: [Date]
**Version**: 1.0.0
**Environment**: Production