import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine, Base
from routers import auth_router, project_router, cpq_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE master_rates ADD COLUMN IF NOT EXISTS remarks VARCHAR;"))
        conn.execute(text("ALTER TABLE equipment_categories ADD COLUMN IF NOT EXISTS domain VARCHAR DEFAULT 'Mechanical';"))
        conn.execute(text("ALTER TABLE estimate_line_items ADD COLUMN IF NOT EXISTS domain VARCHAR DEFAULT 'Mechanical';"))
        conn.commit()
except Exception:
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE master_rates ADD COLUMN remarks VARCHAR;"))
            conn.commit()
    except Exception:
        pass
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE equipment_categories ADD COLUMN domain VARCHAR DEFAULT 'Mechanical';"))
            conn.commit()
    except Exception:
        pass
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE estimate_line_items ADD COLUMN domain VARCHAR DEFAULT 'Mechanical';"))
            conn.commit()
    except Exception:
        pass

app = FastAPI(
    title="Enterprise CPQ Cost Estimation & Benchmarking API",
    description="Specialized high-confidentiality engineering estimation backend with dynamic JSONB specification filtering and quotation escalation.",
    version="1.0.0"
)

# Configure CORS for React Vite frontend and local development
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wire up routers
app.include_router(auth_router.router)
app.include_router(project_router.router)
app.include_router(cpq_router.router)

@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "Enterprise CPQ Estimator Core API",
        "security_policy": "STRICT CONFIDENTIALITY ENFORCED"
    }
