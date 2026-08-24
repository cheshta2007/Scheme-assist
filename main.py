import os
from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import UserProfile, SchemeResult
from rule_engine import load_schemes, run_rule_engine
from llm_explainer import explain_result

app = FastAPI(
    title="AI-Powered Scheme Assistance Agent",
    description="Phase 4 Eligibility Rule Engine & LLM Explanation Backend API",
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


@app.post("/check-eligibility-with-explanation")
def check_eligibility_with_explanation(user: UserProfile) -> Dict[str, Any]:
    """Accepts UserProfile JSON body, evaluates rules against loaded schemes, generates explanations, returns results."""
    schemes = load_schemes(SCHEMES_FILE_PATH)
    raw_results = run_rule_engine(user, schemes)
    user_dict = user.dict() if hasattr(user, "dict") else user.model_dump()

    results = []
    for r in raw_results:
        res_dict = dict(r)
        res_dict["explanation"] = explain_result(user_dict, res_dict)
        results.append(SchemeResult(**res_dict))

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

