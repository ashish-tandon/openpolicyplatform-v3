# API Schemas (Examples)

## POST /api/v1/auth/login (form)
Request (x-www-form-urlencoded):
- username: string
- password: string

Response 200:
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@openpolicy.com",
    "full_name": "System Administrator",
    "role": "admin",
    "permissions": ["read", "write", "admin", "delete"]
  }
}
```

## GET /api/v1/health/detailed
Response 200 (example):
```json
{
  "status": "healthy",
  "service": "Open Policy Platform API",
  "version": "1.0.0",
  "environment": "development",
  "database": "healthy",
  "timestamp": "2024-08-08T12:00:00Z",
  "uptime": "1:23:45",
  "system_metrics": {
    "cpu_percent": 12.5,
    "memory_percent": 45.1,
    "disk_percent": 70.3,
    "active_processes": 231
  }
}
```

## GET /api/v1/policies
Query params: `page`, `limit`, `search?`, `category?`, `jurisdiction?`, `status?`

Response 200 (example):
```json
{
  "policies": [
    {
      "id": "123",
      "title": "An Act to Amend ...",
      "content": "...",
      "category": "health",
      "jurisdiction": "federal",
      "status": "introduced",
      "created_at": "2024-07-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 10,
  "pages": 10,
  "filters": {
    "search": "health",
    "category": "health",
    "jurisdiction": null,
    "status": null
  }
}
```