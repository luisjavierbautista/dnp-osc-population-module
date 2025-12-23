# Docker Deployment - DNP Population Module

## 🚀 All Services Running Successfully!

### Container Status

All three services are running in Docker:

```bash
$ docker compose ps
```

| Service | Container | Status | Ports |
|---------|-----------|--------|-------|
| **Frontend** | `dnp_population_frontend` | ✅ Healthy | 3003:3000 |
| **Backend** | `dnp_population_backend` | ✅ Healthy | 8000:8000 |
| **Database** | `dnp_population_db` | ✅ Healthy | 5434:5432 |

## 🌐 Access Points

### Local Access (Development)

- **Frontend**: http://localhost:3003
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5434 (PostgreSQL)

### Ngrok Tunnels (Production/Public Access)

If you have ngrok tunnels configured:

- **Frontend**: https://dnp.ngrok.app
- **Backend API**: https://dnp-back.ngrok.app
- **API Docs**: https://dnp-back.ngrok.app/docs

## 🎯 LLM Provider Configuration

Both providers are configured and working:

```bash
$ curl http://localhost:8000/api/v1/chats/providers
{
    "available": ["claude", "azure_openai"],
    "default": "azure_openai"
}
```

**Available Providers:**
- ✅ **Azure OpenAI (DNP)** - Default provider
  - Endpoint: `https://dnp-oai-obdies-dev.openai.azure.com/`
  - Model: `gpt-4o`
  - Status: Active and configured

- ✅ **Claude (Anthropic)**
  - Model: `claude-sonnet-4-5-20250929`
  - Status: Active and configured

## 📋 Docker Commands

### Start All Services
```bash
docker compose up -d
```

### Stop All Services
```bash
docker compose down
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f frontend
docker compose logs -f backend
docker compose logs -f db
```

### Restart a Service
```bash
docker compose restart frontend
docker compose restart backend
docker compose restart db
```

### Check Status
```bash
docker compose ps
```

### View Resource Usage
```bash
docker stats dnp_population_frontend dnp_population_backend dnp_population_db
```

## 🔧 Port Mappings

Ports have been adjusted to avoid conflicts with other running services:

- **Frontend**: 3003 → 3000 (internal)
- **Backend**: 8000 → 8000 (internal)
- **Database**: 5434 → 5432 (internal)

**Why these ports?**
- Port 3000: Used by tmsa-frontend
- Port 3001: Used by dcms-frontend
- Port 3002: Used by another service
- Port 5432: Used by tmsa-postgres

## 🗄️ Database Connection

### From Host Machine
```bash
psql -h localhost -p 5434 -U population_user -d population_db
# Password: population_pass
```

### From Docker Containers (Internal)
```
Host: db
Port: 5432
User: population_user
Password: population_pass
Database: population_db
```

## 📦 Volume Management

### View Volumes
```bash
docker volume ls | grep dnp
```

### Backup Database
```bash
docker compose exec db pg_dump -U population_user population_db > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker compose exec -T db psql -U population_user population_db
```

## 🔄 Updating Code

### Frontend or Backend Code Changes

The containers use volume mounts, so code changes are reflected immediately:

**Backend**: Auto-reload enabled via `--reload` flag
**Frontend**: Next.js dev mode with hot reload

No restart needed for code changes!

### Dependency Changes

If you update `package.json` or `requirements.txt`:

```bash
# Rebuild and restart
docker compose up -d --build frontend
docker compose up -d --build backend
```

## 🧪 Testing the Stack

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Test API Providers
```bash
curl http://localhost:8000/api/v1/chats/providers | jq
```

### Test Frontend
```bash
curl -I http://localhost:3003
```

### Test Database Connection
```bash
docker compose exec db psql -U population_user -d population_db -c "SELECT COUNT(*) FROM territorio;"
```

## 🌍 Environment Variables

Current configuration in `.env`:

### Database
```env
POSTGRES_SERVER=db
POSTGRES_USER=population_user
POSTGRES_PASSWORD=population_pass
POSTGRES_DB=population_db
POSTGRES_PORT=5432  # Internal port
```

### LLM Providers
```env
# Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Azure OpenAI (DNP Official)
AZURE_OPENAI_API_KEY=7ZDCNluNf0OQWiNz5dq4...
AZURE_OPENAI_ENDPOINT=https://dnp-oai-obdies-dev.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### Frontend API URL
```env
# For local development
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# For ngrok/production
NEXT_PUBLIC_API_URL=https://dnp-back.ngrok.app/api/v1
```

## 🚨 Troubleshooting

### Frontend Not Loading
```bash
# Check logs
docker compose logs frontend

# Restart
docker compose restart frontend
```

### Backend API Errors
```bash
# Check logs
docker compose logs backend

# Check database connection
docker compose logs db

# Restart both
docker compose restart backend db
```

### Database Connection Issues
```bash
# Check if db is healthy
docker compose ps db

# Check logs
docker compose logs db

# Recreate if needed
docker compose up -d --force-recreate db
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :3003
lsof -i :8000
lsof -i :5434

# Stop the conflicting service or update docker-compose.yml
```

## 📊 Resource Limits

Current resource configuration:

### Backend
- Memory Limit: 8GB
- Memory Reservation: 4GB
- Shared Memory: 2GB

### Frontend
- No specific limits (uses defaults)

### Database
- No specific limits (uses defaults)

## 🔐 Security Notes

1. **Secrets in .env**: Never commit `.env` to version control
2. **Database Password**: Change `population_pass` in production
3. **API Keys**: Rotate keys periodically
4. **CORS**: Update `BACKEND_CORS_ORIGINS` for production domains
5. **Secret Key**: Change `SECRET_KEY` to a strong random value

## 📈 Next Steps

1. **Set up ngrok** (if not already):
   ```bash
   ngrok http 3003 --domain=dnp.ngrok.app
   ngrok http 8000 --domain=dnp-back.ngrok.app
   ```

2. **Test LLM Providers**:
   - Visit http://localhost:3003/chat
   - Try switching between Claude and Azure OpenAI
   - Send test queries

3. **Monitor Logs**:
   ```bash
   docker compose logs -f
   ```

4. **Production Deployment**:
   - Update `.env` with production values
   - Set up proper SSL certificates
   - Configure production database
   - Enable security headers

## 🎉 Success!

All services are running and configured:
- ✅ Frontend accessible at http://localhost:3003
- ✅ Backend API at http://localhost:8000
- ✅ Both LLM providers working (Claude + Azure OpenAI)
- ✅ Provider switching enabled in chat interface
- ✅ Database healthy and accessible

Ready to use! 🚀
