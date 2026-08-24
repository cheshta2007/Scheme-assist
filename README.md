# AI-Powered Scheme Assistance Agent — Backend (Phase 2)

A FastAPI backend for the hackathon prototype **AI-Powered Scheme Assistance Agent**. Phase 2 implements a deterministic, pure rule-based eligibility engine that evaluates a user's profile against government welfare schemes.

> **Note:** The rule engine is intentionally pure and deterministic (no LLM/AI involved in decision making). An LLM will only be used in later phases to explain results in natural language without overriding eligibility logic.

---

## 📁 Project Structure

```
scheme-assistant-backend/
├── main.py              # FastAPI app + API routes
├── rule_engine.py        # Core eligibility matching logic
├── models.py              # Pydantic request/response models
├── schemes.json           # Verified scheme database
├── test_rule_engine.py     # Sanity tests (5 requirement test cases)
├── requirements.txt       # Dependencies
└── README.md              # Project documentation
```

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

```bash
pip install -r requirements.txt
```

---

## 🧪 Running Tests

Run the standalone sanity test suite:

```bash
python test_rule_engine.py
```

Expected output:
```
All tests passed ✅
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
- **POST `/check-eligibility`**: Submit a user profile and get scheme eligibility results.
- **GET `/schemes`**: Fetch the list of loaded schemes.
- **Swagger Docs**: Available at `http://localhost:8000/docs`.
