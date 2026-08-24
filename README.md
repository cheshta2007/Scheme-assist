# AI-Powered Scheme Assistance Agent — Backend (Phase 4)

A FastAPI backend for the hackathon prototype **AI-Powered Scheme Assistance Agent**. Phase 4 introduces an **LLM Explanation Layer** on top of the Phase 2 pure rule engine to provide friendly, natural-language explanations for scheme eligibility results.

> 🔒 **Core Architecture Principle — Rules Decide, AI Explains:**
> The rule engine is pure and deterministic. Eligibility decisions (`eligible: True/False` and `failed_on`) are calculated strictly by `rule_engine.py`. The LLM's **ONLY** role is to explain an eligibility decision that has already been decided — it never evaluates, overrides, or alters eligibility logic. This separation is enforced by never passing raw eligibility rules to the LLM, only the final decision and failed criteria.

---

## 📁 Project Structure

```
scheme-assistant-backend/
├── main.py                    # FastAPI app + API routes (/check-eligibility & /check-eligibility-with-explanation)
├── rule_engine.py             # Core deterministic eligibility matching logic
├── llm_explainer.py           # LLM explanation generator using Anthropic Claude API with fallback
├── models.py                  # Pydantic request/response models (UserProfile, SchemeResult)
├── schemes.json               # Verified scheme database
├── test_rule_engine.py        # Rule engine test suite
├── test_llm_explainer.py      # LLM explainer unit test suite (mocked API calls)
├── requirements.txt           # Project dependencies (fastapi, uvicorn, pydantic, anthropic, python-dotenv)
├── .env                       # Environment variables (API keys)
└── README.md                  # Project documentation
```

---

## 🔑 Environment Setup & API Key

1. Generate an Anthropic API Key from [console.anthropic.com](https://console.anthropic.com/).
2. Create or edit the `.env` file in the project root directory:

```env
ANTHROPIC_API_KEY=your-actual-api-key-here
```

> **Note:** The `.env` file is excluded from Git via `.gitignore` to keep credentials secure.

---

## 🚀 Setup & Installation

### 1. Create and Activate Virtual Environment

```bash
cd scheme-assistant-backend
python -m venv venv
```

- **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 2. Install Dependencies

Install required Python packages (including `anthropic` and `python-dotenv`):

```bash
pip install -r requirements.txt
```

---

## 🧪 Running Tests

### 1. Rule Engine Tests (Phase 2)
```bash
python test_rule_engine.py
```

### 2. LLM Explainer Tests (Phase 4 - Mocked API)
```bash
python test_llm_explainer.py
```

Expected output:
```
All tests passed ✅
All LLM explainer tests passed ✅
```

---

## 🌐 Running the FastAPI Server

Start the Uvicorn server:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

---

## 🔗 API Endpoints

- **GET `/`**: Health check.
- **POST `/check-eligibility`**: Returns raw eligibility results without AI explanations.
- **POST `/check-eligibility-with-explanation`**: Returns eligibility results enriched with natural-language LLM explanations.
- **GET `/schemes`**: Fetch the list of loaded schemes.
- **Swagger Docs**: Available at `http://localhost:8000/docs`.

---

## 💡 Example Request & Response (`/check-eligibility-with-explanation`)

### Curl Request

```bash
curl -X POST "http://127.0.0.1:8000/check-eligibility-with-explanation" \
     -H "Content-Type: application/json" \
     -d '{
           "age": 30,
           "income": 150000,
           "state": "Maharashtra",
           "occupation": "Farmer",
           "category": "General",
           "gender": "Male"
         }'
```

### Example Response

```json
{
  "total_schemes_checked": 5,
  "eligible_count": 2,
  "results": [
    {
      "scheme": "PM-Kisan Samman Nidhi",
      "eligible": true,
      "failed_on": [],
      "required_documents": ["Aadhaar Card", "Land Ownership Certificate", "Bank Passbook"],
      "official_source": "https://pmkisan.gov.in",
      "application_link": "https://pmkisan.gov.in/registration",
      "explanation": "You qualify for PM-Kisan Samman Nidhi because you are a farmer residing in Maharashtra with an annual income within the eligible threshold."
    },
    {
      "scheme": "Post Matric Scholarship for SC/ST Students",
      "eligible": false,
      "failed_on": ["occupation", "category"],
      "required_documents": ["Caste Certificate", "Income Certificate", "Marksheet"],
      "official_source": "https://scholarships.gov.in",
      "application_link": "https://scholarships.gov.in/apply",
      "explanation": "You are currently not eligible for Post Matric Scholarship for SC/ST Students because the scheme requires student status and specific social categories."
    }
  ]
}
```
