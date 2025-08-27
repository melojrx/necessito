# 🚀 Deployment Checklist - Necessito Production

## Pre-Deployment Checklist

### 1. Repositório (Local ou Git Pull)
- [ ] Acesso ao repositório via git funcionando (SSH ou HTTPS)
- [ ] Branch main atualizado (git pull)
- [ ] Permissões corretas de execução em scripts (`chmod +x scripts/*.sh`)

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

### 3. Primeiro Deploy
Opção A (build local):
```bash
./scripts/deploy.sh
```
Opção B (imagem de registry):
```bash
export REGISTRY_IMAGE=ghcr.io/SEU_USER/necessito-web
export IMAGE_TAG=latest
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

## Processo Regular de Deploy Manual

1. `git pull origin main`
2. (Se quiser build limpo) remover imagem anterior opcionalmente
3. Rodar `./scripts/deploy.sh` (com ou sem variáveis de registry)
4. Confirmar health / logs

### 3. Post-Deployment Checks
- [ ] Application accessible
- [ ] Database migrations applied
- [ ] Static files updated
- [ ] All services running
- [ ] Logs show no errors
- [ ] Performance metrics normal

## Rollback Procedure

### Se Deploy Falhar
```bash
cd /opt/necessito
./scripts/rollback.sh   # Usa last_success_digest
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