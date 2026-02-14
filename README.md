# ChartSense AI 🏥🤖

**AI-Powered Clinical Decision Support Platform for Thai Hospitals**

ระบบสนับสนุนการตัดสินใจทางคลินิกด้วย AI สำหรับโรงพยาบาลในประเทศไทย

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docs.docker.com/compose/)

---

## 🌟 Features

### 1. AI Clinical Decision Support (CDS)
- **Pre-Diagnosis**: Ranked differential diagnoses with confidence scores using GraphRAG knowledge graph
- **Order Suggestion**: CPG-compliant lab/imaging/medication orders personalized per patient
- **Admission Decision**: Risk scoring using CURB-65, qSOFA with admission recommendations

### 2. Chart Completeness Engine
- Real-time chart completeness score (0-100%)
- 20+ configurable rules across 4 dimensions (Diagnosis, Procedure, Consistency, Documentation)
- Gap identification with suggested ICD-10 codes

### 3. AI Code Suggestion
- ICD-10 code recommendations with evidence trails
- RW (Relative Weight) impact calculation
- Revenue impact analysis in THB (Before/After comparison)
- Accept/Reject workflow for medical coders

### Disease Groups (MVP)
- 🫁 **Community-Acquired Pneumonia (CAP)**
- 💉 **DM Complications** (Hyperglycemia, DKA, AKI, Neuropathy)
- ❤️ **Heart Failure** (HFrEF, Acute Decompensated HF)

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph Frontend
        A[Next.js 14<br/>React + TypeScript<br/>Tailwind + shadcn/ui]
    end

    subgraph Backend
        B[FastAPI<br/>Python 3.12]
        C[GraphRAG Service<br/>Knowledge Graph]
        D[Rule Engine<br/>Chart Completeness]
        E[DRG/RW Calculator<br/>Code Suggestion]
        F[Thai NLP Service<br/>Keyword Matching]
    end

    subgraph Data
        G[(PostgreSQL 16<br/>Patient Data)]
        H[(Neo4j 5<br/>Knowledge Graph)]
        I[(Redis 7<br/>Cache)]
    end

    subgraph Infra
        J[Nginx<br/>Reverse Proxy]
    end

    J --> A
    J --> B
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    C --> H
    B --> I
```

---

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

# Run
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 API Documentation

### Clinical Decision Support
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cds/pre-diagnosis` | Generate differential diagnoses |
| POST | `/api/v1/cds/order-suggestion` | CPG-compliant order suggestions |
| POST | `/api/v1/cds/admission-decision` | Risk scoring & admission recommendation |

### Chart Completeness
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/chart-completeness/{encounter_id}` | Get chart completeness score |
| POST | `/api/v1/chart-completeness/evaluate` | Evaluate chart completeness |

### Code Suggestion
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/code-suggestion/{encounter_id}` | Get AI code suggestions |
| POST | `/api/v1/code-suggestion/{encounter_id}/accept` | Accept suggested codes |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/rules` | List chart completeness rules |
| POST | `/api/v1/admin/rules` | Create new rule |
| PUT | `/api/v1/admin/rules/{rule_id}` | Update rule |
| GET | `/api/v1/admin/templates` | List CPG templates |
| GET | `/api/v1/admin/patients` | List patients |
| GET | `/api/v1/admin/encounters/{encounter_id}` | Get encounter details |

Full interactive API docs: `http://localhost:8000/docs`

---

## 🗂️ Project Structure

```
chartsense-ai/
├── frontend/                   # Next.js 14 App
│   ├── src/
│   │   ├── app/               # App Router pages
│   │   │   ├── page.tsx       # Dashboard
│   │   │   ├── patients/[id]/ # Patient detail view
│   │   │   ├── admin/         # Admin panel
│   │   │   └── analytics/     # Analytics dashboard
│   │   ├── components/        # React components
│   │   │   ├── ui/           # shadcn/ui components
│   │   │   └── layout/       # Layout components
│   │   ├── lib/              # Utilities
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── backend/                    # FastAPI App
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   ├── cds.py        # CDS endpoints
│   │   │   ├── chart.py      # Chart completeness
│   │   │   ├── coding.py     # Code suggestion
│   │   │   └── admin.py      # Admin endpoints
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── graphrag.py   # Knowledge graph traversal
│   │   │   ├── rules.py      # Chart completeness rules
│   │   │   ├── drg.py        # DRG/RW calculator
│   │   │   └── nlp.py        # Thai NLP (keyword-based)
│   │   ├── core/             # Configuration
│   │   └── db/               # Database & seeding
│   ├── requirements.txt
│   └── Dockerfile
├── nginx/                      # Nginx config
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

---

## 🎯 Key Screens

1. **Dashboard** — Patient overview with chart scores, pending code reviews, disease group summary
2. **Patient View** — Integrated CDS with 4 tabs:
   - 🩺 Differential Diagnosis + Admission Decision
   - 📋 CPG-Compliant Order Suggestions
   - 📊 Chart Completeness Score with Gap Analysis
   - 🔢 Code Suggestions with RW Impact
3. **Admin Panel** — Rule editor, CPG template management
4. **Analytics** — Weekly trends, revenue impact, disease group statistics

---

## 🏥 Demo Data

The system seeds automatically with:
- **12 patients** with Thai names and realistic clinical histories
- **11 encounters** across CAP, DM, and HF disease groups
- **20 chart completeness rules** across 4 categories
- **3 CPG templates** (Thai CPG 2023)
- Lab results, vitals, progress notes (in Thai)
- Pre-configured knowledge graph for all 3 disease groups

---

## 🔧 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://chartsense:...@postgres:5432/chartsense_db` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `NEO4J_URI` | Neo4j Bolt URI | `bolt://neo4j:7687` |
| `NEO4J_USER` | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `chartsense_neo4j_2026` |
| `DEMO_MODE` | Enable demo mode | `true` |
| `NEXT_PUBLIC_API_URL` | Backend API URL for frontend | `http://localhost:8000` |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Anirach Mingkhwan** — Medical Informatics Researcher

---

## ⚠️ Disclaimer

This is an **MVP/Demo** application for educational and research purposes. It should **NOT** be used for actual clinical decision-making without proper validation, regulatory approval, and clinical oversight.

The AI components use simplified rule-based logic (GraphRAG knowledge graph traversal + keyword matching) rather than full machine learning models. All clinical data is simulated.
