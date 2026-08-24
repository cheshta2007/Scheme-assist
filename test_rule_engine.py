from models import UserProfile
from rule_engine import check_scheme_eligibility, matches_list


def test_user_qualifies():
    """Test 1: User who meets all scheme criteria passes eligibility check."""
    user = UserProfile(
        age=30,
        income=150000.0,
        state="Maharashtra",
        occupation="Farmer",
        category="General",
        gender="Male"
    )
    scheme = {
        "scheme": "PM-Kisan Samman Nidhi",
        "min_age": 18,
        "max_age": 70,
        "max_income": 200000.0,
        "states": ["Maharashtra", "Punjab"],
        "occupations": ["Farmer"],
        "categories": ["All"],
        "genders": ["All"],
        "required_documents": ["Aadhaar Card", "Land Record"],
        "official_source": "https://pmkisan.gov.in",
        "application_link": "https://pmkisan.gov.in/registration"
    }
    result = check_scheme_eligibility(user, scheme)
    assert result["eligible"] is True, f"Expected eligible=True, got {result}"
    assert result["failed_on"] == [], f"Expected failed_on=[], got {result['failed_on']}"
    assert result["scheme"] == "PM-Kisan Samman Nidhi"


def test_income_too_high():
    """Test 2: User fails eligibility due to income exceeding maximum limit."""
    user = UserProfile(
        age=25,
        income=350000.0,  # exceeds max_income of 250000
        state="Delhi",
        occupation="Student",
        category="OBC",
        gender="Female"
    )
    scheme = {
        "scheme": "Post Matric Scholarship",
        "min_age": 15,
        "max_age": 30,
        "max_income": 250000.0,
        "states": ["Delhi"],
        "occupations": ["Student"],
        "categories": ["OBC", "SC", "ST"],
        "genders": ["All"],
        "required_documents": ["Income Certificate", "Student ID"],
        "official_source": "https://scholarships.gov.in",
        "application_link": "https://scholarships.gov.in/apply"
    }
    result = check_scheme_eligibility(user, scheme)
    assert result["eligible"] is False, f"Expected eligible=False, got {result}"
    assert "income" in result["failed_on"], f"Expected 'income' in failed_on, got {result['failed_on']}"


def test_age_out_of_range():
    """Test 3: User fails eligibility due to age being out of range."""
    user = UserProfile(
        age=75,  # exceeds max_age of 60
        income=50000.0,
        state="Karnataka",
        occupation="Senior Citizen",
        category="General",
        gender="Male"
    )
    scheme = {
        "scheme": "Yuva Skill Training Scheme",
        "min_age": 18,
        "max_age": 60,
        "max_income": 100000.0,
        "states": ["Karnataka"],
        "occupations": ["All"],
        "categories": ["All"],
        "genders": ["All"],
        "required_documents": ["Age Proof"],
        "official_source": "https://skill.gov.in",
        "application_link": "https://skill.gov.in/apply"
    }
    result = check_scheme_eligibility(user, scheme)
    assert result["eligible"] is False, f"Expected eligible=False, got {result}"
    assert "age" in result["failed_on"], f"Expected 'age' in failed_on, got {result['failed_on']}"


def test_state_wildcard_all():
    """Test 4: User qualifies via the 'All' wildcard for state."""
    user = UserProfile(
        age=40,
        income=120000.0,
        state="Kerala",  # Any state should match 'All'
        occupation="Artisan",
        category="SC",
        gender="Female"
    )
    scheme = {
        "scheme": "National Artisan Welfare Scheme",
        "min_age": 18,
        "max_age": 65,
        "max_income": 200000.0,
        "states": ["All"],  # Wildcard
        "occupations": ["Artisan", "Craftsman"],
        "categories": ["All"],
        "genders": ["All"],
        "required_documents": ["Artisan Identity Card"],
        "official_source": "https://handicrafts.gov.in",
        "application_link": "https://handicrafts.gov.in/apply"
    }
    result = check_scheme_eligibility(user, scheme)
    assert result["eligible"] is True, f"Expected eligible=True with 'All' state wildcard, got {result}"
    assert result["failed_on"] == [], f"Expected no failed criteria, got {result['failed_on']}"


def test_wrong_occupation():
    """Test 5: User fails eligibility due to non-matching occupation."""
    user = UserProfile(
        age=35,
        income=80000.0,
        state="Gujarat",
        occupation="Software Engineer",  # Scheme is only for Farmers and Laborers
        category="General",
        gender="Male"
    )
    scheme = {
        "scheme": "Krishi Kalyan Yojana",
        "min_age": 18,
        "max_age": 65,
        "max_income": 150000.0,
        "states": ["Gujarat"],
        "occupations": ["Farmer", "Laborer"],
        "categories": ["All"],
        "genders": ["All"],
        "required_documents": ["Farmer ID"],
        "official_source": "https://agri.gujarat.gov.in",
        "application_link": "https://agri.gujarat.gov.in/apply"
    }
    result = check_scheme_eligibility(user, scheme)
    assert result["eligible"] is False, f"Expected eligible=False, got {result}"
    assert "occupation" in result["failed_on"], f"Expected 'occupation' in failed_on, got {result['failed_on']}"


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    
    test_user_qualifies()
    test_income_too_high()
    test_age_out_of_range()
    test_state_wildcard_all()
    test_wrong_occupation()
    print("All tests passed ✅")

