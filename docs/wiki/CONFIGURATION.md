# CONFIGURATION.md

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://chartsense:chartsense_secret_2026@postgres:5432/chartsense_db` | Yes |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` | Yes |
| `NEO4J_URI` | Neo4j Bolt URI | `bolt://neo4j:7687` | Yes |
| `NEO4J_USER` | Neo4j username | `neo4j` | Yes |
| `NEO4J_PASSWORD` | Neo4j password | `chartsense_neo4j_2026` | Yes |
| `DEMO_MODE` | Enable demo mode | `true` | No |
| `NEXT_PUBLIC_API_URL` | Backend API URL for frontend | `http://localhost:8000` | Yes |

## Configuration Files

### `backend/app/core/config.py`

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://chartsense:chartsense_secret_2026@postgres:5432/chartsense_db"
    REDIS_URL: str = "redis://redis:6379/0"
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "chartsense_neo4j_2026"
    DEMO_MODE: bool = True

    class Config:
        env_file = ".env"
```

### `frontend/next.config.js`

```javascript
module.exports = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};
```

### `docker-compose.yml`

Key configurations:

```yaml
services:
  postgres:
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-chartsense}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-chartsense_secret_2026}
      POSTGRES_DB: ${POSTGRES_DB:-chartsense_db}

  neo4j:
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD:-chartsense_neo4j_2026}

  backend:
    environment:
      DATABASE_URL: postgresql://chartsense:chartsense_secret_2026@postgres:5432/chartsense_db
      REDIS_URL: redis://redis:6379/0
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: chartsense_neo4j_2026
      DEMO_MODE: "true"

  frontend:
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
```