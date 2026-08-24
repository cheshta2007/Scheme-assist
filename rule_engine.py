import json
from typing import List, Dict, Any, Union
from models import UserProfile


def load_schemes(path: str = "schemes.json") -> List[Dict[str, Any]]:
    """Loads schemes from a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def matches_list(value: str, allowed_list: Union[List[str], str, None]) -> bool:
    """
    Checks if a given value matches allowed_list.
    - Case-insensitive comparison.
    - Returns True if allowed_list is None, empty, or contains "All" / "all".
    """
    if allowed_list is None:
        return True
    if isinstance(allowed_list, str):
        allowed_list = [allowed_list]
    if not allowed_list:
        return True

    val_lower = str(value).strip().lower()
    allowed_lower = [str(item).strip().lower() for item in allowed_list]

    if "all" in allowed_lower:
        return True

    return val_lower in allowed_lower


def check_scheme_eligibility(
    user: Union[UserProfile, Dict[str, Any]], 
    scheme: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Checks a user's eligibility against a single scheme based on deterministic rules:
    - Age range (min_age, max_age)
    - Income limit (max_income)
    - State (states)
    - Occupation (occupations)
    - Category (categories)
    - Gender (genders)
    
    Returns dict with scheme name, eligible (bool), failed_on list, and scheme details.
    """
    if isinstance(user, UserProfile):
        u_age = user.age
        u_income = user.income
        u_state = user.state
        u_occupation = user.occupation
        u_category = user.category
        u_gender = user.gender
    else:
        u_age = user.get("age", 0)
        u_income = user.get("income", 0.0)
        u_state = user.get("state", "")
        u_occupation = user.get("occupation", "")
        u_category = user.get("category", "")
        u_gender = user.get("gender", "")

    failed_on: List[str] = []

    # Age criteria check
    min_age = scheme.get("min_age")
    max_age = scheme.get("max_age")
    if min_age is not None and u_age < min_age:
        failed_on.append("age")
    elif max_age is not None and u_age > max_age:
        failed_on.append("age")

    # Income criteria check
    max_income = scheme.get("max_income")
    if max_income is not None and u_income > max_income:
        failed_on.append("income")

    # State criteria check
    states = scheme.get("states", scheme.get("state"))
    if states is not None and not matches_list(u_state, states):
        failed_on.append("state")

    # Occupation criteria check
    occupations = scheme.get("occupations", scheme.get("occupation"))
    if occupations is not None and not matches_list(u_occupation, occupations):
        failed_on.append("occupation")

    # Category criteria check
    categories = scheme.get("categories", scheme.get("category"))
    if categories is not None and not matches_list(u_category, categories):
        failed_on.append("category")

    # Gender criteria check (if present in scheme)
    genders = scheme.get("genders", scheme.get("gender"))
    if genders is not None and not matches_list(u_gender, genders):
        failed_on.append("gender")

    eligible = (len(failed_on) == 0)
    scheme_name = scheme.get("scheme", scheme.get("name", "Unknown Scheme"))

    return {
        "scheme": scheme_name,
        "eligible": eligible,
        "failed_on": failed_on,
        "required_documents": scheme.get("required_documents", []),
        "official_source": scheme.get("official_source", ""),
        "application_link": scheme.get("application_link", "")
    }


def run_rule_engine(
    user: Union[UserProfile, Dict[str, Any]], 
    schemes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Runs check_scheme_eligibility across all schemes for a user profile."""
    return [check_scheme_eligibility(user, s) for s in schemes]
