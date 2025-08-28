# PyLadies Seoul Deployment Runbook

This runbook provides comprehensive procedures for deploying, operating, and maintaining the PyLadies Seoul website in production.

## Table of Contents

1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Production Deployment](#production-deployment)
3. [Staging Deployment](#staging-deployment)
4. [Rollback Procedures](#rollback-procedures)
5. [Monitoring and Alerting](#monitoring-and-alerting)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance Tasks](#maintenance-tasks)
8. [Emergency Procedures](#emergency-procedures)

## Pre-deployment Checklist

### Code Quality Checks
- [ ] All tests pass (unit, integration, e2e)
- [ ] Code coverage meets minimum requirements (80%+)
- [ ] Security scan completed with no high/critical issues
- [ ] Performance tests pass
- [ ] Accessibility tests pass
- [ ] Code review completed and approved

### Infrastructure Checks
- [ ] SSL certificates are valid and not expiring soon
- [ ] Database backup completed successfully
- [ ] All secrets are properly configured
- [ ] Monitoring and alerting are functional
- [ ] Rollback plan is documented and tested

### Environment Preparation
- [ ] Production environment variables updated
- [ ] Docker images built and tested
- [ ] Database migrations tested in staging
- [ ] Static files compilation verified
- [ ] Third-party service integrations tested

## Production Deployment

### Automated Deployment (Recommended)

Use GitHub Actions for automated deployments:

```bash
# Tag a release for production deployment
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Or trigger manual deployment
gh workflow run deploy-production.yml -f version=v1.0.0
```

### Manual Deployment (Emergency Only)

#### 1. Pre-deployment Backup

```bash
# SSH to production server
ssh deploy@pyladiesseoul.org

# Navigate to application directory
cd /opt/pyladies-seoul

# Create comprehensive backup
./scripts/backup.sh full

# Backup current Docker images
docker save $(docker-compose -f docker-compose.prod.yml config --services | xargs -I {} docker-compose -f docker-compose.prod.yml images -q {}) | gzip > backups/docker-images-$(date +%Y%m%d_%H%M%S).tar.gz
```

#### 2. Enable Maintenance Mode

```bash
# Enable maintenance mode
docker-compose -f docker-compose.prod.yml exec nginx \
  cp /etc/nginx/conf.d/maintenance.conf /etc/nginx/conf.d/default.conf
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

# Verify maintenance mode is active
curl -I https://pyladiesseoul.org
```

#### 3. Deploy Application

```bash
# Pull latest code
git fetch --tags
git checkout v1.0.0

# Set environment variables
export BUILD_DATE=$(date -Iseconds)
export GIT_COMMIT=$(git rev-parse HEAD)

# Build and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
./scripts/migrate.sh

# Collect static files
docker-compose -f docker-compose.prod.yml exec web \
  python manage.py collectstatic --noinput --settings=config.settings.production
```

#### 4. Disable Maintenance Mode

```bash
# Disable maintenance mode
docker-compose -f docker-compose.prod.yml exec nginx \
  cp /etc/nginx/conf.d/production.conf /etc/nginx/conf.d/default.conf
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

# Verify site is accessible
curl -f https://pyladiesseoul.org/health/
```

#### 5. Post-deployment Verification

```bash
# Run comprehensive health checks
./scripts/health-check.sh --comprehensive

# Monitor logs for errors
docker-compose -f docker-compose.prod.yml logs --tail=100 -f
```

## Staging Deployment

Staging deployments are automated on pushes to the `develop` branch:

```bash
# Deploy to staging
git checkout develop
git pull origin develop
git push origin develop

# Manual staging deployment
gh workflow run deploy-staging.yml
```

### Staging Environment Access

- **URL**: https://staging.pyladiesseoul.org
- **Admin**: https://staging.pyladiesseoul.org/admin/
- **Monitoring**: Available through production monitoring stack

## Rollback Procedures

### Automated Rollback

```bash
# Rollback using previous Docker images
./scripts/rollback.sh --to-previous

# Rollback to specific version
./scripts/rollback.sh --to-version=v0.9.0
```

### Manual Rollback

#### 1. Immediate Rollback (Emergency)

```bash
# Enable maintenance mode
docker-compose -f docker-compose.prod.yml exec nginx \
  cp /etc/nginx/conf.d/maintenance.conf /etc/nginx/conf.d/default.conf
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

# Restore from backup
./scripts/restore.sh latest --clean

# Rollback Docker containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Disable maintenance mode
docker-compose -f docker-compose.prod.yml exec nginx \
  cp /etc/nginx/conf.d/production.conf /etc/nginx/conf.d/default.conf
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

#### 2. Database Rollback

```bash
# If database changes need to be reverted
./scripts/restore.sh /backups/pre_deployment_YYYYMMDD_HHMMSS.sql.gz --clean

# Run any necessary reverse migrations
docker-compose -f docker-compose.prod.yml exec web \
  python manage.py migrate app_name migration_name --settings=config.settings.production
```

## Monitoring and Alerting

### Key Metrics to Monitor

#### Application Metrics
- Response time (< 2 seconds for 95th percentile)
- Error rate (< 1% for 5xx errors)
- Request throughput
- Database query performance
- Memory and CPU usage

#### Infrastructure Metrics
- SSL certificate expiration
- Disk space usage (< 80%)
- Database connections
- Redis memory usage
- Container health status

### Alerting Channels

- **Critical**: Slack #incidents + SMS
- **Warning**: Slack #monitoring
- **Info**: Email notifications

### Monitoring Tools

- **APM**: Elastic APM Server
- **Logs**: Promtail + Loki + Grafana
- **Metrics**: Prometheus + Grafana
- **Uptime**: External monitoring service
- **SSL**: SSL Labs monitoring

## Troubleshooting

### Common Issues

#### Application Not Responding

```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs web --tail=100

# Check resource usage
docker stats

# Restart application container
docker-compose -f docker-compose.prod.yml restart web
```

#### Database Connection Issues

```bash
# Check database status
docker-compose -f docker-compose.prod.yml ps db

# Check database logs
docker-compose -f docker-compose.prod.yml logs db --tail=100

# Test database connectivity
docker-compose -f docker-compose.prod.yml exec web \
  python manage.py dbshell --settings=config.settings.production
```

#### SSL Certificate Issues

```bash
# Check certificate status
./scripts/setup-ssl.sh status

# Test SSL configuration
./scripts/setup-ssl.sh test

# Renew certificates (if needed)
./scripts/setup-ssl.sh renew --force-renewal
```

#### High Memory Usage

```bash
# Check memory usage by container
docker stats --no-stream

# Restart containers with high memory usage
docker-compose -f docker-compose.prod.yml restart web

# Clear cache if needed
docker-compose -f docker-compose.prod.yml exec web \
  python manage.py clear_cache --settings=config.settings.production
```

#### Load Balancer Issues

```bash
# Check Nginx status
docker-compose -f docker-compose.prod.yml ps nginx

# Check Nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload Nginx configuration
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Log Locations

```bash
# Application logs
/opt/pyladies-seoul/data/logs/django.log

# Nginx logs
/opt/pyladies-seoul/data/logs/nginx/access.log
/opt/pyladies-seoul/data/logs/nginx/error.log

# Database logs
/opt/pyladies-seoul/data/logs/postgresql/

# Container logs
docker-compose -f docker-compose.prod.yml logs [service_name]
```

## Maintenance Tasks

### Daily Tasks
- [ ] Check system alerts and notifications
- [ ] Review application logs for errors
- [ ] Monitor resource usage trends
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Review and analyze performance metrics
- [ ] Check SSL certificate status
- [ ] Update security patches (if available)
- [ ] Clean up old log files and backups

### Monthly Tasks
- [ ] Review and update monitoring thresholds
- [ ] Perform disaster recovery test
- [ ] Update documentation
- [ ] Security audit and review

### Automated Maintenance

```bash
# Set up automated maintenance cron jobs
crontab -e

# Daily backup (already set up via docker-compose)
# 0 2 * * * /opt/pyladies-seoul/scripts/backup.sh full

# Weekly SSL certificate check
# 0 0 * * 0 /opt/pyladies-seoul/scripts/setup-ssl.sh renew

# Monthly cleanup
# 0 3 1 * * /opt/pyladies-seoul/scripts/cleanup.sh
```

## Emergency Procedures

### Site Down (P0 - Critical)

1. **Immediate Response**
   ```bash
   # Check if it's a planned maintenance
   curl -I https://pyladiesseoul.org
   
   # If not planned, check container status
   docker-compose -f docker-compose.prod.yml ps
   
   # Restart all services
   docker-compose -f docker-compose.prod.yml restart
   ```

2. **If issue persists**
   ```bash
   # Enable maintenance mode
   docker-compose -f docker-compose.prod.yml exec nginx \
     cp /etc/nginx/conf.d/maintenance.conf /etc/nginx/conf.d/default.conf
   docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
   
   # Investigate and fix the issue
   # Once fixed, disable maintenance mode
   ```

3. **Communication**
   - Post status update on social media
   - Send notification to stakeholders
   - Update status page (if available)

### Data Loss (P0 - Critical)

1. **Stop all writes**
   ```bash
   # Enable maintenance mode immediately
   docker-compose -f docker-compose.prod.yml exec nginx \
     cp /etc/nginx/conf.d/maintenance.conf /etc/nginx/conf.d/default.conf
   docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
   ```

2. **Assess damage**
   ```bash
   # Check database integrity
   docker-compose -f docker-compose.prod.yml exec db \
     pg_dump -U postgres pyladies_seoul > /dev/null
   ```

3. **Restore from backup**
   ```bash
   # Restore from latest backup
   ./scripts/restore.sh latest --clean
   ```

### Security Breach (P0 - Critical)

1. **Immediate containment**
   ```bash
   # Take site offline
   docker-compose -f docker-compose.prod.yml down
   ```

2. **Assessment**
   - Review logs for suspicious activity
   - Check for unauthorized changes
   - Assess scope of potential data exposure

3. **Recovery**
   - Change all passwords and API keys
   - Restore from known good backup
   - Apply security patches
   - Conduct security audit

### Performance Degradation (P1 - High)

1. **Identify bottleneck**
   ```bash
   # Check resource usage
   docker stats
   
   # Check slow queries
   docker-compose -f docker-compose.prod.yml logs db | grep "slow query"
   
   # Check application performance
   curl -w "%{time_total}\n" -o /dev/null -s https://pyladiesseoul.org
   ```

2. **Mitigation**
   ```bash
   # Scale up containers if needed
   docker-compose -f docker-compose.prod.yml up -d --scale web=3
   
   # Clear cache
   docker-compose -f docker-compose.prod.yml exec web \
     python manage.py clear_cache --settings=config.settings.production
   ```

## Contact Information

### Emergency Contacts
- **Primary On-call**: [Phone] [Email]
- **Secondary On-call**: [Phone] [Email]
- **Escalation**: [Phone] [Email]

### Service Providers
- **Hosting Provider**: [Contact Details]
- **Domain Registrar**: [Contact Details]
- **SSL Certificate Provider**: Let's Encrypt (automated)
- **Monitoring Service**: [Contact Details]

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2024-01-01 | Initial runbook | DevOps Team |

---

**Remember**: Always test procedures in staging before applying to production. When in doubt, prioritize safety over speed.