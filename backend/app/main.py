from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import cds, chart, coding, admin
from app.core.config import settings
from app.db.database import engine, Base
from app.db.seed import seed_database

app = FastAPI(
    title="ChartSense AI",
    description="AI-Powered Clinical Decision Support Platform for Thai Hospitals",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cds.router, prefix="/api/v1/cds", tags=["Clinical Decision Support"])
app.include_router(chart.router, prefix="/api/v1/chart-completeness", tags=["Chart Completeness"])
app.include_router(coding.router, prefix="/api/v1/code-suggestion", tags=["Code Suggestion"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


@app.on_event("startup")
async def startup() -> None:
    Base.metadata.create_all(bind=engine)
    seed_database()


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ChartSense AI"}
