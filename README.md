# ASPRAMS — Agent-Based Software Project Risk Assessment and Mitigation System

> A full-stack AI-powered system that simulates negotiation between an **Estimation Agent** and a **Risk Analysis Agent** to arrive at a realistic software project effort estimate — powered by **Google Gemini**.

---

## 📐 Architecture

```
asprams/
├── backend/                  # FastAPI + multi-agent system
│   ├── main.py               # App entry point
│   ├── agents/
│   │   ├── estimation_agent.py   # Optimistic estimate via Gemini
│   │   └── risk_agent.py         # Risk-adjusted counter via Gemini
│   ├── core/
│   │   ├── negotiation_engine.py # Iterative negotiation loop
│   │   └── schemas.py            # Pydantic request/response models
│   ├── config/
│   │   └── settings.py           # Environment variable management
│   ├── integrations/
│   │   └── jira_service.py       # Jira REST API integration
│   ├── routes/
│   │   ├── analyze.py            # POST /analyze
│   │   └── health.py             # GET /health
│   ├── tests/
│   │   └── test_api.py           # Integration tests
│   └── requirements.txt
├── frontend/                 # Vite + React + Tailwind CSS
│   └── src/
│       ├── components/           # Form, Timeline, ResultCard
│       ├── pages/                # Home dashboard
│       └── services/             # Axios API client
├── .github/workflows/ci.yml  # GitHub Actions pipeline
├── .env.example              # Environment variable template
├── Dockerfile                # Multi-stage production build
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- A Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey))

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd asprams

# Copy environment template
cp .env.example .env
# Edit .env with your actual keys
```

### 2. Start the Backend

```bash
cd backend

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py
# OR: uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at **http://localhost:5173**

---

## ⚙️ Configuration

Create a `.env` file in the `asprams/` root based on `.env.example`:

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key |
| `GEMINI_MODEL` | No | Defaults to `gemini-1.5-flash` |
| `JIRA_EMAIL` | Optional | Atlassian account email |
| `JIRA_API_TOKEN` | Optional | Jira API token |
| `JIRA_DOMAIN` | Optional | e.g. `yourcompany.atlassian.net` |
| `JIRA_PROJECT_KEY` | Optional | e.g. `PROJ` |
| `MAX_NEGOTIATION_ROUNDS` | No | Defaults to `5` |
| `VITE_API_URL` | No | Backend URL, defaults to `http://localhost:8000` |

---

## 🤖 How the Multi-Agent System Works

```
  User Input
      │
      ▼
  Estimation Agent (Gemini)
  ──────────────────────────
  "Optimistically, this project
   needs ~24 person-weeks."
      │
      ▼
  Risk Analysis Agent (Gemini)
  ──────────────────────────────
  "I see 3 key risks. I COUNTER
   with 31 person-weeks."
      │
      ▼
  Estimation Agent revises...
      │
      ▼
  [Loop up to MAX_NEGOTIATION_ROUNDS]
      │
      ▼
  Risk Agent ACCEPTs ──► Final Effort Returned
```

### Agent Roles

| Agent | Persona | Strategy |
|---|---|---|
| **Estimation Agent** | Optimistic planner | Minimizes effort, assumes smooth execution |
| **Risk Analysis Agent** | Skeptical reviewer | Identifies risks, applies buffers |

---

## 🔗 API Reference

### `POST /analyze`

**Request:**
```json
{
  "description": "Build a real-time inventory management system",
  "team_size": 5,
  "duration": 12,
  "complexity": "medium"
}
```

**Response:**
```json
{
  "rounds": [
    {
      "round_number": 1,
      "estimation_agent": { "effort": 24.5, "decision": "COUNTER", "reason": "..." },
      "risk_agent": { "effort": 31.0, "decision": "COUNTER", "reason": "..." }
    }
  ],
  "final_effort": 28.5,
  "converged": true,
  "jira_issue_key": "PROJ-42"
}
```

### `GET /health`

```json
{ "status": "ok", "service": "ASPRAMS API", "timestamp": "2026-01-01T00:00:00Z" }
```

---

## 🏗️ Docker (Production)

```bash
# From asprams/ directory
docker build -t asprams .

docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e JIRA_EMAIL=your@email.com \
  -e JIRA_API_TOKEN=your_token \
  -e JIRA_DOMAIN=yourco.atlassian.net \
  -e JIRA_PROJECT_KEY=PROJ \
  asprams
```

---

## 🛠️ CI/CD Pipeline

The `.github/workflows/ci.yml` pipeline runs on every push to `main`:

1. **Setup** — Python 3.11 + Node.js 20
2. **Backend** — Install deps → lint with flake8 → run API integration tests
3. **Frontend** — Install deps → `npm run build` (Vite)
4. **All Clear** — Pipeline reports success

Add your secrets to GitHub: `Settings → Secrets → Actions`:
- `GEMINI_API_KEY`
- `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_DOMAIN`, `JIRA_PROJECT_KEY`

---

## 📋 Jira Integration

When Jira credentials are configured, ASPRAMS automatically creates a **Jira Story** after each simulation containing:
- Project description, team size, duration, complexity
- Final agreed effort estimate
- Risk agent reasoning
- Simulation convergence status

Issue labels: `asprams`, `risk-assessment`, `automated`

---

## 🧪 Running Tests

```bash
cd backend

# Start server first (in another terminal)
uvicorn main:app --reload

# Run tests
pytest tests/ -v
```

---

## 📄 License

MIT License — free to use and modify.
