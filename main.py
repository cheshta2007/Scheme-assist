import os
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import UserProfile, SchemeResult
from rule_engine import load_schemes, run_rule_engine

app = FastAPI(
    title="AI-Powered Scheme Assistance Agent",
    description="Phase 2 Eligibility Rule Engine Backend API",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCHEMES_FILE_PATH = os.path.join(os.path.dirname(__file__), "schemes.json")


@app.get("/")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Scheme Assistant Backend API is running"
    }


@app.post("/check-eligibility")
def check_eligibility(user: UserProfile) -> Dict[str, Any]:
    """Accepts UserProfile JSON body, evaluates rules against loaded schemes, returns eligibility results."""
    schemes = load_schemes(SCHEMES_FILE_PATH)
    results = [SchemeResult(**r) for r in run_rule_engine(user, schemes)]
    eligible_count = sum(1 for r in results if r.eligible)
    return {
        "total_schemes_checked": len(schemes),
        "eligible_count": eligible_count,
        "results": results
    }


@app.get("/schemes")
def get_schemes() -> List[Dict[str, Any]]:
    """Returns the full raw list of schemes."""
    return load_schemes(SCHEMES_FILE_PATH)
