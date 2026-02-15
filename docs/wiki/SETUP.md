# SETUP.md — Development and Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Run with Docker Compose
```bash
# Clone the repository
git clone https://github.com/Anirach/chartsense-ai.git
cd chartsense-ai

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474
```

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://chartsense:chartsense_secret_2026@localhost:5432/chartsense_db
export REDIS_URL=redis://localhost:6379/0
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=chartsense_neo4j_2026
export DEMO_MODE="true"

# Run
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🐳 Docker Deployment

### Production Build
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `NEO4J_URI`: Neo4j Bolt URI
- `NEO4J_USER`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password
- `DEMO_MODE`: Enable demo mode (true/false)
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend

## 🔧 Troubleshooting

### Common Issues
1. **Port Conflicts**: Ensure ports 3000, 8000, 5432, 6379, and 7474 are free.
2. **Database Initialization**: Run `docker-compose down -v` and restart if databases fail to initialize.
3. **Frontend Not Connecting**: Verify `NEXT_PUBLIC_API_URL` matches the backend URL.

### Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```