# DEPENDENCIES.md

## Backend Dependencies (`backend/requirements.txt`)

| Package | Version | Rationale |
|---------|---------|-----------|
| `fastapi` | 0.115.0 | Web framework for building APIs |
| `uvicorn` | 0.27.0 | ASGI server for running FastAPI |
| `sqlalchemy` | 2.0.25 | ORM for database interactions |
| `psycopg2-binary` | 2.9.9 | PostgreSQL adapter for Python |
| `redis` | 5.0.1 | Redis client for caching |
| `neo4j` | 5.14.0 | Neo4j driver for graph database |
| `pydantic` | 2.5.3 | Data validation and settings management |
| `python-dotenv` | 1.0.0 | Load environment variables from `.env` |

## Frontend Dependencies (`frontend/package.json`)

| Package | Version | Rationale |
|---------|---------|-----------|
| `next` | 14.0.0 | React framework for server-side rendering |
| `react` | 18.2.0 | UI library for building components |
| `typescript` | 5.3.0 | Type checking for JavaScript |
| `tailwindcss` | 3.3.0 | Utility-first CSS framework |
| `shadcn/ui` | 0.6.0 | UI component library |
| `axios` | 1.6.0 | HTTP client for API calls |

## Infrastructure Dependencies

| Tool | Version | Rationale |
|------|---------|-----------|
| `Docker` | 24.0.0 | Containerization for deployment |
| `docker-compose` | 2.23.0 | Orchestration for multi-container apps |
| `PostgreSQL` | 16.0 | Relational database for structured data |
| `Redis` | 7.0.0 | In-memory cache for performance |
| `Neo4j` | 5.0.0 | Graph database for knowledge graph |
| `Nginx` | 1.25.0 | Reverse proxy and load balancer |