from unittest.mock import patch, MagicMock
from llm_explainer import explain_result


def test_explain_result_eligible():
    """Test 1: explain_result returns non-empty explanation for eligible user (mocked API call)."""
    user_profile = {
        "age": 30,
        "income": 150000.0,
        "state": "Maharashtra",
        "occupation": "Farmer",
        "category": "General",
        "gender": "Male"
    }
    result = {
        "scheme": "PM-Kisan Samman Nidhi",
        "eligible": True,
        "failed_on": [],
        "required_documents": ["Aadhaar Card"],
        "official_source": "https://pmkisan.gov.in",
        "application_link": "https://pmkisan.gov.in/registration"
    }

    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.text = "You qualify for PM-Kisan Samman Nidhi because you meet all income and occupation criteria."
    mock_response.content = [mock_content]

    with patch("os.getenv", return_value="fake-api-key"), \
         patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = mock_response

        explanation = explain_result(user_profile, result)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert explanation == "You qualify for PM-Kisan Samman Nidhi because you meet all income and occupation criteria."


def test_explain_result_ineligible():
    """Test 2: explain_result returns non-empty explanation for ineligible user with failed_on (mocked API call)."""
    user_profile = {
        "age": 25,
        "income": 350000.0,
        "state": "Delhi",
        "occupation": "Student",
        "category": "OBC",
        "gender": "Female"
    }
    result = {
        "scheme": "Post Matric Scholarship",
        "eligible": False,
        "failed_on": ["income"],
        "required_documents": ["Student ID"],
        "official_source": "https://scholarships.gov.in",
        "application_link": "https://scholarships.gov.in/apply"
    }

    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.text = "You do not meet the income criteria for Post Matric Scholarship as your income exceeds the limit."
    mock_response.content = [mock_content]

    with patch("os.getenv", return_value="fake-api-key"), \
         patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.return_value = mock_response

        explanation = explain_result(user_profile, result)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "income" in explanation or "Post Matric Scholarship" in explanation


def test_explain_result_fallback_on_exception():
    """Test 3: Fallback template path works correctly when the API call raises an exception."""
    user_profile = {
        "age": 40,
        "income": 500000.0,
        "state": "Kerala",
        "occupation": "Teacher",
        "category": "General",
        "gender": "Female"
    }
    result = {
        "scheme": "Low Income Housing Scheme",
        "eligible": False,
        "failed_on": ["income", "occupation"],
        "required_documents": ["Income Certificate"],
        "official_source": "https://housing.gov.in",
        "application_link": "https://housing.gov.in/apply"
    }

    with patch("os.getenv", return_value="invalid-key"), \
         patch("anthropic.Anthropic") as MockAnthropic:
        mock_client = MockAnthropic.return_value
        mock_client.messages.create.side_effect = Exception("API connection error")

        explanation = explain_result(user_profile, result)
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Low Income Housing Scheme" in explanation
        assert "income" in explanation and "occupation" in explanation


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    
    test_explain_result_eligible()
    test_explain_result_ineligible()
    test_explain_result_fallback_on_exception()
    print("All LLM explainer tests passed ✅")
